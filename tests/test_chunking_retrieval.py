"""Chunking + TF-IDF retrieval tests."""

import pytest

from compliance_rag.chunking import chunk_text
from compliance_rag.corpus import load_corpus
from compliance_rag.retrieval import Retriever


def test_chunk_empty_input_yields_no_chunks():
    assert chunk_text("", "X") == []
    assert chunk_text("   ", "X") == []


def test_chunk_max_length_respected():
    chunks = chunk_text("word " * 500, "X", max_chars=100, overlap=10)
    assert chunks and all(len(c.text) <= 100 for c in chunks)
    assert all(c.text for c in chunks)


def test_chunk_overlap_preserves_boundary_text():
    text = "alpha beta gamma delta epsilon zeta eta theta iota kappa"
    chunks = chunk_text(text, "S", max_chars=30, overlap=10)
    assert len(chunks) >= 2
    # Overlap: tail of chunk 0 shares text with head of chunk 1.
    assert chunks[0].text[-5:] in chunks[1].text or len(chunks[0].text) < 30


def test_chunk_ids_are_stable_and_unique():
    chunks = chunk_text("one two three " * 60, "SRC", max_chars=50, overlap=5)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))
    assert ids[0] == "SRC#0"


def test_chunk_invalid_params_rejected():
    with pytest.raises(ValueError):
        chunk_text("hello world", "S", max_chars=10, overlap=10)


def test_corpus_loads_chunks():
    chunks = load_corpus()
    assert len(chunks) >= 5
    assert {c.source_id for c in chunks} >= {"BB-CDD-01", "BB-REC-02", "BB-AML-03"}


def test_retrieval_ranks_relevant_passage_first():
    retriever = Retriever(load_corpus())
    results = retriever.search("How long are identity verification records kept?")
    assert results
    assert results[0].chunk.source_id == "BB-CDD-01"


def test_retrieval_scores_descending():
    results = Retriever(load_corpus()).search("training refresher twelve months")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_retrieval_no_match_returns_empty():
    assert Retriever(load_corpus()).search("quantum entanglement banana") == []


def test_retrieval_top_k_respected():
    results = Retriever(load_corpus()).search("records retained years", top_k=1)
    assert len(results) == 1


def test_retrieval_invalid_top_k():
    with pytest.raises(ValueError):
        Retriever(load_corpus()).search("records", top_k=0)


def test_retriever_uses_custom_vectorizer():
    """Swap-point proof: a custom vectorizer actually drives retrieval."""
    seen = []

    def vectorizer(text):
        seen.append(text)
        return {"records": 1.0} if "records" in text.lower() else {}

    def similarity(a, b):
        return 1.0 if set(a) & set(b) else 0.0

    retriever = Retriever(load_corpus(), vectorizer=vectorizer,
                          similarity=similarity)
    results = retriever.search("records")
    assert seen  # custom vectorizer was called
    assert results and all("records" in r.chunk.text.lower() for r in results)
