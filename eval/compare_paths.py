"""Compare the three answering paths (rules / retrieval / llm) on the eval cases.  Lab 6 — T4 / T5.

Run from the repository root (offline, no API key; the llm path uses the stub by default):

    python eval/compare_paths.py                                   # base 20 cases
    python eval/compare_paths.py --cases eval/cases.jsonl submissions/lab06/long_th/h1_cases.jsonl
    python eval/compare_paths.py --include-submissions             # base + every member's H1 cases
    python eval/compare_paths.py --out docs/lab6/path_comparison_table.md --json eval/results.json
    python eval/compare_paths.py --min-pass retrieval=16 --min-pass llm=16   # exit 1 below (CI gate)
    LLM_PROVIDER=ollama LLM_MODEL=llama3.2 python eval/compare_paths.py      # bonus T7
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # works without ``pip install -e .`` too

from dotenv import load_dotenv  # noqa: E402

from assistant_core.config import load_settings  # noqa: E402
from assistant_core.evaluation import (  # noqa: E402
    PATHS,
    CaseError,
    build_runners,
    load_cases,
    markdown_report,
    run_eval,
)
from assistant_core.llm import make_draft_provider  # noqa: E402
from assistant_core.rag.index import KBIndex  # noqa: E402

DEFAULT_CASES = ROOT / "eval" / "cases.jsonl"
SUBMISSIONS_GLOB = "submissions/lab06/*/h1_cases.jsonl"


def parse_min_pass(values: list[str]) -> dict[str, int]:
    gates: dict[str, int] = {}
    for item in values:
        path, _, num = item.partition("=")
        if path not in PATHS or not num.isdigit():
            raise SystemExit(f"--min-pass expects PATH=N with PATH in {PATHS}, got {item!r}")
        gates[path] = int(num)
    return gates


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", nargs="+", type=Path, default=[DEFAULT_CASES], help="JSONL case files")
    ap.add_argument("--include-submissions", action="store_true", help=f"also load {SUBMISSIONS_GLOB}")
    ap.add_argument("--paths", default=",".join(PATHS), help="comma-separated subset of rules,retrieval,llm")
    ap.add_argument("--out", type=Path, help="also write the Markdown report to this file")
    ap.add_argument("--json", type=Path, help="also write machine-readable metrics to this file")
    ap.add_argument("--min-pass", action="append", default=[], metavar="PATH=N", help="fail if PATH passes < N")
    args = ap.parse_args(argv)

    load_dotenv(ROOT / ".env", override=False)
    settings = load_settings()
    paths = [p.strip() for p in args.paths.split(",") if p.strip()]
    if unknown := set(paths) - set(PATHS):
        ap.error(f"unknown path(s): {', '.join(sorted(unknown))}")
    gates = parse_min_pass(args.min_pass)

    case_files = list(args.cases)
    if args.include_submissions:
        case_files += sorted(p for p in ROOT.glob(SUBMISSIONS_GLOB) if p.read_text(encoding="utf-8").strip())

    index = KBIndex.from_dir(settings.kb_dir)
    try:
        cases = load_cases(case_files, index)
    except (CaseError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    provider = make_draft_provider(settings.llm_provider, settings.llm_model, settings.ollama_url)
    runners = build_runners(settings, provider, index)
    reports = run_eval(cases, runners, index.alias_map(), paths)
    report = markdown_report(reports, provider.name, settings, len(cases))

    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report + "\n", encoding="utf-8")
    if args.json:
        payload = {
            "provider": provider.name,
            "min_score": settings.retrieval_min_score,
            "k": settings.retrieval_k,
            "case_files": [str(p) for p in case_files],
            "paths": {p: r.as_dict() for p, r in reports.items()},
        }
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    failed_gates = [
        f"{p}: {reports[p].passed} < {n}" for p, n in gates.items() if p in reports and reports[p].passed < n
    ]
    if failed_gates:
        print("\nEVAL GATE FAILED — " + "; ".join(failed_gates), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
