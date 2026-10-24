"""Tuition questions: detect them, parse credits/retakes, compute the fee.

Extracted from the fee branch of ``handle()`` in the monolith. Every function
here is pure: no globals, no I/O, and all rates come from :class:`Settings`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from assistant_core.config import Settings

# Whole-word match, so "coffee" or "feedback" is not a fee question.
_FEE_KEYWORDS = re.compile(r"\b(?:fees?|tuition)\b", re.IGNORECASE)
# ASCII digits only: str.isdigit() also accepts "²", which int() rejects.
_NUMBER = re.compile(r"[0-9]+")
# Punctuation stripped from the ends of a word ("18," -> "18"). Signs are
# kept on purpose so "-5" is not read as 5 credits.
_EDGE_PUNCTUATION = ".,;:!?()[]\"'"


class TooManyCreditsError(ValueError):
    """Raised when the requested credits exceed ``Settings.max_credits``."""


@dataclass(frozen=True)
class FeeQuery:
    """Numbers found in a tuition question."""

    credits: int  # 0 means "not specified"
    retakes: int


def is_fee_question(text: str) -> bool:
    """Return True if *text* mentions fee, fees or tuition as a whole word."""
    return _FEE_KEYWORDS.search(text) is not None


def parse_fee_query(text: str) -> FeeQuery:
    """Extract the credit and retake counts from *text*.

    A number followed by a word starting with "retake" ("retake",
    "retakes") is the retake count; otherwise the first non-zero number is
    the credit count. ``credits`` is 0 when no credit count is found.
    """
    words = [w.strip(_EDGE_PUNCTUATION) for w in text.lower().replace("?", " ").split()]
    credits = 0
    retakes = 0
    for i, word in enumerate(words):
        if not _NUMBER.fullmatch(word):
            continue
        next_word = words[i + 1] if i + 1 < len(words) else ""
        if next_word.startswith("retake"):
            retakes = int(word)
        elif credits == 0:
            credits = int(word)
    return FeeQuery(credits=credits, retakes=retakes)


def compute_tuition(q: FeeQuery, s: Settings) -> int:
    """Return the tuition in VND for *q*, rounded down like the monolith.

    Retake credits cost ``s.retake_multiplier`` times the normal rate. The
    multiplier goes through :class:`Decimal` so e.g. 1.15 is not truncated
    to 1.1499999 by float arithmetic.

    Raises:
        TooManyCreditsError: if ``q.credits`` exceeds ``s.max_credits``
            (retakes are not counted, as in the monolith).
    """
    if q.credits > s.max_credits:
        raise TooManyCreditsError(
            f"{q.credits} credits exceeds the maximum of {s.max_credits}"
        )
    retake_rate = Decimal(str(s.retake_multiplier)) * s.credit_rate
    total = q.credits * s.credit_rate + q.retakes * retake_rate
    return int(total)
