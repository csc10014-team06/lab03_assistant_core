"""test_service.py — unit tests for AssistantService.

Owner: nhat_dm

Coverage goals
--------------
* Every public method: handle(), stats(), save_history()
* Intent routing: fee, office, handbook+LLM, handbook+LLM-failure-fallback, other
* Edge cases from the plan: 0 credits, >30 credits, retakes, path traversal
* stats() counts are consistent with handle() routing
* History is instance-isolated (no shared global state between tests)
"""
from __future__ import annotations

from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.data_loader import Office, Rule
from assistant_core.llm import FakeLLM, LLMError
from assistant_core.service import AssistantService

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    """Settings with history_dir pointing to a temp directory."""
    return Settings(
        credit_rate=450_000,
        retake_multiplier=1.5,
        max_credits=30,
        history_dir=tmp_path,
    )


@pytest.fixture()
def sample_offices() -> dict[str, Office]:
    return {
        "library": Office(name="Library", room="A101", hours="8-17"),
        "registrar": Office(name="Registrar", room="B202", hours="8-12"),
        "student affairs": Office(name="Student Affairs", room="C303", hours="9-16"),
    }


@pytest.fixture()
def sample_rules() -> list[Rule]:
    return [
        Rule(
            id="R001",
            title="Thesis registration",
            text="Students may register their thesis after completing 90 credits.",
        ),
        Rule(
            id="R002",
            title="Exam absence",
            text="Exam absence must be reported within three days.",
        ),
        Rule(
            id="R003",
            title="Retake policy",
            text="Students may retake an exam if they failed the previous attempt.",
        ),
    ]


@pytest.fixture()
def service(settings, sample_offices, sample_rules) -> AssistantService:
    """A fresh AssistantService with FakeLLM (no network, no randomness)."""
    return AssistantService(settings, sample_offices, sample_rules, FakeLLM())


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_service(
    settings: Settings,
    offices: dict[str, Office] | None = None,
    rules: list[Rule] | None = None,
    llm=None,
) -> AssistantService:
    return AssistantService(
        settings,
        offices or {},
        rules or [],
        llm or FakeLLM(),
    )


# ---------------------------------------------------------------------------
# handle() — built-in commands
# ---------------------------------------------------------------------------

class TestHandleBuiltins:
    def test_empty_message(self, service):
        assert service.handle("") == "empty"

    def test_whitespace_only(self, service):
        assert service.handle("   ") == "empty"

    @pytest.mark.parametrize("greeting", ["hi", "hello", "hey", "xin chao"])
    def test_greetings(self, service, greeting):
        response = service.handle(greeting)
        assert "Hello" in response

    def test_history_empty(self, service):
        service.handle("hi")
        response = service.handle("history")
        assert "hi" in response
        assert "history" in response

    def test_history_accumulates(self, service):
        service.handle("hi")
        service.handle("hello")
        response = service.handle("history")
        assert "hi" in response
        assert "hello" in response

    def test_stats_command(self, service):
        service.handle("fee for 10 credits")
        response = service.handle("stats")
        assert "fee=" in response
        assert "office=" in response

    def test_save_default_filename(self, service, settings):
        service.handle("hi")
        response = service.handle("save")
        assert response == "saved"
        assert (settings.history_dir / "history.txt").exists()

    def test_save_custom_filename(self, service, settings):
        service.handle("hi")
        response = service.handle("save mylog.txt")
        assert response == "saved"
        assert (settings.history_dir / "mylog.txt").exists()

    def test_save_file_contains_history(self, service, settings):
        service.handle("hi")
        service.handle("hello")
        service.handle("save out.txt")
        content = (settings.history_dir / "out.txt").read_text(encoding="utf-8")
        assert "hi\n" in content
        assert "hello\n" in content


# ---------------------------------------------------------------------------
# handle() — fee intent
# ---------------------------------------------------------------------------

class TestHandleFee:
    def test_fee_basic(self, service):
        response = service.handle("tuition for 18 credits")
        assert "8100000" in response          # 18 * 450_000

    def test_fee_with_retakes(self, service):
        # 18 credits + 2 retakes = 18*450_000 + 2*450_000*1.5 = 8_100_000 + 1_350_000 = 9_450_000
        response = service.handle("tuition for 18 credits and 2 retake")
        assert "9450000" in response

    def test_fees_plural_triggers_fee_branch(self, service):
        assert service.handle("what are the fees?") == "How many credits?"
        assert service.stats()["fee"] == 1

    def test_fee_zero_credits(self, service):
        response = service.handle("how much is the fee?")
        assert response == "How many credits?"

    def test_fee_too_many_credits(self, service):
        response = service.handle("fee for 40 credits")
        assert response == "too many credits"

    def test_fee_exact_max_credits(self, service):
        response = service.handle("tuition for 30 credits")
        assert "13500000" in response         # 30 * 450_000

    def test_fee_word_boundary_coffee(self, service):
        """'coffee' must NOT trigger the fee branch (old monolith bug)."""
        response = service.handle("I want a coffee")
        assert "VND" not in response
        assert "credits" not in response.lower()

    @pytest.mark.parametrize("msg,expected", [
        ("fee for 1 credit", "450000"),
        ("tuition 10", "4500000"),
    ])
    def test_fee_parametrized(self, service, msg, expected):
        assert expected in service.handle(msg)


# ---------------------------------------------------------------------------
# handle() — office intent
# ---------------------------------------------------------------------------

class TestHandleOffice:
    def test_office_hit(self, service):
        response = service.handle("where is the library?")
        assert "Library" in response
        assert "A101" in response
        assert "8-17" in response

    def test_office_case_insensitive(self, service):
        response = service.handle("WHERE IS THE LIBRARY")
        assert "Library" in response

    def test_office_miss(self, service):
        response = service.handle("where is the cafeteria?")
        # Should NOT return an office line; falls through to the fallback
        assert response == "Sorry I dont know"

    def test_office_registrar(self, service):
        response = service.handle("I need the registrar office")
        assert "Registrar" in response
        assert "B202" in response


# ---------------------------------------------------------------------------
# handle() — handbook + LLM
# ---------------------------------------------------------------------------

class TestHandleHandbook:
    def test_rule_hit_returns_source(self, service):
        response = service.handle("can I register my thesis with 90 credits")
        assert "(source: R001)" in response

    def test_rule_llm_fallback_on_error(self, settings, sample_offices, sample_rules):
        """When LLM raises LLMError, service must return raw rule text."""

        class AlwaysFailLLM:
            def complete(self, prompt: str) -> str:
                raise LLMError("forced failure")

        svc = AssistantService(settings, sample_offices, sample_rules, AlwaysFailLLM())
        response = svc.handle("can I register my thesis")
        # Must still return the rule text, not propagate the exception
        assert "thesis" in response.lower()
        assert "(source: R001)" in response

    def test_no_match_returns_fallback(self, service):
        response = service.handle("what is the weather today?")
        assert response == "Sorry I dont know"

    def test_rule_exam_absence(self, service):
        response = service.handle("what happens if I miss the exam")
        assert "(source: R002)" in response


# ---------------------------------------------------------------------------
# save_history() — path traversal fix
# ---------------------------------------------------------------------------

class TestSaveHistoryPathTraversal:
    def test_path_traversal_blocked(self, service, settings):
        """'save ../../evil' must write to history_dir/evil, not above it."""
        service.handle("hi")
        path = service.save_history("../../evil.txt")
        # The resolved path must be inside history_dir
        assert path.parent.resolve() == settings.history_dir.resolve()
        assert path.name == "evil.txt"

    def test_absolute_path_blocked(self, service, settings, tmp_path):
        """An absolute path in the filename must be reduced to its basename."""
        service.handle("hi")
        abs_name = str(tmp_path / "sneaky" / "output.txt")
        path = service.save_history(abs_name)
        assert path.parent.resolve() == settings.history_dir.resolve()

    def test_empty_filename_uses_default(self, service, settings):
        service.handle("hi")
        path = service.save_history("")
        assert path.name == "history.txt"


# ---------------------------------------------------------------------------
# stats() — dict shape and counting
# ---------------------------------------------------------------------------

class TestStats:
    def test_stats_empty(self, service):
        result = service.stats()
        assert result == {"fee": 0, "office": 0, "rule": 0, "other": 0}

    def test_stats_fee_counted(self, service):
        service.handle("fee for 10 credits")
        assert service.stats()["fee"] == 1

    def test_stats_office_counted(self, service):
        service.handle("where is the library")
        assert service.stats()["office"] == 1

    def test_stats_rule_counted(self, service):
        # "thesis" is in _RULE_KEYWORDS; will score as rule if no office match
        service.handle("thesis registration deadline")
        stats = service.stats()
        assert stats["rule"] >= 1

    def test_stats_other_counted(self, service):
        service.handle("what is the weather")
        assert service.stats()["other"] == 1

    def test_stats_total_equals_history(self, service):
        messages = [
            "hi",
            "fee for 5 credits",
            "where is the library",
            "random stuff",
        ]
        for m in messages:
            service.handle(m)
        s = service.stats()
        total = s["fee"] + s["office"] + s["rule"] + s["other"]
        assert total == len(messages)


# ---------------------------------------------------------------------------
# Instance isolation — no shared global state
# ---------------------------------------------------------------------------

class TestInstanceIsolation:
    def test_two_services_independent_history(self, settings, sample_offices, sample_rules):
        svc1 = AssistantService(settings, sample_offices, sample_rules, FakeLLM())
        svc2 = AssistantService(settings, sample_offices, sample_rules, FakeLLM())
        svc1.handle("hi from svc1")
        # svc2 must have an empty history
        assert svc2.stats() == {"fee": 0, "office": 0, "rule": 0, "other": 0}

    def test_history_not_leaked_between_instances(self, settings):
        svc1 = make_service(settings)
        svc2 = make_service(settings)
        svc1.handle("secret message")
        response = svc2.handle("history")
        assert "secret message" not in response
