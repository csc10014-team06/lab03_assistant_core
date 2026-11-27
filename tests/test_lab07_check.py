"""Lab 7 — the individual-submission checker (submissions/lab07/check.py) validates correctly.

Templates are read from lab07/worksheets (never from a member folder, which members fill in).
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("lab07_check", ROOT / "submissions" / "lab07" / "check.py")
check = importlib.util.module_from_spec(_spec)
sys.modules["lab07_check"] = check  # dataclasses look the module up while the file executes
_spec.loader.exec_module(check)  # type: ignore[union-attr]

CHECKLIST = (check.WORKSHEETS / "usability_checklist.md").read_text(encoding="utf-8")
OBSERVATIONS = (check.WORKSHEETS / "user_test_observations.md").read_text(encoding="utf-8")


def filled_observations(rows: int = 3) -> str:
    text = OBSERVATIONS.replace("first name only): ____  Date: ____", "first name only): An  Date: 2026-11-28")
    for i in range(1, rows + 1):
        text = text.replace(f"| {i} | | | | |", f"| {i} | clicked an example | an answer | slow | add spinner |")
    return text


def test_every_member_has_a_folder_with_official_files():
    for member in check.MEMBERS:
        folder = ROOT / "submissions" / "lab07" / member
        assert (folder / "README.md").exists(), member
        for name in ("hello_streamlit.py", "test_hello_streamlit.py"):
            assert (folder / name).exists(), f"{member}/{name}"
        official = (check.PRACTICE / "test_hello_streamlit.py").read_text(encoding="utf-8")
        assert (folder / "test_hello_streamlit.py").read_text(encoding="utf-8") == official


def test_checklist_template_fails(tmp_path):
    (tmp_path / "usability_checklist.md").write_text(CHECKLIST, encoding="utf-8")
    item = check.check_t2(tmp_path)
    assert not item.ok and "neither ticked nor explained" in item.detail


def test_checklist_ticked_or_explained_passes(tmp_path):
    text = CHECKLIST.replace("- [ ] ", "- [x] ", 9)
    text = text.replace("- [ ] Works on a phone-width window", "- [ ] Works on a phone-width window — sidebar hidden")
    (tmp_path / "usability_checklist.md").write_text(text, encoding="utf-8")
    item = check.check_t2(tmp_path)
    assert item.ok and item.detail.startswith("9/10")


def test_checklist_deleted_item_fails(tmp_path):
    text = "\n".join(ln for ln in CHECKLIST.replace("- [ ] ", "- [x] ").splitlines() if "phone-width" not in ln)
    (tmp_path / "usability_checklist.md").write_text(text, encoding="utf-8")
    assert "do not delete items" in check.check_t2(tmp_path).detail


def test_observations_template_fails(tmp_path):
    (tmp_path / "user_test_observations.md").write_text(OBSERVATIONS, encoding="utf-8")
    item = check.check_t3(tmp_path)
    assert not item.ok and "tester" in item.detail and "0 complete" in item.detail


@pytest.mark.parametrize(("rows", "ok"), [(2, False), (3, True)])
def test_observations_need_three_complete_rows(tmp_path, rows, ok):
    (tmp_path / "user_test_observations.md").write_text(filled_observations(rows), encoding="utf-8")
    assert check.check_t3(tmp_path).ok is ok


def test_t1_detects_edited_test_file(tmp_path):
    shutil.copy(check.PRACTICE / "hello_streamlit.py", tmp_path)
    (tmp_path / "test_hello_streamlit.py").write_text("def test_ok():\n    assert True\n")
    item = check.check_t1(tmp_path)
    assert not item.ok and "edited" in item.detail


def test_t1_explains_missing_streamlit(tmp_path, monkeypatch):
    for name in ("hello_streamlit.py", "test_hello_streamlit.py"):
        shutil.copy(check.PRACTICE / name, tmp_path)
    monkeypatch.setattr(check.importlib.util, "find_spec", lambda name: None)
    assert "lab07/starter venv" in check.check_t1(tmp_path).detail


def test_hygiene_flags_env_file(tmp_path):
    (tmp_path / ".env").write_text("SECRET=1")
    assert not check.check_hygiene(tmp_path).ok
