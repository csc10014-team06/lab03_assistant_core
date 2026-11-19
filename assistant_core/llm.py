
"""LLM interfaces and offline/demo implementations."""

from __future__ import annotations

import json
import logging
import random
import re
import time
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

import httpx
from pydantic import BaseModel, Field, ValidationError

if TYPE_CHECKING:
    from assistant_core.rag.index import Hit


class LLMError(Exception):
    """Raised when an LLM implementation cannot complete a prompt."""


@runtime_checkable
class LLMClient(Protocol):
    """Common interface used by the assistant service."""

    def complete(self, prompt: str) -> str:
        """Return a completion or raise LLMError."""
        ...


class FakeLLM:
    """Deterministic, offline LLM substitute for tests."""

    def __init__(self, response: str = "fake response") -> None:
        self.response = response
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        """Record the prompt and return a configured response."""
        self.prompts.append(prompt)
        return self.response


class DemoLLM:
    """Offline demo implementation matching the monolith's reply format."""

    def __init__(
        self,
        *,
        rng: Callable[[], float] = random.random,
        sleep_fn: Callable[[float], object] = time.sleep,
        timeout_probability: float = 0.1,
        delay_seconds: float = 0.2,
        logger: logging.Logger | None = None,
    ) -> None:
        if not 0.0 <= timeout_probability <= 1.0:
            raise ValueError(
                "timeout_probability must be between 0 and 1"
            )
        if delay_seconds < 0:
            raise ValueError("delay_seconds must not be negative")

        self._rng = rng
        self._sleep = sleep_fn
        self._timeout_probability = timeout_probability
        self._delay_seconds = delay_seconds
        self._logger = logger or logging.getLogger(__name__)

    def complete(self, prompt: str) -> str:
        """Simulate a completion or raise LLMError on timeout."""
        self._logger.debug("LLM prompt: %.60s", prompt)
        self._sleep(self._delay_seconds)

        if self._rng() < self._timeout_probability:
            raise LLMError("LLM timeout")

        return "Here is what I found: " + prompt[-120:]


# ---------------------------------------------------------------------------
# Lab 6 — RAG drafts: the model writes an answer *from retrieved chunks* and
# must say which chunks it used. Our code, not the model, checks that claim.
# ---------------------------------------------------------------------------


class ProviderError(LLMError):
    """The draft provider failed or returned something we refuse to show a student."""


class Draft(BaseModel):
    """What a draft provider must return (as JSON)."""

    answer: str = ""
    source_ids: list[str] = Field(default_factory=list)
    abstain: bool = False


@runtime_checkable
class DraftProvider(Protocol):
    """A model that drafts a grounded answer. Returns the raw text; parse it with parse_draft()."""

    name: str

    def draft(self, question: str, hits: Sequence[Hit]) -> str: ...


PROMPT_TEMPLATE = """You are a study assistant. Answer ONLY from the handbook excerpts below.
Reply with JSON only: {{"answer": "...", "source_ids": ["<id>", ...], "abstain": false}}.
Cite the ids of the excerpts you used. If the excerpts do not answer the question, or the
question asks about another person, reply {{"answer": "", "source_ids": [], "abstain": true}}.

Excerpts:
{context}

Question: {question}
JSON:"""


def build_prompt(question: str, hits: Sequence[Hit]) -> str:
    context = "\n".join(f"[{h.chunk.id}] {h.chunk.title}: {h.chunk.text}" for h in hits)
    return PROMPT_TEMPLATE.format(context=context, question=question)


_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def parse_draft(raw: str, allowed_ids: set[str]) -> Draft:
    """Parse the provider's raw reply into a Draft and run the grounding check (A2).

    Raises ProviderError when the reply is not valid JSON of the expected shape, or when a
    non-abstaining answer cites nothing or cites a chunk that was not retrieved.
    """
    match = _JSON_OBJECT.search(raw or "")
    if match is None:
        raise ProviderError("provider reply contains no JSON object")
    try:
        draft = Draft.model_validate(json.loads(match.group(0)))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ProviderError(f"provider reply is not a valid draft: {exc}") from exc

    # A2 — grounding check: an answer must cite >= 1 source, and only sources we retrieved.
    if not draft.abstain and (not draft.source_ids or not set(draft.source_ids) <= allowed_ids):
        raise ProviderError("answer cites sources that were not retrieved")
    if not draft.abstain and not draft.answer.strip():
        raise ProviderError("answer is empty")
    return draft


class StubLLM:
    """Offline, deterministic draft provider: quotes the best chunk and cites it.

    It never abstains on its own — which is exactly why questions about *another person*
    (E19) still get answered on the llm (stub) path. A real model may do better.
    """

    name = "stub"

    def __init__(self) -> None:
        self.calls = 0

    def draft(self, question: str, hits: Sequence[Hit]) -> str:
        self.calls += 1
        if not hits:
            return json.dumps({"answer": "", "source_ids": [], "abstain": True})
        top = hits[0].chunk
        return json.dumps({"answer": top.text, "source_ids": [top.id], "abstain": False})


class OllamaLLM:
    """Draft provider backed by a local Ollama server (bonus T7). Needs ``ollama serve``."""

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        timeout_s: float = 60.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.model = model
        self.name = f"ollama:{model}"
        self._url = base_url.rstrip("/") + "/api/generate"
        self._client = client or httpx.Client(timeout=timeout_s)

    def draft(self, question: str, hits: Sequence[Hit]) -> str:
        payload = {
            "model": self.model,
            "prompt": build_prompt(question, hits),
            "format": "json",
            "stream": False,
            "options": {"temperature": 0},
        }
        try:
            resp = self._client.post(self._url, json=payload)
            resp.raise_for_status()
            return str(resp.json()["response"])
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise ProviderError(f"ollama request failed: {exc}") from exc


def make_draft_provider(provider: str, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
    """Build the provider named by ``ASSISTANT_LLM_PROVIDER`` / ``LLM_PROVIDER`` (stub | ollama)."""
    name = provider.strip().lower()
    if name == "stub":
        return StubLLM()
    if name == "ollama":
        return OllamaLLM(model=model, base_url=base_url)
    raise ValueError(f"unknown LLM provider {provider!r} (expected 'stub' or 'ollama')")
