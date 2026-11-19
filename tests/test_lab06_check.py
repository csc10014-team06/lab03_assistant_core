"""Lab 6 — the individual-submission checker (submissions/lab06/check.py) validates correctly."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.rag.index import KBIndex

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("lab06_check", ROOT / "submissions" / "lab06" / "check.py")
check = importlib.util.module_from_spec(_spec)
sys.modules["lab06_check"] = check  # dataclasses look the module up while the file executes
_spec.loader.exec_module(check)  # type: ignore[union-attr]


@pytest.fixture(scope="module")
def index() -> KBIndex:
    return KBIndex.from_dir(Settings().kb_dir)


def write_cases(folder: Path, rows: list[dict]) -> None:
    (folder / "h1_cases.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


GOOD = [
    {"id": "E21", "question": "how many books can I borrow", "expect_source": "S26#1"},
    {"id": "E22", "question": "graduation English certificate", "expect_source": "H26#10"},
    {"id": "E23", "question": "semester GPA below 1.0 warning", "expect_source": "H26#9"},
    {"id": "E24", "question": "who will win the football match", "expect_abstain": True, "category": "out-of-scope"},
    {"id": "E25", "question": "what is Lan's GPA", "expect_abstain": True, "category": "other-person"},
]


def test_id_ranges_follow_member_order():
    assert check.id_range_label("long_th") == "E21–E25"
    assert check.id_range_label("vy_th") == "E26–E30"
    assert check.id_range_label("dieu_sp") == "E51–E55"


def test_every_member_has_a_folder_with_templates():
    for member in check.MEMBERS:
        folder = ROOT / "submissions" / "lab06" / member
        for name in ("README.md", "mini_search.py", "test_mini_search.py", "h1_cases.jsonl",
                     "path_comparison.md", "reflection.md", "bonus.md"):
            assert (folder / name).exists(), f"{member}/{name}"


def test_h1_good_cases_pass(tmp_path, index):
    write_cases(tmp_path, GOOD)
    item, cases = check.check_h1_cases("long_th", tmp_path, index)
    assert item.ok and item.points == 2 and len(cases) == 5


def test_h1_empty_file_fails(tmp_path, index):
    (tmp_path / "h1_cases.jsonl").write_text("", encoding="utf-8")
    item, _ = check.check_h1_cases("long_th", tmp_path, index)
    assert not item.ok and "empty" in item.detail


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda rows: rows[:4], "4 cases"),
        (lambda rows: [{**rows[0], "id": "E26"}, *rows[1:]], "outside your range"),
        (lambda rows: [{**rows[0], "expect_source": "S26#99"}, *rows[1:]], "not a chunk id"),
        (lambda rows: [{**rows[0], "id": "E02"}, *rows[1:]], "duplicate id E02"),
        (lambda rows: [*rows[:3], rows[3], {**rows[2], "id": "E25"}], "4 normal \\+ 1 abstain"),
    ],
)
def test_h1_bad_cases_fail(tmp_path, index, mutate, match):
    write_cases(tmp_path, mutate([dict(r) for r in GOOD]))
    item, _ = check.check_h1_cases("long_th", tmp_path, index)
    assert not item.ok
    assert item.points == 0
    assert re.search(match, item.detail), item.detail


def test_reflection_template_fails_and_filled_passes(tmp_path):
    template = (ROOT / "submissions" / "lab06" / "long_th" / "reflection.md").read_text(encoding="utf-8")
    (tmp_path / "reflection.md").write_text(template, encoding="utf-8")
    assert not check.check_reflection(tmp_path).ok
    filled = template
    for i in range(1, 6):
        filled = filled.replace(f"TODO line {i}", f"line {i}" + (" — the min_score threshold" if i == 3 else ""))
    (tmp_path / "reflection.md").write_text(filled, encoding="utf-8")
    assert check.check_reflection(tmp_path).ok


def test_comparison_template_fails(tmp_path):
    template = (ROOT / "submissions" / "lab06" / "long_th" / "path_comparison.md").read_text(encoding="utf-8")
    (tmp_path / "path_comparison.md").write_text(template, encoding="utf-8")
    t4, t5 = check.check_comparison(tmp_path)
    assert not t4.ok and not t5.ok


def test_t1_detects_edited_test_file(tmp_path):
    practice = ROOT / "submissions" / "lab06" / "_practice"
    (tmp_path / "mini_search.py").write_text((practice / "mini_search.py").read_text(encoding="utf-8"))
    (tmp_path / "test_mini_search.py").write_text("def test_ok():\n    assert True\n")
    item = check.check_t1(tmp_path)
    assert not item.ok and "edited" in item.detail


def test_hygiene_flags_env_file(tmp_path):
    (tmp_path / ".env").write_text("SECRET=1")
    assert not check.check_hygiene(tmp_path).ok
