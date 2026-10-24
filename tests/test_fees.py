import pytest

from assistant_core.config import Settings
from assistant_core.fees import (
    FeeQuery,
    TooManyCreditsError,
    compute_tuition,
    is_fee_question,
    parse_fee_query,
)

DEFAULTS = Settings()


@pytest.mark.parametrize(
    "text",
    [
        "fee",
        "What is the fee for 15 credits?",
        "what are the fees for 18 credits",
        "TUITION 30 credits",
        "tuition, please",
        "fee-paying course",
    ],
)
def test_is_fee_question_true(text):
    assert is_fee_question(text)


@pytest.mark.parametrize(
    "text",
    [
        "I want a coffee",  # substring "fee" fooled the monolith
        "coffee 18",
        "feedback on my thesis",
        "where is the library",
        "",
    ],
)
def test_is_fee_question_false(text):
    assert not is_fee_question(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("tuition for 18 credits and 2 retake", FeeQuery(18, 2)),
        ("fee for 2 retake 18 credits", FeeQuery(18, 2)),  # order does not matter
        ("fee 10 credits 1 retake", FeeQuery(10, 1)),
        ("tuition 18 credits 3 retakes", FeeQuery(18, 3)),
        ("What is the fee for 15 credits?", FeeQuery(15, 0)),
        ("fee 18 credits 2?retakes", FeeQuery(18, 2)),  # "?" splits words
        ("tuition 18, please", FeeQuery(18, 0)),  # trailing punctuation
        ("tuition (18) credits", FeeQuery(18, 0)),
        ("TUITION 20 CREDITS 1 RETAKE", FeeQuery(20, 1)),
        ("tuition 18 credits and 20 credits", FeeQuery(18, 0)),  # first number wins
        ("tuition 0 credits 18", FeeQuery(18, 0)),  # 0 is not a credit count
        ("tuition for 2 retakes", FeeQuery(0, 2)),
        ("fee", FeeQuery(0, 0)),
        ("", FeeQuery(0, 0)),
        ("tuition 2nd semester", FeeQuery(0, 0)),  # not a whole number
        ("tuition -5 credits", FeeQuery(0, 0)),  # sign is not stripped
        ("tuition 2² credits", FeeQuery(0, 0)),  # non-ASCII digit, no crash
    ],
)
def test_parse_fee_query(text, expected):
    assert parse_fee_query(text) == expected


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (FeeQuery(18, 2), 9_450_000),  # 18 * 450 000 + 2 * 675 000
        (FeeQuery(10, 1), 5_175_000),
        (FeeQuery(15, 0), 6_750_000),
        (FeeQuery(30, 0), 13_500_000),  # limit is inclusive
        (FeeQuery(1, 0), 450_000),
        (FeeQuery(0, 2), 1_350_000),
        (FeeQuery(0, 0), 0),
        (FeeQuery(30, 5), 16_875_000),  # retakes do not count towards the limit
    ],
)
def test_compute_tuition_defaults(query, expected):
    assert compute_tuition(query, DEFAULTS) == expected


@pytest.mark.parametrize("credits", [31, 40, 1000])
def test_compute_tuition_too_many_credits(credits):
    with pytest.raises(TooManyCreditsError, match=f"{credits} credits"):
        compute_tuition(FeeQuery(credits, 0), DEFAULTS)


def test_too_many_credits_is_a_value_error():
    assert issubclass(TooManyCreditsError, ValueError)


def test_compute_tuition_uses_settings():
    s = Settings(credit_rate=500_000, retake_multiplier=2.0, max_credits=40)
    assert compute_tuition(FeeQuery(40, 1), s) == 21_000_000
    with pytest.raises(TooManyCreditsError):
        compute_tuition(FeeQuery(41, 0), s)


def test_compute_tuition_no_float_rounding_error():
    # 100 000 * 1.15 is 114 999.999... in float arithmetic
    s = Settings(credit_rate=100_000, retake_multiplier=1.15)
    assert compute_tuition(FeeQuery(0, 1), s) == 115_000


def test_compute_tuition_rounds_down():
    s = Settings(credit_rate=1, retake_multiplier=1.5)
    assert compute_tuition(FeeQuery(0, 1), s) == 1


def test_parse_then_compute_matches_monolith_answer():
    q = parse_fee_query("tuition for 18 credits and 2 retake")
    assert compute_tuition(q, DEFAULTS) == 9_450_000
