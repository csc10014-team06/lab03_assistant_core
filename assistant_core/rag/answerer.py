"""answerer.py — answer a question from the knowledge base, or say "I don't know".

Lab 6. Two of the three answering paths live here:

* ``retrieval`` — search the KB and return the best chunk as the answer (no model).
* ``llm``       — search the KB, hand the top chunks to a draft provider (stub or Ollama),
                  and only show its answer if it passes the grounding check (A2).

Both paths share the abstain gate (A1): when no chunk scores at least ``min_score`` we stop
*before* calling any model and send the student to the Training Office.
"""
from __future__ import annotations

import logging

from assistant_core.llm import DraftProvider, ProviderError, parse_draft
from assistant_core.models import Intent, Response, Source
from assistant_core.rag.index import Hit, KBIndex, tokenize

log = logging.getLogger(__name__)

ESCALATE_MSG = (
    "Sorry, I could not find this in the student handbook. "
    "Please contact the Training Office (room I.101, Mon-Fri 07:30-16:30)."
)


class RagAnswerer:
    def __init__(
        self,
        index: KBIndex,
        provider: DraftProvider | None = None,
        *,
        min_score: float = 2.0,
        k: int = 3,
    ) -> None:
        self.index = index
        self.provider = provider
        self.min_score = min_score
        self.k = k

    def answer(self, question: str, *, use_llm: bool = True) -> Response:
        hits = self.index.search(question, k=self.k)

        # A1 — abstain before calling the model when nothing relevant enough was found.
        if not hits or hits[0].score < self.min_score:
            return Response(answer=ESCALATE_MSG, intent=Intent.UNKNOWN, path="abstain",
                            escalate=True, confidence=0.0)

        if not use_llm or self.provider is None:
            top = hits[0]
            return Response(
                answer=top.chunk.text,
                intent=Intent.RULE,
                sources=[_source(top)],
                path="retrieval",
                confidence=_confidence(question, top),
            )

        allowed = {h.chunk_id for h in hits}
        try:
            draft = parse_draft(self.provider.draft(question, hits), allowed)
        except ProviderError as exc:
            # A hallucinated citation (or a broken provider) is never shown to the student.
            log.warning("draft rejected: %s", exc)
            return Response(answer=ESCALATE_MSG, intent=Intent.UNKNOWN, path="abstain",
                            escalate=True, degraded=True, confidence=0.0)

        if draft.abstain:
            return Response(answer=ESCALATE_MSG, intent=Intent.UNKNOWN, path="abstain",
                            escalate=True, confidence=0.0)

        by_id = {h.chunk_id: h for h in hits}
        cited = [by_id[sid] for sid in dict.fromkeys(draft.source_ids)]
        return Response(
            answer=draft.answer.strip(),
            intent=Intent.RULE,
            sources=[_source(h) for h in cited],
            path="llm",
            confidence=_confidence(question, cited[0]),
        )


def _source(hit: Hit) -> Source:
    return Source(id=hit.chunk.id, title=hit.chunk.title)


def _confidence(question: str, hit: Hit) -> float:
    """Share of the (distinct, non-stopword) question words that the chunk contains."""
    terms = set(tokenize(question))
    return round(min(1.0, hit.score / len(terms)), 2) if terms else 0.0
