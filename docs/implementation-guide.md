# Implementation guide (for adopters)

1. **Start from the trust boundary, not the retriever.** Decide your
   answer / review / abstain thresholds on a labelled set you trust,
   and measure the abstention rate before you measure accuracy. An
   answer system that never refuses is a liability in regulated work.
2. **Keep claims excerpt-shaped.** In this scaffold a claim is an exact
   excerpt of a cited passage. If you add generation, keep the rule
   "every factual sentence carries a citation, and the citation must
   contain the sentence's content" as a test, not a guideline.
3. **Swap embeddings at the documented point.** Implement
   `vectorizer(text) -> dict[str, float]` (or adapt `Retriever` to
   dense vectors) and re-run the regression set; do not rewrite
   `qa.py`. Expect thresholds to change — re-measure them.
4. **Replace the corpus, not the schema.** Real documents go through
   the same chunker; keep chunk ids stable across re-indexes or old
   citations break.
5. **Wire escalation to a real queue.** The `escalate_to_human` flag
   is the seam: route abstained and needs-review answers there, with
   reviewer identity and timestamps, before any user-facing release.
6. **Keep the store behind views.** Add new views for new read needs;
   never widen the authorizer to base tables for convenience. Add an
   authorizer test per new view.
7. **Redact before logging, not after.** Call `redact()` at the point
   an answer or query is recorded; a log scrubber run later is a second
   line, not the first.
8. **Do not ship the synthetic corpus as content.** It is test data.
   Label it as such wherever it appears, and replace it before any
   real use.
