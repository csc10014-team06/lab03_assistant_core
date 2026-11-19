"""Lab 6 practice — tests for S1–S3. Do not edit (check.py compares this file to the original)."""
from mini_search import DOCS, build_index, search


def test_s1_build_index_maps_words_to_doc_ids():
    idx = build_index(DOCS)
    assert idx["card"] == {"D3"}
    assert idx["credits"] == {"D2"}
    assert all(isinstance(v, set) for v in idx.values())
    assert "the" not in idx  # stopwords are dropped by tokenize


def test_s2_lost_student_card_scores_d3():
    assert search(build_index(DOCS), "I lost my student card") == [("D3", 3)]


def test_s2_no_match_returns_empty_list():
    assert search(build_index(DOCS), "what is the capital of France") == []


def test_s3_ties_sorted_by_doc_id_and_cut_to_k():
    idx = build_index(DOCS)
    assert search(idx, "library tuition exam") == [("D1", 1), ("D2", 1)]
    assert search(idx, "library tuition exam", k=3) == [("D1", 1), ("D2", 1), ("D4", 1)]
