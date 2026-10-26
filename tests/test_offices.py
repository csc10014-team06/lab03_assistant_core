"""test_offices.py — Unit tests for offices.py (Office lookup).

Owner: truyen_lp (Lab 3)

Coverage targets:
- Exact name match, case-insensitivity, embedded in sentences.
- Misses: nonexistent office, empty query, whitespace-only.
- Edge cases: empty offices dictionary, multiple office names in one message.
- Return type: immutable Office dataclass with correct attributes.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from assistant_core.data_loader import Office
from assistant_core.offices import find_office


@pytest.fixture
def sample_offices() -> dict[str, Office]:
    """Sample office mapping with lowercase keys, identical to data_loader contract."""
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


class TestFindOfficeHits:
    """Tests where an office is expected to be found."""

    @pytest.mark.parametrize(
        ("query", "expected_name", "expected_room"),
        [
            ("library", "Library", "B.201"),
            ("where is the library", "Library", "B.201"),
            ("where is the library?", "Library", "B.201"),
            ("Student Affairs", "Student Affairs", "I.102"),
            ("STUDENT AFFAIRS office hours", "Student Affairs", "I.102"),
            ("training office hours", "Training Office", "I.101"),
            ("it helpdesk", "IT Helpdesk", "E.005"),
            ("I need help from the IT HELPDESK please", "IT Helpdesk", "E.005"),
        ],
    )
    def test_find_office_matches_expected(
        self, sample_offices, query, expected_name, expected_room
    ):
        result = find_office(query, sample_offices)
        assert result is not None
        assert result.name == expected_name
        assert result.room == expected_room

    def test_find_office_preserves_first_match_order(self, sample_offices):
        """When text mentions multiple offices, the first key in dictionary order wins."""
        # Both "training office" and "library" appear in text;
        # "training office" is earlier in sample_offices.
        query = "Can the training office or the library help me?"
        result = find_office(query, sample_offices)
        assert result is not None
        assert result.name == "Training Office"

        # Reverse dictionary order
        reversed_offices = {
            "library": sample_offices["library"],
            "training office": sample_offices["training office"],
        }
        result_rev = find_office(query, reversed_offices)
        assert result_rev is not None
        assert result_rev.name == "Library"


class TestFindOfficeMisses:
    """Tests where no office should match."""

    @pytest.mark.parametrize(
        "query",
        [
            ("where is the canteen"),
            ("dormitory registration"),
            ("hello, how are you?"),
            ("12345"),
            (""),
            ("    "),
            ("\n\t  "),
        ],
    )
    def test_find_office_returns_none_when_no_match(self, sample_offices, query):
        assert find_office(query, sample_offices) is None

    def test_find_office_with_empty_offices_dict(self):
        """When the offices dictionary is empty, always return None."""
        assert find_office("library", {}) is None


class TestOfficeDataclassProperties:
    """Verify dataclass contract, immutability, and attribute integrity."""

    def test_returns_office_dataclass_instance(self, sample_offices):
        result = find_office("library", sample_offices)
        assert isinstance(result, Office)
        assert result.name == "Library"
        assert result.room == "B.201"
        assert result.hours == "Mon-Sat 07:00-20:00"

    def test_office_dataclass_is_frozen(self, sample_offices):
        result = find_office("library", sample_offices)
        assert result is not None
        with pytest.raises(FrozenInstanceError):
            result.room = "X.999"  # type: ignore[misc]
