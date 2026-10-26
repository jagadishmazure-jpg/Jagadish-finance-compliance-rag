# Limitations and known failures

Kept visible, with the test that encodes each one where applicable.

1. **Lexical retrieval only.** TF-IDF cannot match synonyms ("keep" vs
   "retain" partially overlap by luck, not understanding), cannot handle
   negation ("must staff tell a customer..." is answered from a passage
   that says staff must *not* tell — the citation is right, the
   reasoning is the reviewer's, not the system's), and cannot rank by
   legal importance. Swap point: `Retriever(vectorizer=...)`.
2. **Thresholds are defaults, not tuned values.** 0.35 / 0.20 were
   chosen so the 6-question regression set separates (lowest regression
   score 0.42; unrelated questions score 0.0 after stopword removal).
   On a real corpus these numbers mean nothing until re-measured.
3. **Citations can be merely related.** The demo's first answer cites
   `BB-REC-02#0` alongside the correct `BB-CDD-01#0`. Citation presence
   is a checkability property, not a quality guarantee.
4. **Tiny synthetic corpus.** 5 invented documents, 6 regression
   questions. Any accuracy-sounding statement beyond "6/6 on this set"
   would be dishonest; the README says 6/6 on this set and nothing more.
5. **No audit log, no review UI, no real workflow.** Escalation is a
   flag on the `Answer` object, not a ticket in a queue. A production
   version needs durable escalation, reviewer identity, and an audit
   trail — all Planned, none claimed.
6. **Stopword list is hand-written.** Dropping "not" from queries is a
   known simplification that weakens negation handling further (see 1).
7. **In-memory store.** The SQLite catalogue is rebuilt per process;
   there is no persistence, migration, or backup story.
8. **No model involved.** There is no language model in this scaffold,
   so there is no generation risk to evaluate — and no generation
   quality to claim either. The refusal behaviour is structural (no
   claims are constructed below threshold), which is the point.
