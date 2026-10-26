# Knowledge notes — distilled patterns

Written in my own words from the general patterns in the source
material. No sentences are copied from any source document, and no
affiliation with any institution is claimed.

## Pattern 1: Ground compliance answers in retrievable text

A compliance answer is only as good as its audit trail. The working
pattern is: keep the source passages addressable (stable ids), retrieve
before answering, and attach the passage to every claim. If a claim
cannot be attached to a passage, it does not ship.

## Pattern 2: Split rules into retrievable pieces

Long rule documents are not retrievable as wholes: a query matches a
whole document weakly and a reviewer cannot find the relevant sentence.
Splitting into bounded, overlapping pieces with stable ids makes both
retrieval precision and human verification practical. Overlap exists
because rules do not respect chunk boundaries.

## Pattern 3: Know when retrieval falls short

The most important behaviour of a compliance retrieval system is not
answering well — it is refusing clearly. Three bands work better than
two: answer confidently, draft for a human, or refuse outright. The
middle band matters because it preserves useful-but-uncertain work
without presenting it as final.

## Pattern 4: Auditable workflows beat clever prompts

For regulated work, the durable artefacts are the log, the citation,
the approver, and the expiry — not the wording of a prompt. Design so
that each of those is a data field with a test, and the system stays
auditable even when its retrieval quality is modest.

## Pattern 5: Synthetic data for the scaffold, real data only with governance

A demo corpus should be invented end to end: invented firm, invented
rules, invented numbers. That keeps the scaffold public and the tests
honest, and it forces a deliberate, governed step before any real
document is loaded.
