"""Lab 7 — self-check for an individual submission (run before sending the PR link to the LMS).

    python submissions/lab07/check.py long_th        # one member, detailed
    python submissions/lab07/check.py --all          # every member, one line each (Tech Lead)

T1 needs Streamlit, so run it with the Lab 7 venv (``lab07/starter/.venv``). Exit code 0 = every task passes.
"""

from __future__ import annotations

import argparse
import filecmp
import importlib.util
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRACTICE = ROOT / "lab07" / "practice"
WORKSHEETS = ROOT / "lab07" / "worksheets"
MEMBERS = ["long_th", "vy_th", "truyen_lp", "nhat_npm", "nhat_dm", "han_htg", "dieu_sp"]
FORBIDDEN = {".env", ".venv", "venv", "assistant.db"}
CHECK_ITEM = re.compile(r"^- \[(?P<mark>[ xX])\] (?P<text>.+)$")
BLANK = re.compile(r"^_+$")


@dataclass
class Item:
    task: str
    ok: bool
    detail: str


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def check_t1(folder: Path) -> Item:
    name = "T1 Streamlit practice"
    test, impl = folder / "test_hello_streamlit.py", folder / "hello_streamlit.py"
    if not impl.exists() or not test.exists():
        return Item(name, False, "hello_streamlit.py / test_hello_streamlit.py missing (copy from lab07/practice/)")
    if not filecmp.cmp(test, PRACTICE / "test_hello_streamlit.py", shallow=False):
        return Item(name, False, "test_hello_streamlit.py was edited; restore it from lab07/practice/")
    if importlib.util.find_spec("streamlit") is None:
        return Item(name, False, "streamlit is not installed here — run with the lab07/starter venv")
    proc = run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_hello_streamlit.py"], folder)
    m = re.search(r"(\d+) passed", proc.stdout)
    passed = int(m.group(1)) if m else 0
    return Item(name, proc.returncode == 0 and passed == 4, f"{passed}/4 passed")


def checklist_items(text: str) -> list[tuple[bool, str]]:
    return [(m["mark"] != " ", m["text"]) for ln in text.splitlines() if (m := CHECK_ITEM.match(ln.strip()))]


def check_t2(folder: Path) -> Item:
    name = "T2 usability checklist"
    path = folder / "usability_checklist.md"
    if not path.exists():
        return Item(name, False, "usability_checklist.md missing")
    expected = len(checklist_items((WORKSHEETS / "usability_checklist.md").read_text(encoding="utf-8")))
    items = checklist_items(path.read_text(encoding="utf-8"))
    if len(items) != expected:
        return Item(name, False, f"{len(items)} items, the worksheet has {expected} — do not delete items")
    open_without_note = [text for ticked, text in items if not ticked and " — " not in text]
    if open_without_note:
        return Item(name, False, f"{len(open_without_note)} item(s) neither ticked nor explained after ' — '")
    ticked = sum(t for t, _ in items)
    return Item(name, True, f"{ticked}/{expected} ticked, the rest explained")


def check_t3(folder: Path) -> Item:
    name = "T3 user test"
    path = folder / "user_test_observations.md"
    if not path.exists():
        return Item(name, False, "user_test_observations.md missing")
    text = path.read_text(encoding="utf-8")
    problems = []
    header = next((ln for ln in text.splitlines() if ln.startswith("Tester")), "")
    fields = re.findall(r":\s*([^:]*?)\s*(?=Date:|$)", header)
    if len(fields) < 2 or any(not f or BLANK.match(f) for f in fields[:2]):
        problems.append("fill in the tester's first name and the date")
    rows = []
    for ln in text.splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if ln.startswith("|") and len(cells) == 5 and cells[0].isdigit():
            rows.append(cells[1:])
    filled = [r for r in rows if all(r)]
    if len(filled) < 3:
        problems.append(f"{len(filled)} complete observation row(s) (need 3, every column filled)")
    return Item(name, not problems, "; ".join(problems) or f"{len(filled)} observations")


def check_hygiene(folder: Path) -> Item:
    found = {p.name for p in folder.iterdir() if p.name in FORBIDDEN or p.suffix == ".db"}
    tracked = run(["git", "ls-files", "--", str(folder)], ROOT).stdout.split()
    found |= {Path(t).name for t in tracked if Path(t).name in FORBIDDEN or t.endswith(".db")}
    return Item("hygiene", not found, f"remove: {', '.join(sorted(found))}" if found else "no .env / .venv / *.db")


def check_member(member: str) -> list[Item]:
    folder = HERE / member
    if not folder.is_dir():
        raise SystemExit(f"no folder {folder}")
    return [check_t1(folder), check_t2(folder), check_t3(folder), check_hygiene(folder)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("member", nargs="?", choices=MEMBERS)
    ap.add_argument("--all", action="store_true", help="summarise every member")
    args = ap.parse_args(argv)
    if not args.member and not args.all:
        ap.error("give a member name or --all")
    if args.all:
        print("| member | T1 | T2 | T3 | hygiene |\n|---|---|---|---|---|")
        results = {m: check_member(m) for m in MEMBERS}
        for m, items in results.items():
            print(f"| {m} | " + " | ".join("✅" if i.ok else "❌" for i in items) + " |")
        return 0 if all(i.ok for items in results.values() for i in items) else 1
    items = check_member(args.member)
    print(f"Lab 7 — {args.member}\n")
    for it in items:
        print(f"  [{'PASS' if it.ok else 'FAIL'}] {it.task:<24} {it.detail}")
    return 0 if all(i.ok for i in items) else 1


if __name__ == "__main__":
    sys.exit(main())
