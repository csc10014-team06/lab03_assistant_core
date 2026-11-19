"""index.py — load the handbook knowledge base (KB) and search it by keyword overlap.

Lab 6. The KB is a folder of Markdown files (``assistant_core/data/kb/*.md``). Every
``## <id> <title>`` heading starts one *chunk*; the lines below it are the chunk text.
An optional ``Alias: <rule id>`` line links the chunk to a rule in ``handbook.json``.

Scoring is the same idea as the mini search engine in the practice (S1–S3): every
distinct query word that appears in a chunk adds 1 to that chunk's score. Ties are
broken by chunk id so results are deterministic.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

_WORD = re.compile(r"[a-z0-9]+")
_HEADING = re.compile(r"^##\s+(?P<id>\S+)\s+(?P<title>.+?)\s*$")
_ALIAS = re.compile(r"^alias:\s*(?P<alias>\S+)\s*$", re.IGNORECASE)

# Function words that would otherwise match almost every chunk.
STOPWORDS = frozenset(
    """
    a about an and any are as at be been but by can could did do does for from had has have
    he her his how i if in into is it its me much many my no not of on or our she should so
    than that the their them then there these they this to up us was we were what when where
    which who whom why will with would you your
    """.split()
)


class KBError(Exception):
    """Raised when the knowledge base folder cannot be read or is malformed."""


def tokenize(text: str) -> list[str]:
    """Lower-case *text*, split it into words and drop stopwords.

    Bonus H3 lives here: e.g. strip a trailing ``s`` from words longer than 4 letters
    so ``retakes`` matches ``retake``. Re-run ``eval/compare_paths.py`` after changing it.
    """
    return [w for w in _WORD.findall(text.lower()) if w not in STOPWORDS]


@dataclass(frozen=True)
class Chunk:
    id: str
    title: str
    text: str
    alias: str | None = None
    terms: frozenset[str] = field(default=frozenset(), compare=False, repr=False)


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float

    @property
    def chunk_id(self) -> str:
        return self.chunk.id


def parse_kb_markdown(markdown: str) -> list[Chunk]:
    """Split one KB Markdown document into chunks (text before the first ``##`` is ignored)."""
    chunks: list[Chunk] = []
    current: dict[str, object] | None = None

    def flush() -> None:
        if current is None:
            return
        text = " ".join(current["lines"]).strip()  # type: ignore[arg-type]
        if not text:
            raise KBError(f"chunk {current['id']} has no text")
        title = str(current["title"])
        chunks.append(
            Chunk(
                id=str(current["id"]),
                title=title,
                text=text,
                alias=current["alias"],  # type: ignore[arg-type]
                terms=frozenset(tokenize(title + " " + text)),
            )
        )

    for raw in markdown.splitlines():
        line = raw.strip()
        if m := _HEADING.match(line):
            flush()
            current = {"id": m["id"], "title": m["title"], "lines": [], "alias": None}
        elif current is not None and (m := _ALIAS.match(line)):
            current["alias"] = m["alias"]
        elif current is not None and line:
            current["lines"].append(line)  # type: ignore[union-attr]
    flush()
    return chunks


class KBIndex:
    """In-memory inverted index over KB chunks."""

    def __init__(self, chunks: Iterable[Chunk]) -> None:
        self._chunks: dict[str, Chunk] = {}
        self._postings: dict[str, set[str]] = {}
        for chunk in chunks:
            if chunk.id in self._chunks:
                raise KBError(f"duplicate chunk id {chunk.id}")
            self._chunks[chunk.id] = chunk
            for term in chunk.terms:
                self._postings.setdefault(term, set()).add(chunk.id)

    @classmethod
    def from_dir(cls, kb_dir: Path) -> KBIndex:
        files = sorted(Path(kb_dir).glob("*.md"))
        if not files:
            raise KBError(f"no *.md files in knowledge base folder {kb_dir}")
        chunks: list[Chunk] = []
        for path in files:
            try:
                chunks.extend(parse_kb_markdown(path.read_text(encoding="utf-8")))
            except OSError as exc:
                raise KBError(f"cannot read {path}: {exc}") from exc
        return cls(chunks)

    def __len__(self) -> int:
        return len(self._chunks)

    def __contains__(self, chunk_id: object) -> bool:
        return chunk_id in self._chunks

    def get(self, chunk_id: str) -> Chunk:
        return self._chunks[chunk_id]

    def ids(self) -> list[str]:
        return sorted(self._chunks)

    def alias_map(self) -> dict[str, str]:
        """Map handbook.json rule ids (aliases) to KB chunk ids."""
        return {c.alias: c.id for c in self._chunks.values() if c.alias}

    def search(self, query: str, k: int = 3) -> list[Hit]:
        """Return the top *k* chunks, score descending then id ascending; chunks scoring 0 are left out."""
        scores: dict[str, int] = {}
        for term in set(tokenize(query)):
            for chunk_id in self._postings.get(term, ()):
                scores[chunk_id] = scores.get(chunk_id, 0) + 1
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
        return [Hit(self._chunks[cid], float(score)) for cid, score in ranked]
