"""test_offices_all.py — Unit tests for offices.all_offices (Lab 4 H1).

Owner: truyen_lp

Covers:
- Sorting by office name in ascending alphabetical order.
- Exact match with homework expected ordering (IT Helpdesk, Library, ...).
- Empty offices dictionary handling.
- Single-item dictionary handling.
- Stability with scrambled dictionary insertion orders.
- Integrity of returned Office dataclass fields (name, room, hours).
"""
from __future__ import annotations

import pytest

from assistant_core.data_loader import Office
from assistant_core.offices import all_offices


@pytest.fixture
def sample_offices() -> dict[str, Office]:
    """Sample office mapping identical to data_loader contract."""
    return {
        "training office": Office(
            name="Training Office", room="I.101", hours="Mon-Fri 07:30-16:30"
        ),
        "student affairs": Office(
            name="Student Affairs", room="I.102", hours="Mon-Fri 08:00-16:00"
        ),
        "library": Office(
            name="Library", room="B.201", hours="Mon-Sat 07:00-20:00"
        ),
        "it helpdesk": Office(
            name="IT Helpdesk", room="E.005", hours="Mon-Fri 08:00-17:00"
        ),
    }


def test_all_offices_sorted_by_name(sample_offices: dict[str, Office]) -> None:
    """Offices must be returned sorted alphabetically by their name attribute."""
    result = all_offices(sample_offices)
    assert isinstance(result, list)
    names = [o.name for o in result]
    assert names == ["IT Helpdesk", "Library", "Student Affairs", "Training Office"]
    assert names == sorted(names)


def test_all_offices_empty() -> None:
    """Empty mapping should yield an empty list."""
    assert all_offices({}) == []


def test_all_offices_single_entry() -> None:
    """Single office in mapping returns a list with that single office."""
    office = Office(name="Library", room="B.201", hours="Mon-Sat 07:00-20:00")
    result = all_offices({"library": office})
    assert result == [office]


def test_all_offices_scrambled_order(sample_offices: dict[str, Office]) -> None:
    """Sorting must depend on office.name regardless of dict key or insertion order."""
    reversed_offices = {
        "training office": sample_offices["training office"],
        "library": sample_offices["library"],
        "student affairs": sample_offices["student affairs"],
        "it helpdesk": sample_offices["it helpdesk"],
    }
    result = all_offices(reversed_offices)
    assert [o.name for o in result] == [
        "IT Helpdesk",
        "Library",
        "Student Affairs",
        "Training Office",
    ]


def test_all_offices_preserves_office_fields(
    sample_offices: dict[str, Office],
) -> None:
    """Returned Office objects must retain all attributes intact."""
    result = all_offices(sample_offices)
    it_helpdesk = result[0]
    assert it_helpdesk.name == "IT Helpdesk"
    assert it_helpdesk.room == "E.005"
    assert it_helpdesk.hours == "Mon-Fri 08:00-17:00"

    library = result[1]
    assert library.name == "Library"
    assert library.room == "B.201"
    assert library.hours == "Mon-Sat 07:00-20:00"
