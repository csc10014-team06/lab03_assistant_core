"""llm.py — LLM interface, FakeLLM, and DemoLLM.

Stub module: implementation owned by nhat_npm.
"""
from __future__ import annotations

import logging
import random
import time
from typing import Protocol

log = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM call fails (timeout, network error, etc.)."""


class LLMClient(Protocol):
    """Protocol that every LLM backend must satisfy."""

    def complete(self, prompt: str) -> str:
        """Return the model's completion for *prompt*."""
        ...


class FakeLLM:
    """Deterministic, offline LLM for use in tests.

    Never calls a network, never sleeps, never reads environment variables.
    """

    def complete(self, prompt: str) -> str:
        return "Here is what I found: " + prompt[-120:]


class DemoLLM:
    """Reproduces the monolith's behaviour with injectable RNG and timeout.

    Never logs the API key; prompts are logged at DEBUG level (truncated).
    """

    def __init__(
        self,
        model: str = "gpt-small",
        api_key: str | None = None,
        *,
        rng: random.Random | None = None,
        sleep_seconds: float = 0.2,
        failure_rate: float = 0.1,
    ) -> None:
        self._model = model
        self._api_key = api_key  # never logged
        self._rng = rng or random.Random()
        self._sleep = sleep_seconds
        self._failure_rate = failure_rate

    def complete(self, prompt: str) -> str:
        log.debug("LLM call model=%s prompt=%.60s…", self._model, prompt)
        time.sleep(self._sleep)
        if self._rng.random() < self._failure_rate:
            raise LLMError("LLM timeout")
        return "Here is what I found: " + prompt[-120:]
