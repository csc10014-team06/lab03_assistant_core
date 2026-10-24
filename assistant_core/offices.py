"""offices.py — office lookup from message text.

Stub module: implementation owned by truyen_lp.
"""
from __future__ import annotations

from assistant_core.data_loader import Office


def find_office(text: str, offices: dict[str, Office]) -> Office | None:
    """Return the first Office whose lower-cased name appears in *text*.

    Returns None if no match is found.
    """
    text_lower = text.lower()
    for key, office in offices.items():
        if key in text_lower:
            return office
    return None
