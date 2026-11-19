"""Lab 6 — retrieval index, grounding check (A2), abstain gate (A1) and draft providers.

``pytest -q tests/test_rag.py -k citation`` runs the A2 tests; ``-k abstain`` the A1 tests.
"""
from __future__ import annotations

import json

import httpx
import pytest

from assistant_core.config import ConfigError, Settings, load_settings
from assistant_core.llm import (
    OllamaLLM,
    ProviderError,
    StubLLM,
    build_prompt,
    make_draft_provider,
    parse_draft,
)
from assistant_core.models import Intent
from assistant_core.rag.answerer import ESCALATE_MSG, RagAnswerer
from assistant_core.rag.index import KBError, KBIndex, parse_kb_markdown, tokenize

KB_DIR = Settings().kb_dir


@pytest.fixture(scope="module")
def index() -> KBIndex:
    return KBIndex.from_dir(KB_DIR)


class ScriptedProvider:
    """Returns a fixed raw reply and counts calls (to prove A1 never reaches the model)."""

    name = "scripted"

    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.calls = 0

    def draft(self, question, hits):
        self.calls += 1
        return self.reply


def reply(answer="ok", source_ids=("S26#3",), abstain=False) -> str:
    return json.dumps({"answer": answer, "source_ids": list(source_ids), "abstain": abstain})


# --- index ---------------------------------------------------------------------------------------


def test_tokenize_lowercases_and_drops_stopwords():
    assert tokenize("I lost MY Student-Card!") == ["lost", "student", "card"]


def test_kb_loads_all_chunks_with_unique_ids(index):
    assert len(index) == 18
    assert "S26#3" in index and "H26#10" in index


def test_kb_aliases_map_handbook_rules(index):
    assert index.alias_map()["H26-7.2"] == "H26#5"
    assert set(index.alias_map()) == {"H26-4.2", "H26-5.3", "H26-5.4", "H26-6.1", "H26-7.2"}


def test_search_lost_student_card_ranks_s26_3_first(index):
    hits = index.search("I lost my student card")
    assert hits[0].chunk_id == "S26#3"
    assert hits[0].score == 3.0


def test_search_out_of_scope_returns_nothing(index):
    assert index.search("what is the capital of France") == []


def test_search_orders_ties_by_id_and_respects_k(index):
    hits = index.search("students", k=50)
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)
    assert [h.chunk_id for h in hits] == sorted(h.chunk_id for h in hits)
    assert len(index.search("students", k=2)) == 2


def test_parse_kb_markdown_reads_alias_and_skips_preamble():
    chunks = parse_kb_markdown("# Title\nintro text\n\n## X#1 First\nAlias: R-1\nBody one.\n## X#2 Second\nBody two.\n")
    assert [(c.id, c.title, c.text, c.alias) for c in chunks] == [
        ("X#1", "First", "Body one.", "R-1"),
        ("X#2", "Second", "Body two.", None),
    ]


def test_parse_kb_markdown_rejects_empty_chunk():
    with pytest.raises(KBError, match="no text"):
        parse_kb_markdown("## X#1 Empty\n\n## X#2 Ok\ntext\n")


def test_kb_rejects_duplicate_ids():
    chunks = parse_kb_markdown("## X#1 A\na\n## X#1 B\nb\n")
    with pytest.raises(KBError, match="duplicate"):
        KBIndex(chunks)


def test_kb_missing_folder_raises(tmp_path):
    with pytest.raises(KBError, match="no \\*.md"):
        KBIndex.from_dir(tmp_path)


# --- A2: grounding check (citation) --------------------------------------------------------------


def test_citation_of_retrieved_chunk_is_accepted():
    draft = parse_draft(reply(source_ids=["S26#3"]), {"S26#3", "S26#4"})
    assert draft.source_ids == ["S26#3"] and not draft.abstain


def test_citation_of_unretrieved_chunk_is_rejected():
    with pytest.raises(ProviderError, match="not retrieved"):
        parse_draft(reply(source_ids=["S26#3", "H26#9"]), {"S26#3"})


def test_citation_missing_is_rejected():
    with pytest.raises(ProviderError, match="not retrieved"):
        parse_draft(reply(source_ids=[]), {"S26#3"})


def test_citation_not_required_when_abstaining():
    assert parse_draft(reply(answer="", source_ids=[], abstain=True), {"S26#3"}).abstain


def test_citation_parse_tolerates_text_around_json():
    raw = "Sure! ```json\n" + reply() + "\n```"
    assert parse_draft(raw, {"S26#3"}).answer == "ok"


@pytest.mark.parametrize("raw", ["", "no json here", "{not json}", '{"answer": 1, "source_ids": "S26#3"}'])
def test_citation_parse_rejects_malformed_reply(raw):
    with pytest.raises(ProviderError):
        parse_draft(raw, {"S26#3"})


def test_citation_parse_rejects_empty_answer():
    with pytest.raises(ProviderError, match="empty"):
        parse_draft(reply(answer="  "), {"S26#3"})


def test_citation_hallucinated_source_is_never_shown(index):
    answerer = RagAnswerer(index, ScriptedProvider(reply(answer="made up", source_ids=["Z99#1"])))
    resp = answerer.answer("I lost my student card")
    assert resp.answer == ESCALATE_MSG
    assert resp.path == "abstain" and resp.escalate and resp.degraded


# --- A1: abstain before calling the model --------------------------------------------------------


def test_abstain_without_calling_model_when_nothing_found(index):
    provider = ScriptedProvider(reply())
    resp = RagAnswerer(index, provider, min_score=2.0).answer("what is the capital of France")
    assert provider.calls == 0
    assert resp.answer == ESCALATE_MSG and "Training Office" in resp.answer
    assert resp.intent == Intent.UNKNOWN and resp.path == "abstain"
    assert resp.escalate is True and resp.confidence == 0.0 and resp.sources == []


def test_abstain_when_top_score_below_min_score(index):
    provider = ScriptedProvider(reply())
    # "card" alone scores 1 < 2.0
    assert RagAnswerer(index, provider, min_score=2.0).answer("card").path == "abstain"
    assert provider.calls == 0


def test_abstain_threshold_is_inclusive(index):
    # "student card" scores exactly 2 on S26#3 / S26#4 -> answered
    resp = RagAnswerer(index, StubLLM(), min_score=2.0).answer("student card")
    assert resp.path == "llm"


def test_abstain_when_model_itself_abstains(index):
    provider = ScriptedProvider(reply(answer="", source_ids=[], abstain=True))
    resp = RagAnswerer(index, provider).answer("I lost my student card")
    assert provider.calls == 1
    assert resp.path == "abstain" and resp.escalate and not resp.degraded


# --- answer paths ---------------------------------------------------------------------------------


def test_llm_path_answers_with_source_s26_3(index):
    resp = RagAnswerer(index, StubLLM()).answer("I lost my student card")
    assert resp.path == "llm" and resp.intent == Intent.RULE
    assert [s.id for s in resp.sources] == ["S26#3"]
    assert resp.sources[0].title == "Lost student card"
    assert "Student Affairs" in resp.answer
    assert resp.confidence == 1.0


def test_retrieval_path_returns_top_chunk_without_model(index):
    provider = ScriptedProvider(reply())
    resp = RagAnswerer(index, provider).answer("I lost my student card", use_llm=False)
    assert provider.calls == 0
    assert resp.path == "retrieval" and resp.answer == index.get("S26#3").text


def test_llm_path_deduplicates_cited_sources(index):
    provider = ScriptedProvider(reply(source_ids=["S26#3", "S26#3", "S26#4"]))
    resp = RagAnswerer(index, provider).answer("I lost my student card")
    assert [s.id for s in resp.sources] == ["S26#3", "S26#4"]


# --- providers ------------------------------------------------------------------------------------


def test_stub_cites_top_hit(index):
    hits = index.search("is health insurance mandatory")
    draft = parse_draft(StubLLM().draft("q", hits), {h.chunk_id for h in hits})
    assert draft.source_ids == ["S26#8"]


def test_prompt_contains_ids_question_and_abstain_rule(index):
    prompt = build_prompt("I lost my student card", index.search("I lost my student card"))
    assert "[S26#3] Lost student card:" in prompt
    assert "Question: I lost my student card" in prompt
    assert '"abstain": true' in prompt and "another person" in prompt


def test_ollama_provider_posts_prompt_and_returns_response(index):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content))
        return httpx.Response(200, json={"response": reply()})

    llm = OllamaLLM(model="llama3.2", client=httpx.Client(transport=httpx.MockTransport(handler)))
    raw = llm.draft("I lost my student card", index.search("I lost my student card"))
    assert parse_draft(raw, {"S26#3"}).answer == "ok"
    assert seen["model"] == "llama3.2" and seen["format"] == "json" and seen["stream"] is False


def test_ollama_connection_error_becomes_provider_error(index):
    def handler(request):
        raise httpx.ConnectError("refused")

    llm = OllamaLLM(client=httpx.Client(transport=httpx.MockTransport(handler)))
    with pytest.raises(ProviderError, match="ollama"):
        llm.draft("q", index.search("student card"))


def test_ollama_down_degrades_to_escalation(index):
    llm = OllamaLLM(client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500))))
    resp = RagAnswerer(index, llm).answer("I lost my student card")
    assert resp.path == "abstain" and resp.degraded


def test_make_draft_provider():
    assert isinstance(make_draft_provider("stub"), StubLLM)
    assert make_draft_provider("OLLAMA", "llama3.2").name == "ollama:llama3.2"
    with pytest.raises(ValueError, match="unknown LLM provider"):
        make_draft_provider("gpt")


# --- settings -------------------------------------------------------------------------------------


def test_rag_settings_defaults():
    s = load_settings({})
    assert (s.answer_path, s.retrieval_min_score, s.retrieval_k, s.llm_provider) == ("llm", 2.0, 3, "stub")


def test_rag_settings_accept_tutorial_unprefixed_names():
    s = load_settings({"LLM_PROVIDER": "ollama", "LLM_MODEL": "qwen2.5", "RETRIEVAL_MIN_SCORE": "3"})
    assert (s.llm_provider, s.llm_model, s.retrieval_min_score) == ("ollama", "qwen2.5", 3.0)


def test_rag_settings_prefixed_name_wins():
    s = load_settings({"ASSISTANT_RETRIEVAL_MIN_SCORE": "1.5", "RETRIEVAL_MIN_SCORE": "9"})
    assert s.retrieval_min_score == 1.5


@pytest.mark.parametrize(
    "env",
    [
        {"ASSISTANT_ANSWER_PATH": "magic"},
        {"ASSISTANT_RETRIEVAL_MIN_SCORE": "-1"},
        {"ASSISTANT_RETRIEVAL_MIN_SCORE": "nan"},
        {"ASSISTANT_RETRIEVAL_K": "0"},
        {"ASSISTANT_LLM_PROVIDER": "gpt"},
    ],
)
def test_rag_settings_reject_invalid(env):
    with pytest.raises(ConfigError):
        load_settings(env)
