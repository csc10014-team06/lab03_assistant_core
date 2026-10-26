"""offices.py — Office lookup from user message text.

Owner: truyen_lp (Lab 3)

Extracted from lines 77–80 of monolith/assistant_monolith.py.
Pure function with no globals or side-effects, returning an immutable Office
dataclass rather than a raw row.
"""
from __future__ import annotations

from assistant_core.data_loader import Office


def find_office(text: str, offices: dict[str, Office]) -> Office | None:
    """Return the first Office whose lower-cased name appears in *text*.

    Matching is case-insensitive. Tie-breaking preserves the iteration
    order of the *offices* dictionary, identical to the monolith behaviour.

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
        if key in text_lower:
            return office
    return None
