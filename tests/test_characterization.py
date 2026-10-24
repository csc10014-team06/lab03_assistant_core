"""Characterization ("golden") tests for the assistant's observable behaviour.

They pin what ``monolith/assistant_monolith.py`` answers today, so the
refactored ``assistant_core`` package can be checked against the same
expectations. Every test runs against two implementations:

* ``monolith`` - the original script (randomness and ``sleep`` are patched out);
* ``package``  - ``assistant_core.service.AssistantService``, skipped until it
  exists. It is built from the interface contracts in ``docs/team-plan.md``.

Cases in ``MONOLITH_QUIRKS`` document bugs the team intends to fix; they only
run against the monolith, so fixing them does not break this file.

Change an expected value here only on purpose, with the whole team agreeing.
"""

from __future__ import annotations

import importlib.util
import random
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MONOLITH_PATH = REPO_ROOT / "monolith" / "assistant_monolith.py"

GREETING = "Hello! I can help with offices, fees and rules."


class EchoLLM:
    """Deterministic stand-in with the same reply format as the monolith's ``llm()``."""

    def complete(self, prompt: str) -> str:
        return "Here is what I found: " + prompt[-120:]


class FailingLLM:
    def complete(self, prompt: str) -> str:
        from assistant_core.llm import LLMError

        raise LLMError("LLM timeout")


class MonolithDriver:
    def __init__(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        spec = importlib.util.spec_from_file_location(
            "assistant_monolith", MONOLITH_PATH
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.DEBUG = False
        monkeypatch.setattr(time, "sleep", lambda _seconds: None)
        monkeypatch.setattr(random, "random", lambda: 0.5)  # LLM call succeeds
        module.load()
        module.BASE = str(tmp_path)  # after load(): history files go to tmp_path
        self._monkeypatch = monkeypatch
        self._module = module
        self.history_dir = tmp_path

    def handle(self, message: str) -> str:
        return self._module.handle(message)

    def make_llm_fail(self) -> None:
        self._monkeypatch.setattr(random, "random", lambda: 0.0)


class PackageDriver:
    def __init__(self, tmp_path: Path) -> None:
        service = pytest.importorskip("assistant_core.service")
        from assistant_core.data_loader import load_handbook, load_offices

        from assistant_core.config import Settings

        settings = Settings(history_dir=tmp_path)
        self._offices = load_offices(settings.offices_path)
        self._rules = load_handbook(settings.handbook_path)
        self._settings = settings
        self._service_cls = service.AssistantService
        self._service = self._service_cls(
            settings, self._offices, self._rules, EchoLLM()
        )
        self.history_dir = tmp_path

    def handle(self, message: str) -> str:
        return self._service.handle(message)

    def make_llm_fail(self) -> None:
        self._service = self._service_cls(
            self._settings, self._offices, self._rules, FailingLLM()
        )


@pytest.fixture(params=["monolith", "package"])
def assistant(request, monkeypatch, tmp_path):
    if request.param == "monolith":
        return MonolithDriver(monkeypatch, tmp_path)
    return PackageDriver(tmp_path)


@pytest.fixture
def monolith(monkeypatch, tmp_path):
    return MonolithDriver(monkeypatch, tmp_path)


GOLDEN_CASES = [
    # the monolith's own hand-run test() cases
    ("hi", GREETING),
    ("tuition for 18 credits and 2 retake", "Your tuition is 9450000 VND"),
    ("where is the library", "Library: room B.201, open Mon-Sat 07:00-20:00"),
    (
        "can I register my thesis with 118 credits",
        (
            "Here is what I found: hey have at least 120 accumulated credits and a GPA of"
            " at least 2.0. Question: can I register my thesis with 118 credits"
            " (source: H26-5.3)"
        ),
    ),
    ("tuition 40 credits", "too many credits"),
    ("", "empty"),
    # greetings
    ("hello", GREETING),
    ("hey", GREETING),
    ("xin chao", GREETING),
    ("HELLO  ", GREETING),
    # fees
    ("fee", "How many credits?"),
    ("tuition for 2 retakes", "How many credits?"),
    ("tuition 30 credits", "Your tuition is 13500000 VND"),
    ("tuition 31 credits", "too many credits"),
    ("fee 10 credits 1 retake", "Your tuition is 5175000 VND"),
    ("What is the fee for 15 credits?", "Your tuition is 6750000 VND"),
    # offices
    (
        "Where is Student Affairs?",
        "Student Affairs: room I.102, open Mon-Fri 08:00-16:00",
    ),
    ("training office hours", "Training Office: room I.101, open Mon-Fri 07:30-16:30"),
    ("it helpdesk", "IT Helpdesk: room E.005, open Mon-Fri 08:00-17:00"),
    # handbook rules via the LLM
    (
        "what about exam absence",
        (
            "Here is what I found: for medical reasons must submit evidence to the"
            " Training Office within 3 working days. Question: what about exam absence"
            " (source: H26-7.2)"
        ),
    ),
    (
        "how late can thesis registration be",
        (
            "Here is what I found: thesis registration requires approval from the"
            " Faculty and the supervisor. Question: how late can thesis registration be"
            " (source: H26-5.4)"
        ),
    ),
    # nothing matches
    ("blah", "Sorry I dont know"),
]


@pytest.mark.parametrize(("message", "expected"), GOLDEN_CASES)
def test_golden_answers(assistant, message, expected):
    assert assistant.handle(message) == expected


def test_llm_failure_falls_back_to_rule_text(assistant):
    assistant.make_llm_fail()
    assert assistant.handle("can I register my thesis with 118 credits") == (
        "Students may register a thesis when they have at least 120 accumulated"
        " credits and a GPA of at least 2.0. (source: H26-5.3)"
    )


def test_history_lists_every_message_including_itself(assistant):
    assistant.handle("hi")
    assistant.handle("where is the library")
    assert assistant.handle("history") == "hi\nwhere is the library\nhistory"


def test_stats_counts_message_categories(assistant):
    for message in [
        "hi",
        "tuition 18 credits",
        "fee 10 credits",
        "where is the library",
        "can I retake an exam",
    ]:
        assistant.handle(message)
    # "stats" itself is counted as "other"
    assert assistant.handle("stats") == "fee=2 office=1 rule=1 other=2"


def test_save_writes_history_to_named_file(assistant):
    assistant.handle("hi")
    assert assistant.handle("save notes.txt") == "saved"
    saved = assistant.history_dir / "notes.txt"
    assert saved.read_text(encoding="utf-8") == "hi\nsave notes.txt\n"


def test_save_without_name_uses_default_file(assistant):
    assistant.handle("hi")
    assert assistant.handle("save") == "saved"
    assert (assistant.history_dir / "history.txt").read_text(encoding="utf-8") == (
        "hi\nsave\n"
    )


# Known bugs: pinned for the monolith only, expected to change in the package.
MONOLITH_QUIRKS = [
    # substring match: "coffee" contains "fee" (dieu_sp fixes in fees.py)
    ("I want a coffee", "How many credits?"),
    # the save command lower-cases the file name
    ("save MyNotes.TXT", "saved"),
]


@pytest.mark.parametrize(("message", "expected"), MONOLITH_QUIRKS)
def test_monolith_quirks(monolith, message, expected):
    assert monolith.handle(message) == expected


def test_monolith_save_lowercases_filename(monolith):
    monolith.handle("save MyNotes.TXT")
    assert [p.name for p in monolith.history_dir.iterdir()] == ["mynotes.txt"]
