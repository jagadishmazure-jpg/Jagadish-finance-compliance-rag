# How it works, step by step

1. **Load the corpus.** `load_corpus()` returns chunks from 5 invented
   documents (due diligence, retention, suspicious activity, monitoring,
   training). Each document is short by design, so every citation can be
   checked by hand.
2. **Chunk.** `chunk_text(text, source_id, max_chars=600, overlap=100)`
   slices with overlap so a rule spanning a boundary is not split away.
   Chunk ids are `<source_id>#<index>`.
3. **Index.** `TFIDFIndex` counts terms per chunk, computes IDF across
   the corpus, and stores a vector per chunk. Function words are dropped
   from both documents and queries.
4. **Retrieve.** `Retriever.search(question, top_k=3)` scores the query
   vector against chunk vectors with cosine similarity and returns the
   top passages with scores, best first, zero-score passages excluded.
5. **Decide.** `answer_question()` applies thresholds:
   - ≥ 0.35: answered. Claims are exact excerpts of retrieved passages;
     citations list their chunk ids.
   - 0.20–0.35: needs review. A draft is returned with citations, but
     `escalate_to_human` is True and the status says so.
   - < 0.20, or no passages, or an empty question: abstained. No claims,
     no citations, escalation True, and a refusal reason explaining the
     score fell short.
6. **Redact and gate.** Before any answer is shown or published, PII is
   redacted and a confirmation gate requires a named, unexpired,
   single-use approval for the exact scope plus an explicit "yes".
7. **Store reads.** Passage lookups go through SQLite views only; the
   authorizer denies base tables, `sqlite_master`, writes, PRAGMA,
   ATTACH, and extension loading.
