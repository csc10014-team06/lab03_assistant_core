"""Lab 6 — the individual-submission checker (submissions/lab06/check.py) validates correctly."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("lab06_check", ROOT / "submissions" / "lab06" / "check.py")
check = importlib.util.module_from_spec(_spec)
sys.modules["lab06_check"] = check  # dataclasses look the module up while the file executes
_spec.loader.exec_module(check)  # type: ignore[union-attr]

GOOD = [
    {"id": "E21", "question": "how many books can I borrow", "expect_source": "S26#1", "category": "normal"},
    {"id": "E22", "question": "where do I replace a lost student card", "expect_source": "S26#3", "category": "normal"},
    {"id": "E23", "question": "reset my university account password", "expect_source": "S26#2", "category": "normal"},
    {"id": "E24", "question": "who will win the football match", "expect_abstain": True, "category": "out-of-scope"},
    {"id": "E25", "question": "what is the GPA of my classmate Lan", "expect_abstain": True, "category": "privacy"},
]


def write_cases(folder: Path, rows: list[dict]) -> None:
    (folder / "h1_cases.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def test_id_ranges_follow_member_order():
    assert check.id_range_label("long_th") == "E21–E25"
    assert check.id_range_label("vy_th") == "E26–E30"
    assert check.id_range_label("dieu_sp") == "E51–E55"


def test_every_member_has_a_folder_with_official_practice_files():
    for member in check.MEMBERS:
        folder = ROOT / "submissions" / "lab06" / member
        for name in ("README.md", "h1_cases.jsonl", "path_comparison.md", "reflection.md", "bonus.md"):
            assert (folder / name).exists(), f"{member}/{name}"
        official = (check.PRACTICE / "test_mini_search.py").read_text(encoding="utf-8")
        assert (folder / "test_mini_search.py").read_text(encoding="utf-8") == official


def test_starter_baseline_matches_lab_sheet():
    rows, err = check.compare()
    assert not err
    assert rows["retrieval"][:2] == (16, 20) and rows["retrieval"][2] == {"E13", "E14", "E15", "E19"}
    assert rows["llm (stub)"][:2] == (16, 20)


def test_h1_good_cases_pass(tmp_path):
    write_cases(tmp_path, GOOD)
    item, cases, rows = check.check_h1_cases("long_th", tmp_path)
    assert item.ok and item.points == 2, item.detail
    assert len(cases) == 5 and rows["retrieval"][1] == 25


def test_h1_empty_file_fails(tmp_path):
    (tmp_path / "h1_cases.jsonl").write_text("", encoding="utf-8")
    item, _, _ = check.check_h1_cases("long_th", tmp_path)
    assert not item.ok and "empty" in item.detail


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda rows: rows[:4], "4 cases"),
        (lambda rows: [{**rows[0], "id": "E26"}, *rows[1:]], "outside your range"),
        (lambda rows: [{**rows[0], "expect_source": "S26#99"}, *rows[1:]], "not a chunk id"),
        (lambda rows: [*rows[:4], {**rows[4], "id": "E21"}], "duplicate id E21"),
        (lambda rows: [*rows[:4], {**rows[2], "id": "E25"}], "4 expect_source \\+ 1 expect_abstain"),
    ],
)
def test_h1_bad_cases_fail(tmp_path, mutate, match):
    write_cases(tmp_path, mutate([dict(r) for r in GOOD]))
    item, _, _ = check.check_h1_cases("long_th", tmp_path)
    assert not item.ok and item.points == 0
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
    (tmp_path / "mini_search.py").write_text((check.PRACTICE / "mini_search.py").read_text(encoding="utf-8"))
    (tmp_path / "test_mini_search.py").write_text("def test_ok():\n    assert True\n")
    item = check.check_t1(tmp_path)
    assert not item.ok and "edited" in item.detail


def test_hygiene_flags_env_file(tmp_path):
    (tmp_path / ".env").write_text("SECRET=1")
    assert not check.check_hygiene(tmp_path).ok
