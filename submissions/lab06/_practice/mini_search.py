"""Lab 6 practice — T1 (S1–S3): a mini search engine over 4 documents.

Fill in the three TODOs, then run (from your folder):

    pytest -q test_mini_search.py          # -> 4 passed
    python mini_search.py                  # prints the two checks from the lab sheet
"""
from __future__ import annotations

import re

DOCS = {
    "D1": "Library opening hours: the library opens at 7am and closes at 8pm.",
    "D2": "Tuition is charged per credit; retake credits cost 1.5 times more.",
    "D3": "Report a lost student card to Student Affairs to get a new card.",
    "D4": "Final exam absence requires medical evidence within 3 working days.",
}

STOPWORDS = {
    "a", "an", "and", "are", "at", "for", "get", "i", "in", "is", "it", "me", "my", "new",
    "of", "on", "or", "per", "the", "to", "what", "when", "where", "with",
}


def tokenize(text: str) -> list[str]:
    """Given: lower-case words without punctuation or stopwords."""
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]


def build_index(docs: dict[str, str]) -> dict[str, set[str]]:
    """S1 — inverted index: word -> set of doc_ids that contain it."""
    index: dict[str, set[str]] = {}
    # TODO S1: for each (doc_id, text) and each word in tokenize(text):
    #          index.setdefault(word, set()).add(doc_id)
    raise NotImplementedError("S1: build_index")
    return index


def search(index: dict[str, set[str]], query: str, k: int = 2) -> list[tuple[str, int]]:
    """S2 + S3 — score = number of query words found in the doc; best k first."""
    scores: dict[str, int] = {}
    # TODO S2: for each word in tokenize(query), add 1 to every doc_id in index.get(word, set())
    # TODO S3: sort by score descending, then doc_id ascending, keep the first k:
    #          sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
    raise NotImplementedError("S2/S3: search")
    return []


if __name__ == "__main__":
    idx = build_index(DOCS)
    print(search(idx, "I lost my student card"))         # expected [('D3', 3)]
    print(search(idx, "what is the capital of France"))  # expected []
