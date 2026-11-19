#!/usr/bin/env python3
"""Compare three assistant paths on eval/cases.jsonl.

deterministic — router + tools only; rule questions are not answered
retrieval     — router + tools + retrieval, quoting the best source (no LLM)
llm           — router + tools + retrieval + LLM with structured output (provider from .env; stub by default)

  python eval/compare_paths.py
  python eval/compare_paths.py ../../submissions/lab06/<member>/h1_cases.jsonl   # + extra case files (H1)
  python eval/compare_paths.py --include-submissions                             # + every member's H1 file
  python eval/compare_paths.py --min-correct 16                                   # exit 1 if retrieval/llm < 16

Team additions (lab03_assistant_core): extra case files, --include-submissions, --min-correct, case validation,
and it can be started from any directory (it switches to lab06/starter and puts src/ first on sys.path).
The table for the base 20 cases is unchanged.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

STARTER = Path(__file__).resolve().parents[1]
REPO = STARTER.parents[1]
sys.path.insert(0, str(STARTER / "src"))  # this starter's assistant_core, even if another one is installed

from assistant_core.config import load_settings  # noqa: E402
from assistant_core.knowledge import Handbook, OfficeDirectory  # noqa: E402
from assistant_core.llm import make_llm  # noqa: E402
from assistant_core.models import Message  # noqa: E402
from assistant_core.rag.answerer import RagAnswerer  # noqa: E402
from assistant_core.rag.chunker import load_folder  # noqa: E402
from assistant_core.rag.index import make_index  # noqa: E402
from assistant_core.responder import TemplateResponder  # noqa: E402
from assistant_core.service import AssistantService  # noqa: E402


class NoAnswer:
    """Deterministic path: never answers from documents."""

    def search(self, query, k=3):
        return []


def correct(case: dict, resp) -> bool:
    if case.get("expect_abstain"):
        return resp.path == "abstain" or resp.intent.value == "unknown"
    if "expect_contains" in case:
        return case["expect_contains"] in resp.answer
    return any(s.id == case["expect_source"] for s in resp.sources)


def load_cases(files: list[Path]) -> list[dict]:
    cases, seen = [], {}
    for f in files:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                c = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{f}:{n}: not valid JSON ({exc.msg})") from None
            if not isinstance(c, dict) or not c.get("id") or not c.get("question"):
                raise SystemExit(f"{f}:{n}: each line needs \"id\" and \"question\"")
            if sum(k in c for k in ("expect_source", "expect_contains", "expect_abstain")) != 1:
                need = "exactly one of expect_source / expect_contains / expect_abstain"
                raise SystemExit(f"{f}:{n}: {c['id']} needs {need}")
            if c["id"] in seen:
                raise SystemExit(f"{f}:{n}: duplicate id {c['id']} (first in {seen[c['id']]})")
            seen[c["id"]] = f"{f}:{n}"
            cases.append(c)
    return cases


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Compare deterministic / retrieval / llm paths on eval cases.")
    ap.add_argument("extra", nargs="*", type=Path, help="extra JSONL case files, e.g. your H1 cases")
    ap.add_argument("--include-submissions", action="store_true", help="add submissions/lab06/*/h1_cases.jsonl")
    ap.add_argument("--min-correct", type=int, metavar="N", help="exit 1 if retrieval or llm get fewer than N right")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    files = [STARTER / "eval" / "cases.jsonl", *(p.resolve() for p in args.extra)]
    if args.include_submissions:
        member_files = REPO.glob("submissions/lab06/*/h1_cases.jsonl")
        files += sorted(p for p in member_files if p.read_text(encoding="utf-8").strip())
    os.chdir(STARTER)  # data/, .env and eval/ are relative to the starter folder
    s = load_settings()
    cases = load_cases(files)
    offices = OfficeDirectory.from_csv(s.data_dir / "offices.csv")
    handbook = Handbook.from_json(s.data_dir / "handbook.json")
    chunks = load_folder(s.kb_dir)
    known = {c.id for c in chunks}
    sourced = [c for c in cases if "expect_source" in c]
    unknown = [f"{c['id']}→{c['expect_source']}" for c in sourced if c["expect_source"] not in known]
    if unknown:
        raise SystemExit(f"expect_source is not a chunk id in {s.kb_dir}: {', '.join(unknown)}")
    if len(files) > 1:
        shown = [str(f.relative_to(REPO)) if f.is_relative_to(REPO) else str(f) for f in files]
        print(f"cases: {len(cases)} from {', '.join(shown)}")
    index = make_index(s.retrieval_kind, chunks)
    provider = s.llm_provider if s.llm_provider != "template" else "stub"
    llm = make_llm(provider, s.llm_model, s.llm_base_url, s.llm_api_key, s.llm_timeout_s)
    paths = {
        "deterministic": RagAnswerer(NoAnswer(), None, s.retrieval_min_score),
        "retrieval": RagAnswerer(index, None, s.retrieval_min_score),
        f"llm ({llm.name})": RagAnswerer(index, llm, s.retrieval_min_score, prompt_version=s.prompt_version),
    }
    print(f"{'path':18} {'correct':>8} {'abstain ok':>11} {'p50 ms':>7} {'max ms':>7}")
    below = []
    for name, rag in paths.items():
        svc = AssistantService(s, offices, handbook, TemplateResponder(), rag)
        ok = abst_ok = abst_total = 0
        lat, fails = [], []
        for c in cases:
            t0 = time.perf_counter()
            r = svc.handle(Message(text=c["question"]))
            lat.append((time.perf_counter() - t0) * 1000)
            good = correct(c, r)
            ok += good
            if c.get("expect_abstain"):
                abst_total += 1
                abst_ok += good
            if not good:
                fails.append(c["id"])
        print(
            f"{name:18} {ok:>5}/{len(cases)} {abst_ok:>7}/{abst_total} {statistics.median(lat):7.1f} {max(lat):7.1f}"
            f"   fails: {' '.join(fails)}"
        )
        if args.min_correct is not None and name != "deterministic" and ok < args.min_correct:
            below.append(f"{name} {ok} < {args.min_correct}")
    if below:
        print("EVAL GATE FAILED: " + "; ".join(below), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
