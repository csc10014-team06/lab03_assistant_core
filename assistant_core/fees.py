"""fees.py — parse fee queries and compute tuition.

Stub module: implementation owned by dieu_sp.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from assistant_core.config import Settings


class TooManyCreditsError(ValueError):
    """Raised when the requested credit count exceeds the maximum allowed."""


@dataclass(frozen=True)
class FeeQuery:
    credits: int   # 0 means "not specified"
    retakes: int


def parse_fee_query(text: str) -> FeeQuery:
    """Extract credit count and retake count from *text*.

    Returns FeeQuery(credits=0, retakes=0) when no numbers are found.
    Uses word-boundary matching so 'coffee' does NOT trigger a fee question.
    """
    text_lower = text.lower()
    words = re.sub(r"[?]", " ", text_lower).split()
    credits = 0
    retakes = 0
    for i, word in enumerate(words):
        if word.isdigit():
            next_word = words[i + 1] if i + 1 < len(words) else ""
            if next_word.startswith("retake"):
                retakes = int(word)
            elif credits == 0:
                credits = int(word)
    return FeeQuery(credits=credits, retakes=retakes)


def compute_tuition(q: FeeQuery, s: Settings) -> int:
    """Compute total tuition in VND.

    Raises TooManyCreditsError when q.credits > s.max_credits.
    """
    if q.credits > s.max_credits:
        raise TooManyCreditsError(
            f"credits {q.credits} exceeds maximum {s.max_credits}"
        )
    total = q.credits * s.credit_rate + q.retakes * s.credit_rate * s.retake_multiplier
    return int(total)
