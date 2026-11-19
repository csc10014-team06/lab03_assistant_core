"""Lab 6 — self-check for an individual submission (run before sending the PR link to the LMS).

    python submissions/lab06/check.py long_th        # one member, detailed
    python submissions/lab06/check.py --all          # every member, one line each (Tech Lead)

Checks T1 (mini search tests), T4 (comparison table + 3 sentences), T5 (5 H1 cases in your id
range, valid chunk ids, re-run table + 1 sentence), T6 (5-line reflection), and repo hygiene.
A1/A2 are team code in ``assistant_core/``; their tests are reported once for information.
Exit code 0 = every required item passes.
"""
from __future__ import annotations

import argparse
import filecmp
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from assistant_core.config import load_settings  # noqa: E402
from assistant_core.evaluation import CaseError, build_runners, load_cases, run_eval  # noqa: E402
from assistant_core.rag.index import KBIndex  # noqa: E402

# Member order = "Member 1..7" in the lab sheet's id table (Member 1 = Tech Lead).
MEMBERS = ["long_th", "vy_th", "truyen_lp", "nhat_npm", "nhat_dm", "han_htg", "dieu_sp"]
ID_RANGES = {m: range(21 + 5 * i, 26 + 5 * i) for i, m in enumerate(MEMBERS)}
BASE_CASES = ROOT / "eval" / "cases.jsonl"
FORBIDDEN = (".env", ".venv", "venv", "school.db", "assistant.db")
REFLECTION_KEYWORDS = ("grounding", "min_score", "threshold", "ngưỡng", "cite", "citation", "trích", "nguồn")


@dataclass
class Item:
    task: str
    ok: bool
    points: float
    max_points: float
    detail: str
    required: bool = True


def id_range_label(member: str) -> str:
    r = ID_RANGES[member]
    return f"E{r.start}–E{r.stop - 1}"


# --- T1 -----------------------------------------------------------------------------------------


def check_t1(folder: Path) -> Item:
    test, impl = folder / "test_mini_search.py", folder / "mini_search.py"
    if not impl.exists() or not test.exists():
        return Item("T1 mini search", False, 0, 2, "mini_search.py / test_mini_search.py missing (copy from _practice/)")
    if not filecmp.cmp(test, HERE / "_practice" / "test_mini_search.py", shallow=False):
        return Item("T1 mini search", False, 0, 2, "test_mini_search.py was edited; restore it from _practice/")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_mini_search.py"],
        cwd=folder, capture_output=True, text=True, check=False,
    )
    m = re.search(r"(\d+) passed", proc.stdout)
    passed = int(m.group(1)) if m else 0
    ok = proc.returncode == 0 and passed == 4
    return Item("T1 mini search", ok, 2 if ok else 0, 2, f"{passed}/4 passed")


# --- T5 (cases) ---------------------------------------------------------------------------------


def check_h1_cases(member: str, folder: Path, index: KBIndex) -> tuple[Item, list]:
    path = folder / "h1_cases.jsonl"
    name = "T5 H1 cases"
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return Item(name, False, 0, 2, f"h1_cases.jsonl is empty — add 5 cases with ids {id_range_label(member)}"), []
    try:
        cases = load_cases([BASE_CASES, path], index)[20:]
    except CaseError as exc:
        return Item(name, False, 0, 2, str(exc)), []
    problems: list[str] = []
    if len(cases) != 5:
        problems.append(f"{len(cases)} cases (need exactly 5)")
    out_of_range = [c.id for c in cases if not (re.fullmatch(r"E\d+", c.id) and int(c.id[1:]) in ID_RANGES[member])]
    if out_of_range:
        problems.append(f"ids {', '.join(out_of_range)} outside your range {id_range_label(member)}")
    normal = [c for c in cases if not c.expect_abstain]
    abstain = [c for c in cases if c.expect_abstain]
    if len(normal) != 3 or len(abstain) != 2:
        problems.append(f"{len(normal)} normal + {len(abstain)} abstain (need 3 + 2)")
    cats = {c.category for c in abstain}
    warn = ""
    if abstain and not ({"out-of-scope", "other-person"} <= cats):
        warn = " · tip: give the abstain cases category 'out-of-scope' and 'other-person'"
    if problems:
        return Item(name, False, 0, 2, "; ".join(problems)), cases
    return Item(name, True, 2, 2, f"5 cases, ids OK, chunk ids exist{warn}"), cases


# --- T4 / T5 (markdown) ---------------------------------------------------------------------------


def _filled(line: str) -> bool:
    body = line.split(":", 1)[-1].strip()
    return bool(body) and "TODO" not in body


def check_comparison(folder: Path) -> tuple[Item, Item]:
    path = folder / "path_comparison.md"
    if not path.exists():
        missing = "path_comparison.md missing"
        return Item("T4 comparison", False, 0, 1, missing), Item("T5 re-run table", False, 0, 0, missing)
    text = path.read_text(encoding="utf-8")
    t4, _, t5 = text.partition("## T5")

    t4_problems = []
    if "Cases: 20" not in t4 or "| retrieval |" not in t4:
        t4_problems.append("paste the table from `python eval/compare_paths.py` (with its 'Cases: 20' line)")
    abc = {k: next((ln for ln in t4.splitlines() if ln.strip().startswith(f"({k})")), "") for k in "abc"}
    unfilled = [k for k, ln in abc.items() if not _filled(ln)]
    if unfilled:
        t4_problems.append(f"sentence(s) ({')('.join(unfilled)}) not written")
    if abc["c"] and not re.search(r"E1[345]|E19", abc["c"]):
        t4_problems.append("(c) must name one of E13, E14, E15, E19")
    t4_item = Item("T4 comparison", not t4_problems, 0 if t4_problems else 1, 1, "; ".join(t4_problems) or "table + 3 sentences")

    t5_problems = []
    if "Cases: 25" not in t5:
        t5_problems.append("paste the re-run table with your 5 cases ('Cases: 25')")
    why = next((ln for ln in t5.splitlines() if ln.strip().lower().startswith("why")), "")
    if not _filled(why):
        t5_problems.append("write the 1 sentence after 'Why …:'")
    t5_item = Item("T5 re-run table", not t5_problems, 0, 0, "; ".join(t5_problems) or "table + explanation")
    return t4_item, t5_item


def check_reflection(folder: Path) -> Item:
    path = folder / "reflection.md"
    if not path.exists():
        return Item("T6 reflection", False, 0, 1, "reflection.md missing")
    m = re.search(r"<!-- reflection:start -->(.*?)<!-- reflection:end -->", path.read_text(encoding="utf-8"), re.S)
    lines = [ln for ln in (m.group(1) if m else "").splitlines() if ln.strip()]
    problems = []
    if len(lines) != 5:
        problems.append(f"{len(lines)} lines between the markers (need exactly 5)")
    if any("TODO" in ln for ln in lines):
        problems.append("replace the TODO lines")
    if not any(k in " ".join(lines).lower() for k in REFLECTION_KEYWORDS):
        problems.append("mention something our code checks and the model does not (grounding check / min_score)")
    return Item("T6 reflection", not problems, 0 if problems else 1, 1, "; ".join(problems) or "5 lines")


def check_hygiene(folder: Path) -> Item:
    found = [p.name for p in folder.iterdir() if p.name in FORBIDDEN or p.suffix == ".db"]
    tracked = subprocess.run(
        ["git", "ls-files", "--", str(folder)], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.split()
    bad_tracked = [t for t in tracked if Path(t).name in FORBIDDEN or t.endswith(".db")]
    bad = sorted(set(found) | set(bad_tracked))
    return Item("hygiene", not bad, 0, 0, f"remove: {', '.join(bad)}" if bad else "no .env / .venv / *.db")


def check_bonus(folder: Path) -> Item:
    path = folder / "bonus.md"
    done = path.exists() and "TODO" not in path.read_text(encoding="utf-8")
    return Item("T7 bonus", done, 1 if done else 0, 0, "written" if done else "optional — not done", required=False)


# --- driver -------------------------------------------------------------------------------------


def eval_member_cases(cases: list, index: KBIndex) -> list[str]:
    settings = load_settings({})
    reports = run_eval(cases, build_runners(settings, index=index), index.alias_map())
    rows = []
    for i, case in enumerate(cases):
        cells = " ".join(f"{p}={'✅' if reports[p].results[i].passed else '❌'}" for p in reports)
        rows.append(f"    {case.id} [{case.expected}] {cells}  — {case.question}")
    return rows


def check_member(member: str, index: KBIndex, verbose: bool = True) -> list[Item]:
    folder = HERE / member
    if not folder.is_dir():
        raise SystemExit(f"no folder {folder}")
    t1 = check_t1(folder)
    h1, cases = check_h1_cases(member, folder, index)
    t4, t5_table = check_comparison(folder)
    items = [t1, t4, h1, t5_table, check_reflection(folder), check_hygiene(folder), check_bonus(folder)]
    if verbose:
        print(f"Lab 6 — {member}  (H1 ids {id_range_label(member)})\n")
        for it in items:
            mark = "PASS" if it.ok else ("----" if not it.required else "FAIL")
            pts = f"{it.points:g}/{it.max_points:g}" if it.max_points else ""
            print(f"  [{mark}] {it.task:<16} {pts:>5}  {it.detail}")
        if cases:
            print("\n  Your H1 cases on each path:")
            print("\n".join(eval_member_cases(cases, index)))
        got = sum(i.points for i in items)
        print(f"\n  Individual points found by this script: {got:g}/6  (+ A1/A2 4 pts in team code, + bonus)")
    return items


def team_tests() -> str:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_rag.py", "-k", "citation or abstain"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    last = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else proc.stderr.strip()
    return last


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("member", nargs="?", choices=MEMBERS)
    ap.add_argument("--all", action="store_true", help="summarise every member")
    args = ap.parse_args(argv)
    if not args.member and not args.all:
        ap.error("give a member name or --all")

    index = KBIndex.from_dir(load_settings({}).kb_dir)
    print(f"A1/A2 team tests (tests/test_rag.py -k 'citation or abstain'): {team_tests()}\n")

    if args.all:
        all_ok = True
        print(f"| member | {' | '.join(['T1', 'T4', 'T5 cases', 'T5 table', 'T6', 'hygiene', 'bonus'])} |")
        print("|---" * 8 + "|")
        for m in MEMBERS:
            items = check_member(m, index, verbose=False)
            all_ok &= all(i.ok for i in items if i.required)
            print(f"| {m} | " + " | ".join("✅" if i.ok else ("·" if not i.required else "❌") for i in items) + " |")
        return 0 if all_ok else 1

    items = check_member(args.member, index)
    return 0 if all(i.ok for i in items if i.required) else 1


if __name__ == "__main__":
    sys.exit(main())
