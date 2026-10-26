"""Retrieval: TF-IDF (stdlib) standing in for embeddings.

SWAP POINT FOR REAL EMBEDDINGS (documented, tested):
``Retriever`` accepts any ``vectorizer`` callable with the signature
``vectorizer(text) -> dict[str, float]``. The default is the TF-IDF index
in this module. To use real embeddings, pass a callable that returns a
sparse or dense vector mapping and a matching similarity function -- no
other code changes. Until that swap happens, retrieval is lexical only:
it matches shared words, not meaning, and that limit is stated in
docs/limitations.md and is visible as tests.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from compliance_rag.chunking import Chunk

_TOKEN = re.compile(r"[a-z0-9]+")

# Common function words carry no topical signal and let unrelated
# questions ("what is the capital of ...?") score off shared glue words.
# They are dropped from both documents and queries. This is a lexical
# heuristic, not understanding: negation and synonyms are still missed
# (see docs/limitations.md).
STOPWORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "am",
    "how", "what", "when", "where", "who", "whom", "which", "why",
    "do", "does", "did", "can", "could", "should", "would", "will",
    "i", "you", "we", "they", "he", "she", "it", "its", "of", "to",
    "in", "on", "for", "and", "or", "by", "with", "after", "before",
    "within", "at", "from", "as", "if", "then", "than", "that", "this",
    "these", "those", "not", "no", "yes",
})


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in STOPWORDS]


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a.get(k, 0.0) * v for k, v in b.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


@dataclass(frozen=True)
class ScoredPassage:
    chunk: Chunk
    score: float


class TFIDFIndex:
    """Build TF-IDF vectors over chunks; query vectors use the same IDF."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = list(chunks)
        docs = [tokenize(c.text) for c in self.chunks]
        df: dict[str, int] = {}
        for tokens in docs:
            for term in set(tokens):
                df[term] = df.get(term, 0) + 1
        n = max(len(docs), 1)
        self.idf = {t: math.log((n + 1) / (d + 1)) + 1.0 for t, d in df.items()}
        self.vectors = [self._vector(tokens) for tokens in docs]

    def _vector(self, tokens: list[str]) -> dict[str, float]:
        counts: dict[str, int] = {}
        for tok in tokens:
            counts[tok] = counts.get(tok, 0) + 1
        return {t: c * self.idf.get(t, 1.0) for t, c in counts.items()}

    def query_vector(self, text: str) -> dict[str, float]:
        return self._vector(tokenize(text))

    def search(self, query: str, top_k: int = 3) -> list[ScoredPassage]:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        qv = self.query_vector(query)
        scored = [ScoredPassage(c, _cosine(qv, v))
                  for c, v in zip(self.chunks, self.vectors)]
        scored.sort(key=lambda s: s.score, reverse=True)
        return [s for s in scored if s.score > 0.0][:top_k]


class Retriever:
    """Retriever with an explicit vectorizer swap point.

    ``vectorizer`` maps text to a vector dict; ``similarity`` compares two
    vectors. Defaults are the TF-IDF index. A test proves a custom
    vectorizer is actually used (see test_retriever_uses_custom_vectorizer).
    """

    def __init__(self, chunks: list[Chunk], vectorizer=None, similarity=None):
        self.chunks = list(chunks)
        self.index = TFIDFIndex(chunks)
        self.vectorizer = vectorizer or self.index.query_vector
        self.similarity = similarity or _cosine
        # Precomputed TF-IDF chunk vectors, used when the default
        # vectorizer is in play; custom vectorizers re-vectorize chunks.
        self._chunk_vectors = self.index.vectors

    def search(self, query: str, top_k: int = 3) -> list[ScoredPassage]:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.vectorizer is self.index.query_vector:
            return self.index.search(query, top_k)
        qv = self.vectorizer(query)
        scored = [ScoredPassage(c, self.similarity(qv, self.vectorizer(c.text)))
                  for c in self.chunks]
        scored.sort(key=lambda s: s.score, reverse=True)
        return [s for s in scored if s.score > 0.0][:top_k]
