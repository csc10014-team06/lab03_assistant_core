"""Lab 6 — eval harness (T4/T5), the 3-path service API and the CLI ``--path`` flag."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from assistant_core.cli import build_service, main
from assistant_core.config import Settings, load_settings
from assistant_core.evaluation import (
    Case,
    CaseError,
    build_runners,
    case_table,
    load_cases,
    parse_case,
    run_eval,
    summary_table,
)
from assistant_core.rag.index import KBIndex

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval" / "cases.jsonl"


@pytest.fixture(scope="module")
def index() -> KBIndex:
    return KBIndex.from_dir(Settings().kb_dir)


@pytest.fixture(scope="module")
def reports(index):
    settings = load_settings({})
    cases = load_cases([CASES], index)
    return run_eval(cases, build_runners(settings, index=index), index.alias_map())


# --- case files -------------------------------------------------------------------------------------


def test_base_cases_are_valid(index):
    cases = load_cases([CASES], index)
    assert [c.id for c in cases] == [f"E{i:02d}" for i in range(1, 21)]
    assert sum(c.expect_abstain for c in cases) == 5


@pytest.mark.parametrize(
    ("line", "match"),
    [
        ("not json", "not valid JSON"),
        ("[1]", "JSON object"),
        ('{"question": "q", "expect_abstain": true}', "missing 'id'"),
        ('{"id": "E1", "expect_abstain": true}', "missing 'question'"),
        ('{"id": "E1", "question": "q"}', "exactly one"),
        ('{"id": "E1", "question": "q", "expect_source": "S26#1", "expect_abstain": true}', "exactly one"),
        ('{"id": "E1", "question": "q", "expect_source": "S99#1"}', "not a chunk id"),
    ],
)
def test_parse_case_rejects_bad_lines(index, line, match):
    with pytest.raises(CaseError, match=match):
        parse_case(line, "f:1", index)


def test_load_cases_rejects_duplicate_ids_across_files(tmp_path, index):
    extra = tmp_path / "h1.jsonl"
    extra.write_text('{"id": "E02", "question": "q", "expect_abstain": true}\n', encoding="utf-8")
    with pytest.raises(CaseError, match="duplicate id E02"):
        load_cases([CASES, extra], index)


# --- metrics on the base set (the numbers the lab sheet expects) --------------------------------------


def test_retrieval_and_llm_stub_pass_16_of_20(reports):
    for path in ("retrieval", "llm"):
        assert reports[path].passed == 16
        assert [r.case.id for r in reports[path].failures] == ["E13", "E14", "E15", "E19"]


def test_rules_path_is_worse_than_retrieval(reports):
    assert reports["rules"].passed < reports["retrieval"].passed


def test_metrics_breakdown(reports):
    d = reports["retrieval"].as_dict()
    assert (d["source_hits"], d["normal_cases"]) == (12, 15)
    assert (d["abstain_hits"], d["abstain_cases"]) == (4, 5)
    assert (d["false_abstains"], d["wrong_sources"], d["grounding_rejections"]) == (2, 1, 0)


def test_rules_sources_are_mapped_through_aliases(reports):
    e09 = next(r for r in reports["rules"].results if r.case.id == "E09")
    assert e09.got_sources == ("H26#1",) and e09.passed


def test_tables_render(reports):
    table = summary_table(reports)
    assert "| retrieval | 16/20 | 80% |" in table and "llm (stub)" in table
    assert "| E02 | normal | I lost my student card | S26#3 |" in case_table(reports)


def test_run_eval_measures_latency_with_injected_clock(index):
    ticks = iter([0.0, 0.5])
    case = Case(id="X", question="I lost my student card", expect_source="S26#3")
    out = run_eval([case], build_runners(load_settings({}), index=index), {}, ["llm"], clock=lambda: next(ticks))
    assert out["llm"].results[0].latency_ms == 500.0


def test_compare_paths_script_writes_reports_and_gates(tmp_path):
    out, js = tmp_path / "table.md", tmp_path / "m.json"
    script = ROOT / "eval" / "compare_paths.py"
    ok = subprocess.run(
        [sys.executable, str(script), "--out", str(out), "--json", str(js), "--min-pass", "retrieval=16"],
        capture_output=True, text=True, cwd=tmp_path, check=False,
    )
    assert ok.returncode == 0, ok.stderr
    assert "| retrieval | 16/20 |" in out.read_text(encoding="utf-8")
    assert json.loads(js.read_text(encoding="utf-8"))["paths"]["llm"]["passed"] == 16

    gated = subprocess.run(
        [sys.executable, str(script), "--paths", "retrieval", "--min-pass", "retrieval=20"],
        capture_output=True, text=True, cwd=tmp_path, check=False,
    )
    assert gated.returncode == 1 and "EVAL GATE FAILED" in gated.stderr


# --- service.ask and CLI ------------------------------------------------------------------------------


@pytest.fixture
def service():
    return build_service(load_settings({}))


def test_ask_rules_path_equals_respond(service):
    resp = service.ask("I lost my student card", "rules")
    assert resp.path == "rules" and resp.sources[0].id == "H26-4.2"  # the keyword rule picks the wrong rule


def test_ask_llm_path_answers_from_kb(service):
    resp = service.ask("I lost my student card", "llm")
    assert resp.path == "llm" and resp.sources[0].id == "S26#3"


def test_ask_keeps_fee_and_office_on_rules(service):
    assert service.ask("tuition 10 credits", "llm").answer == "Your tuition is 4,500,000 VND."
    assert service.ask("where is the library", "retrieval").answer.startswith("Library: room B.201")


def test_ask_without_kb_falls_back_to_rules(tmp_path):
    settings = Settings(data_dir=tmp_path)  # no kb/ folder (and no offices/handbook)
    svc = build_service(settings)
    assert svc.ask("I lost my student card", "llm").path == "rules"


def test_cli_default_path_answers_with_source(capsys):
    assert main(["I lost my student card"]) == 0
    assert "(source: S26#3)" in capsys.readouterr().out


def test_cli_abstains_and_points_to_training_office(capsys):
    assert main(["what is the capital of France"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("Sorry") and "Training Office" in out


def test_cli_rules_path_is_unchanged(capsys):
    assert main(["--path", "rules", "I lost my student card"]) == 0
    assert "(source: H26-4.2)" in capsys.readouterr().out
