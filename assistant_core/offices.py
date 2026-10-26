"""offices.py — Office lookup from user message text.

Owner: truyen_lp (Lab 3)

Extracted from lines 77–80 of monolith/assistant_monolith.py.
Pure function with no globals or side-effects, returning an immutable Office
dataclass rather than a raw row.
Uses word-boundary matching to prevent substring false positives
(e.g., "librarian" matching "library").
"""
from __future__ import annotations

import re

from assistant_core.data_loader import Office


def find_office(text: str, offices: dict[str, Office]) -> Office | None:
    """Return the first Office whose lower-cased name appears in *text*.

    Matching is case-insensitive and uses whole-word boundaries to avoid
    substring false positives (team-plan.md §5 line 78 issue).
    Tie-breaking preserves the iteration order of the *offices* dictionary,
    identical to the monolith behaviour.

    Parameters
    ----------
    text:
        User message or inquiry string.
    offices:
        Mapping of lower-cased office names to Office dataclasses.

    Returns
    -------
    Office | None:
        The matched Office dataclass, or None if no office name appears in *text*.
    """
    text_lower = text.lower()
    for key, office in offices.items():
        pattern = rf"\b{re.escape(key)}\b"
        if re.search(pattern, text_lower):
            return office
    return None
