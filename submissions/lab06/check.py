"""Lab 6 — self-check for an individual submission (run before sending the PR link to the LMS).

    python submissions/lab06/check.py long_th        # one member, detailed
    python submissions/lab06/check.py --all          # every member, one line each (Tech Lead)

Checks T1 (mini search tests), T4 (comparison output + 3 sentences), T5 (5 H1 cases in your id range,
valid chunk ids, re-run output + 1 sentence), T6 (5-line reflection) and repo hygiene. A1/A2 live in
``lab06/starter``; their tests are reported once for information. Exit code 0 = every required item passes.
Works with any Python that has the starter's requirements installed (the root .venv is fine).
"""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STARTER = ROOT / "lab06" / "starter"
PRACTICE = ROOT / "lab06" / "practice"
COMPARE = STARTER / "eval" / "compare_paths.py"

# Member order = "Member 1..7" in the lab sheet's id table (Member 1 = Tech Lead).
MEMBERS = ["long_th", "vy_th", "truyen_lp", "nhat_npm", "nhat_dm", "han_htg", "dieu_sp"]
ID_RANGES = {m: range(21 + 5 * i, 26 + 5 * i) for i, m in enumerate(MEMBERS)}
FORBIDDEN = {".env", ".venv", "venv", "school.db", "assistant.db"}
REFLECTION_KEYWORDS = ("grounding", "min_score", "threshold", "ngưỡng", "cite", "citation", "trích", "nguồn")
PATH_LINE = re.compile(r"^(?P<path>deterministic|retrieval|llm \([^)]*\))\s+(?P<ok>\d+)/(?P<n>\d+).*?fails:(?P<fails>.*)$")


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


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


# --- T1 ---------------------------------------------------------------------------------------------


def check_t1(folder: Path) -> Item:
    test, impl = folder / "test_mini_search.py", folder / "mini_search.py"
    if not impl.exists() or not test.exists():
        return Item("T1 mini search", False, 0, 2, "mini_search.py / test_mini_search.py missing (copy from lab06/practice/)")
    if not filecmp.cmp(test, PRACTICE / "test_mini_search.py", shallow=False):
        return Item("T1 mini search", False, 0, 2, "test_mini_search.py was edited; restore it from lab06/practice/")
    proc = run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_mini_search.py"], folder)
    m = re.search(r"(\d+) passed", proc.stdout)
    passed = int(m.group(1)) if m else 0
    ok = proc.returncode == 0 and passed == 4
    return Item("T1 mini search", ok, 2 if ok else 0, 2, f"{passed}/4 passed")


# --- T5 cases ----------------------------------------------------------------------------------------


def compare(case_file: Path | None = None) -> tuple[dict[str, tuple[int, int, set[str]]], str]:
    """Run the starter's compare_paths.py; return {path: (correct, total, failed ids)} and any error text."""
    cmd = [sys.executable, str(COMPARE)] + ([str(case_file)] if case_file else [])
    proc = run(cmd, STARTER)
    rows = {}
    for line in proc.stdout.splitlines():
        if m := PATH_LINE.match(line.strip()):
            rows[m["path"]] = (int(m["ok"]), int(m["n"]), set(m["fails"].split()))
    if proc.returncode != 0 or not rows:
        err = (proc.stderr.strip().splitlines() or proc.stdout.strip().splitlines() or ["compare_paths failed"])[-1]
        return rows, err
    return rows, ""


def check_h1_cases(member: str, folder: Path) -> tuple[Item, list[dict], dict]:
    name, path = "T5 H1 cases", folder / "h1_cases.jsonl"
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return Item(name, False, 0, 2, f"h1_cases.jsonl is empty — add 5 cases with ids {id_range_label(member)}"), [], {}
    try:
        cases = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except json.JSONDecodeError as exc:
        return Item(name, False, 0, 2, f"h1_cases.jsonl: not valid JSON ({exc.msg}, line {exc.lineno})"), [], {}
    if not all(isinstance(c, dict) for c in cases):
        return Item(name, False, 0, 2, "h1_cases.jsonl: every line must be a JSON object"), [], {}
    problems = []
    if len(cases) != 5:
        problems.append(f"{len(cases)} cases (need exactly 5)")
    ids = [str(c.get("id", "")) for c in cases]
    bad_ids = [i for i in ids if not (re.fullmatch(r"E\d+", i) and int(i[1:]) in ID_RANGES[member])]
    if bad_ids:
        problems.append(f"ids {', '.join(bad_ids) or '(missing)'} outside your range {id_range_label(member)}")
    normal = [c for c in cases if "expect_source" in c]
    abstain = [c for c in cases if c.get("expect_abstain") is True]
    if len(normal) != 3 or len(abstain) != 2:
        problems.append(f"{len(normal)} expect_source + {len(abstain)} expect_abstain (need 3 + 2)")
    rows, err = compare(path)  # also validates JSON shape, duplicate ids and chunk ids
    if err:
        problems.append(err)
    if problems:
        return Item(name, False, 0, 2, "; ".join(problems)), cases, rows
    tip = ""
    if not {"out-of-scope", "privacy", "other-person"} & {c.get("category") for c in abstain}:
        tip = " · tip: label the abstain cases 'out-of-scope' and 'privacy'"
    return Item(name, True, 2, 2, f"5 cases, ids OK, chunk ids exist{tip}"), cases, rows


# --- T4 / T5 markdown ---------------------------------------------------------------------------------


def _filled(line: str) -> bool:
    body = line.split(":", 1)[-1].strip()
    return bool(body) and "TODO" not in body


def check_comparison(folder: Path) -> tuple[Item, Item]:
    path = folder / "path_comparison.md"
    if not path.exists():
        return Item("T4 comparison", False, 0, 1, "path_comparison.md missing"), Item(
            "T5 re-run output", False, 0, 0, "path_comparison.md missing"
        )
    t4, _, t5 = path.read_text(encoding="utf-8").partition("## T5")

    t4_problems = []
    if not re.search(r"^retrieval\s+\d+/20", t4, re.M):
        t4_problems.append("paste the output of `python eval/compare_paths.py` (the 20-case table)")
    abc = {k: next((ln for ln in t4.splitlines() if ln.strip().startswith(f"({k})")), "") for k in "abc"}
    unfilled = [k for k, ln in abc.items() if not _filled(ln)]
    if unfilled:
        t4_problems.append(f"sentence(s) ({')('.join(unfilled)}) not written")
    elif not re.search(r"E1[345]|E19", abc["c"]):
        t4_problems.append("(c) must name one of E13, E14, E15, E19")
    t4_item = Item(
        "T4 comparison", not t4_problems, 0 if t4_problems else 1, 1, "; ".join(t4_problems) or "table + 3 sentences"
    )

    t5_problems = []
    if not re.search(r"^retrieval\s+\d+/25", t5, re.M):
        t5_problems.append("paste the re-run output with your 5 cases (the 25-case table)")
    why = next((ln for ln in t5.splitlines() if ln.strip().lower().startswith("why")), "")
    if not _filled(why):
        t5_problems.append("write the 1 sentence after 'Why …:'")
    t5_item = Item("T5 re-run output", not t5_problems, 0, 0, "; ".join(t5_problems) or "table + explanation")
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
    found = {p.name for p in folder.iterdir() if p.name in FORBIDDEN or p.suffix == ".db"}
    tracked = run(["git", "ls-files", "--", str(folder)], ROOT).stdout.split()
    found |= {Path(t).name for t in tracked if Path(t).name in FORBIDDEN or t.endswith(".db")}
    return Item("hygiene", not found, 0, 0, f"remove: {', '.join(sorted(found))}" if found else "no .env / .venv / *.db")


def check_bonus(folder: Path) -> Item:
    path = folder / "bonus.md"
    done = path.exists() and "TODO" not in path.read_text(encoding="utf-8")
    return Item("T7 bonus", done, 1 if done else 0, 0, "written" if done else "optional — not done", required=False)


# --- driver -----------------------------------------------------------------------------------------


def check_member(member: str, verbose: bool = True) -> list[Item]:
    folder = HERE / member
    if not folder.is_dir():
        raise SystemExit(f"no folder {folder}")
    h1, cases, rows = check_h1_cases(member, folder)
    t4, t5_table = check_comparison(folder)
    items = [check_t1(folder), t4, h1, t5_table, check_reflection(folder), check_hygiene(folder), check_bonus(folder)]
    if verbose:
        print(f"Lab 6 — {member}  (H1 ids {id_range_label(member)})\n")
        for it in items:
            mark = "PASS" if it.ok else ("----" if not it.required else "FAIL")
            pts = f"{it.points:g}/{it.max_points:g}" if it.max_points else ""
            print(f"  [{mark}] {it.task:<17} {pts:>5}  {it.detail}")
        if cases and rows:
            print("\n  Your H1 cases on each path:")
            for c in cases:
                cells = " ".join(f"{p.split()[0]}={'❌' if c.get('id') in f else '✅'}" for p, (_, _, f) in rows.items())
                expected = "abstain" if c.get("expect_abstain") else c.get("expect_source", c.get("expect_contains"))
                print(f"    {c.get('id')} [{expected}] {cells}  — {c.get('question')}")
        got = sum(i.points for i in items)
        print(f"\n  Individual points found by this script: {got:g}/6  (+ A1/A2 4 pts in lab06/starter, + bonus)")
    return items


def team_tests() -> str:
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_rag.py", "-k", "citation or abstain"]
    proc = run(cmd, STARTER)
    out = proc.stdout.strip().splitlines() or proc.stderr.strip().splitlines() or ["(no output)"]
    return out[-1]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("member", nargs="?", choices=MEMBERS)
    ap.add_argument("--all", action="store_true", help="summarise every member")
    args = ap.parse_args(argv)
    if not args.member and not args.all:
        ap.error("give a member name or --all")

    print(f"A1/A2 (lab06/starter tests/test_rag.py -k 'citation or abstain'): {team_tests()}\n")
    if args.all:
        all_ok = True
        print("| member | T1 | T4 | T5 cases | T5 output | T6 | hygiene | bonus |")
        print("|---" * 8 + "|")
        for m in MEMBERS:
            items = check_member(m, verbose=False)
            all_ok &= all(i.ok for i in items if i.required)
            print(f"| {m} | " + " | ".join("✅" if i.ok else ("·" if not i.required else "❌") for i in items) + " |")
        return 0 if all_ok else 1
    items = check_member(args.member)
    return 0 if all(i.ok for i in items if i.required) else 1


if __name__ == "__main__":
    sys.exit(main())
