"""test_handbook.py — Unit tests for handbook.py (Rule search & scoring).

Owner: truyen_lp (Lab 3)

Coverage targets:
- Pure scoring function score_rule(): word len <= 3 ignored, word len > 3 scored,
  case-insensitivity, boundary punctuation cleaning, repeated words.
- Search function best_rule(): clear hit, miss, min_score thresholding,
  tie-breaking (first rule in list wins), empty list, empty query.
- Dataclass contract: immutable Rule with id, title, text attributes.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from assistant_core.data_loader import Rule
from assistant_core.handbook import (
    best_rule,
    find_exam_absence_rule,
    get_exam_absence_deadline,
    score_rule,
)


@pytest.fixture
def sample_rules() -> list[Rule]:
    """Sample rules reflecting the student handbook dataset."""
    return [
        Rule(
            id="H26-4.2",
            title="Retaking a course",
            text=(
                "Students may retake a course they failed. Retake credits are charged at "
                "1.5 times the normal rate. Final-year students must register retakes "
                "before week 2."
            ),
        ),
        Rule(
            id="H26-5.3",
            title="Thesis registration",
            text=(
                "Students may register a thesis when they have at least 120 accumulated credits "
                "and a GPA of at least 2.0."
            ),
        ),
        Rule(
            id="H26-5.4",
            title="Late thesis registration",
            text="Late thesis registration requires approval from the Faculty and the supervisor.",
        ),
        Rule(
            id="H26-6.1",
            title="Credit load",
            text=(
                "A regular semester load is between 14 and 30 credits. "
                "More than 30 credits requires approval."
            ),
        ),
        Rule(
            id="H26-7.2",
            title="Exam absence",
            text=(
                "Students absent from a final exam for medical reasons must submit evidence to the "
                "Training Office within 3 working days."
            ),
        ),
    ]


class TestScoreRule:
    """Unit tests for the pure scoring function score_rule()."""

    def test_short_words_ignored(self):
        rule = Rule(id="R1", title="Test", text="Quick brown fox jumps")
        # "fox", "the", "and", "a" are all len <= 3
        assert score_rule("the fox and a cat", rule) == 0

    def test_words_longer_than_three_characters_scored(self):
        rule = Rule(id="R1", title="Test", text="Quick brown fox jumps over lazy dog")
        # "quick" (5), "brown" (5), "lazy" (4) all match
        assert score_rule("quick brown lazy bear", rule) == 3

    def test_case_insensitive_scoring(self):
        rule = Rule(id="R1", title="Test", text="Students must submit medical evidence")
        assert score_rule("STUDENTS SUBMIT EVIDENCE", rule) == 3

    def test_punctuation_stripped_from_words(self):
        rule = Rule(id="R1", title="Test", text="Students must submit medical evidence")
        # "students,", "submit!", "evidence?" should match after stripping punctuation
        assert score_rule("students, submit! evidence?", rule) == 3

    def test_repeated_matching_words_increment_score(self):
        """Repeated keywords in the query contribute multiple times, matching monolith."""
        rule = Rule(id="R1", title="Test", text="Students must register their thesis")
        # "thesis" appears twice, both contribute to score
        assert score_rule("thesis and thesis", rule) == 2
        # Single appearance gives 1
        assert score_rule("only one thesis", rule) == 1

    def test_empty_query_scores_zero(self):
        rule = Rule(id="R1", title="Test", text="Some important policy text")
        assert score_rule("", rule) == 0
        assert score_rule("   ", rule) == 0


class TestBestRuleSearch:
    """Unit tests for best_rule() query search."""

    def test_thesis_registration_finds_rule(self, sample_rules):
        query = "can I register my thesis with 118 credits"
        match = best_rule(query, sample_rules)
        assert match is not None
        assert match.id == "H26-5.3"
        assert match.title == "Thesis registration"

    def test_exam_absence_finds_rule(self, sample_rules):
        query = "what about final exam absence"
        match = best_rule(query, sample_rules)
        assert match is not None
        assert match.id == "H26-7.2"
        assert "medical reasons" in match.text

    def test_no_matching_keywords_returns_none(self, sample_rules):
        assert best_rule("what is the weather today in Hanoi", sample_rules) is None

    def test_empty_query_returns_none(self, sample_rules):
        assert best_rule("", sample_rules) is None
        assert best_rule("   \n\t", sample_rules) is None

    def test_empty_rules_list_returns_none(self):
        assert best_rule("register my thesis", []) is None

    def test_min_score_threshold_enforced(self, sample_rules):
        # "exam" matches H26-7.2 (score = 1)
        # With default min_score=1, it should match
        assert best_rule("exam", sample_rules, min_score=1) is not None
        # With min_score=2, score 1 should return None
        assert best_rule("exam", sample_rules, min_score=2) is None

    def test_tie_breaking_preserves_first_rule_encountered(self):
        """When two rules score the same max score, the first rule in list wins."""
        rule_a = Rule(
            id="A",
            title="First",
            text="Standard university policy for credit registration",
        )
        rule_b = Rule(
            id="B",
            title="Second",
            text="Faculty specific policy for credit registration",
        )
        # Query with equal matches in both: "credit registration"
        rules_ab = [rule_a, rule_b]
        rules_ba = [rule_b, rule_a]

        match_ab = best_rule("credit registration", rules_ab)
        assert match_ab is not None
        assert match_ab.id == "A"

        match_ba = best_rule("credit registration", rules_ba)
        assert match_ba is not None
        assert match_ba.id == "B"


class TestRuleDataclassProperties:
    """Verify Rule dataclass contracts and immutability."""

    def test_rule_attributes(self, sample_rules):
        rule = sample_rules[0]
        assert isinstance(rule, Rule)
        assert rule.id == "H26-4.2"
        assert rule.title == "Retaking a course"
        assert "retake" in rule.text.lower()

    def test_rule_dataclass_is_frozen(self, sample_rules):
        rule = sample_rules[0]
        with pytest.raises(FrozenInstanceError):
            rule.title = "Modified Title"  # type: ignore[misc]


class TestExamAbsenceExtension:
    """Tests for the AI-extended exam absence feature."""

    def test_find_exam_absence_rule_by_id(self, sample_rules):
        rule = find_exam_absence_rule(sample_rules)
        assert rule is not None
        assert rule.id == "H26-7.2"

    def test_find_exam_absence_rule_fallback_to_keywords(self):
        # Different ID but content mentions absence and medical reasons
        fallback_rule = Rule(
            id="CUSTOM-99",
            title="Absence Notice",
            text="Medical reasons for exam absence must be certified.",
        )
        found = find_exam_absence_rule([fallback_rule])
        assert found is not None
        assert found.id == "CUSTOM-99"

    def test_find_exam_absence_rule_missing(self):
        unrelated = [Rule(id="R1", title="Fee", text="Pay tuition on time.")]
        assert find_exam_absence_rule(unrelated) is None
        assert find_exam_absence_rule([]) is None

    def test_get_exam_absence_deadline_extracted_correctly(self, sample_rules):
        response = get_exam_absence_deadline(sample_rules)
        assert response is not None
        assert "within 3 working days" in response
        assert "Training Office" in response
        assert "(source: H26-7.2)" in response

    def test_get_exam_absence_deadline_missing_rule(self):
        assert get_exam_absence_deadline([]) is None

    def test_get_exam_absence_deadline_no_regex_match(self):
        rule = Rule(
            id="H26-7.2",
            title="Exam absence",
            text="Students absent must contact the dean immediately.",
        )
        response = get_exam_absence_deadline([rule])
        assert response is not None
        assert "contact the dean immediately" in response
        assert "(source: H26-7.2)" in response

    def test_get_exam_absence_deadline_dynamic_office_and_deadline(self):
        """Office and deadline are dynamically extracted from rule.text (single source of truth)."""
        rule = Rule(
            id="H26-7.2",
            title="Exam absence",
            text=(
                "Students absent from exam must submit evidence "
                "to the Faculty Office within 5 working days."
            ),
        )
        response = get_exam_absence_deadline([rule])
        assert response is not None
        assert "within 5 working days" in response
        assert "to the Faculty Office" in response
        assert "(source: H26-7.2)" in response


