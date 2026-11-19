"""evaluation.py — score the three answering paths (rules / retrieval / llm) on eval cases.

Lab 6 (T4/T5). Used by ``eval/compare_paths.py`` and ``submissions/lab06/check.py``.

A case is one JSON object per line::

    {"id": "E02", "question": "I lost my student card", "expect_source": "S26#3", "category": "normal"}
    {"id": "E16", "question": "what is the capital of France", "expect_abstain": true, "category": "out-of-scope"}

Pass rules
----------
* ``expect_source`` case: the path answered (did not abstain) **and** cited that chunk.
  The rules path cites ``handbook.json`` ids; they are mapped to KB chunks through ``Alias:``.
* ``expect_abstain`` case: the path said "I don't know" (rules: intent ``unknown``;
  retrieval / llm: ``path == "abstain"``).
"""
from __future__ import annotations

import json
import statistics
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from assistant_core.config import Settings
from assistant_core.data_loader import load_handbook, load_offices
from assistant_core.llm import DraftProvider, FakeLLM, make_draft_provider
from assistant_core.models import Intent, Message, Response
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.index import KBIndex
from assistant_core.service import AssistantService

PATHS = ("rules", "retrieval", "llm")


class CaseError(ValueError):
    """An eval case file is malformed."""


@dataclass(frozen=True)
class Case:
    id: str
    question: str
    expect_source: str | None = None
    expect_abstain: bool = False
    category: str = "normal"
    origin: str = ""

    @property
    def expected(self) -> str:
        return "abstain" if self.expect_abstain else str(self.expect_source)


@dataclass(frozen=True)
class CaseResult:
    case: Case
    path: str
    passed: bool
    abstained: bool
    got_sources: tuple[str, ...]
    degraded: bool
    latency_ms: float

    @property
    def got(self) -> str:
        if self.abstained:
            return "abstain"
        return ",".join(self.got_sources) or "(no source)"


@dataclass
class PathReport:
    path: str
    results: list[CaseResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(r.passed for r in self.results)

    @property
    def accuracy(self) -> float:
        return self.passed / self.total if self.total else 0.0

    def _normal(self) -> list[CaseResult]:
        return [r for r in self.results if not r.case.expect_abstain]

    def _abstain(self) -> list[CaseResult]:
        return [r for r in self.results if r.case.expect_abstain]

    @property
    def source_hits(self) -> tuple[int, int]:
        normal = self._normal()
        return sum(r.passed for r in normal), len(normal)

    @property
    def false_abstains(self) -> int:
        return sum(r.abstained for r in self._normal())

    @property
    def wrong_sources(self) -> int:
        return sum((not r.abstained) and not r.passed for r in self._normal())

    @property
    def abstain_hits(self) -> tuple[int, int]:
        cases = self._abstain()
        return sum(r.passed for r in cases), len(cases)

    @property
    def grounding_rejections(self) -> int:
        return sum(r.degraded for r in self.results)

    @property
    def mean_latency_ms(self) -> float:
        return statistics.fmean(r.latency_ms for r in self.results) if self.results else 0.0

    @property
    def failures(self) -> list[CaseResult]:
        return [r for r in self.results if not r.passed]

    def as_dict(self) -> dict[str, object]:
        hit, normal = self.source_hits
        ab_hit, ab_total = self.abstain_hits
        return {
            "path": self.path,
            "passed": self.passed,
            "total": self.total,
            "accuracy": round(self.accuracy, 3),
            "source_hits": hit,
            "normal_cases": normal,
            "abstain_hits": ab_hit,
            "abstain_cases": ab_total,
            "false_abstains": self.false_abstains,
            "wrong_sources": self.wrong_sources,
            "grounding_rejections": self.grounding_rejections,
            "mean_latency_ms": round(self.mean_latency_ms, 2),
            "failed_ids": [r.case.id for r in self.failures],
        }


# ---------------------------------------------------------------------------
# Loading cases
# ---------------------------------------------------------------------------


def load_cases(paths: Iterable[Path], index: KBIndex | None = None) -> list[Case]:
    """Read and validate JSONL case files (ids must be unique across *all* files)."""
    cases: list[Case] = []
    seen: dict[str, str] = {}
    for path in paths:
        path = Path(path)
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            where = f"{path}:{lineno}"
            case = parse_case(line, where, index)
            if case.id in seen:
                raise CaseError(f"{where}: duplicate id {case.id} (first in {seen[case.id]})")
            seen[case.id] = where
            cases.append(case)
    return cases


def parse_case(line: str, where: str = "<case>", index: KBIndex | None = None) -> Case:
    try:
        obj = json.loads(line)
    except json.JSONDecodeError as exc:
        raise CaseError(f"{where}: not valid JSON ({exc.msg})") from None
    if not isinstance(obj, dict):
        raise CaseError(f"{where}: each line must be a JSON object")
    cid, question = obj.get("id"), obj.get("question")
    if not isinstance(cid, str) or not cid.strip():
        raise CaseError(f"{where}: missing 'id'")
    if not isinstance(question, str) or not question.strip():
        raise CaseError(f"{where}: {cid} missing 'question'")
    source = obj.get("expect_source")
    abstain = obj.get("expect_abstain", False) is True
    if bool(source) == abstain:
        raise CaseError(f"{where}: {cid} needs exactly one of 'expect_source' or '\"expect_abstain\": true'")
    if source is not None and index is not None and source not in index:
        raise CaseError(f"{where}: {cid} expect_source {source!r} is not a chunk id in data/kb/")
    return Case(
        id=cid,
        question=question,
        expect_source=source,
        expect_abstain=abstain,
        category=str(obj.get("category", "normal")),
        origin=where.rsplit(":", 1)[0],
    )


# ---------------------------------------------------------------------------
# Running the paths
# ---------------------------------------------------------------------------


Runner = Callable[[str], Response]


def build_runners(
    settings: Settings,
    provider: DraftProvider | None = None,
    index: KBIndex | None = None,
) -> dict[str, Runner]:
    """One callable per path. Each path is measured *on its own* (no fee/office routing)."""
    index = index or KBIndex.from_dir(settings.kb_dir)
    provider = provider or make_draft_provider(settings.llm_provider, settings.llm_model, settings.ollama_url)
    rules_service = AssistantService(
        settings,
        load_offices(settings.offices_path),
        load_handbook(settings.handbook_path),
        FakeLLM("(rules path answer)"),  # the rules path's LLM only rephrases; keep it offline and instant
    )
    answerer = RagAnswerer(index, provider, min_score=settings.retrieval_min_score, k=settings.retrieval_k)
    return {
        "rules": lambda q: rules_service.respond(Message(text=q)),
        "retrieval": lambda q: answerer.answer(q, use_llm=False),
        "llm": lambda q: answerer.answer(q, use_llm=True),
    }


def score(case: Case, path: str, resp: Response, aliases: dict[str, str], latency_ms: float) -> CaseResult:
    abstained = resp.intent == Intent.UNKNOWN if path == "rules" else resp.path == "abstain"
    got = tuple(aliases.get(s.id, s.id) for s in resp.sources)
    passed = abstained if case.expect_abstain else (not abstained and case.expect_source in got)
    return CaseResult(case, path, passed, abstained, got, resp.degraded, latency_ms)


def run_eval(
    cases: Sequence[Case],
    runners: dict[str, Runner],
    aliases: dict[str, str],
    paths: Sequence[str] = PATHS,
    clock: Callable[[], float] = time.perf_counter,
) -> dict[str, PathReport]:
    reports = {p: PathReport(p) for p in paths}
    for case in cases:
        for p in paths:
            start = clock()
            resp = runners[p](case.question)
            elapsed = (clock() - start) * 1000
            reports[p].results.append(score(case, p, resp, aliases, elapsed))
    return reports


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def path_label(path: str, provider_name: str) -> str:
    return f"llm ({provider_name})" if path == "llm" else path


def summary_table(reports: dict[str, PathReport], provider_name: str = "stub") -> str:
    lines = [
        "| path | passed | accuracy | right source (normal) | abstained correctly | false abstain"
        " | wrong source | grounding rejected | mean latency (ms) | failed |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p, r in reports.items():
        hit, normal = r.source_hits
        ab, ab_total = r.abstain_hits
        failed = ", ".join(x.case.id for x in r.failures) or "—"
        lines.append(
            f"| {path_label(p, provider_name)} | {r.passed}/{r.total} | {r.accuracy:.0%} | {hit}/{normal}"
            f" | {ab}/{ab_total} | {r.false_abstains} | {r.wrong_sources} | {r.grounding_rejections}"
            f" | {r.mean_latency_ms:.2f} | {failed} |"
        )
    return "\n".join(lines)


def case_table(reports: dict[str, PathReport]) -> str:
    paths = list(reports)
    header = "| id | category | question | expected | " + " | ".join(paths) + " |"
    lines = [header, "|" + "---|" * (4 + len(paths))]
    rows = zip(*(reports[p].results for p in paths), strict=True)
    for row in rows:
        case = row[0].case
        cells = [f"{'✅' if r.passed else '❌'} {r.got}" for r in row]
        lines.append(f"| {case.id} | {case.category} | {case.question} | {case.expected} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def markdown_report(reports: dict[str, PathReport], provider_name: str, settings: Settings, n_cases: int) -> str:
    return "\n".join(
        [
            f"Cases: {n_cases} · `RETRIEVAL_MIN_SCORE={settings.retrieval_min_score}` · k={settings.retrieval_k}"
            f" · provider: `{provider_name}`",
            "",
            summary_table(reports, provider_name),
            "",
            "<details><summary>Per-case results</summary>",
            "",
            case_table(reports),
            "",
            "</details>",
        ]
    )
