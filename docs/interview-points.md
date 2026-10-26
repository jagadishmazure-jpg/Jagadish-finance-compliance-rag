# Interview points

- **Why abstention is structural, not behavioural.** Below threshold
  the code constructs no claims at all. There is no prompt asking a
  model to be careful; there is simply nothing to display. That is the
  strongest form of a refusal guarantee a retrieval scaffold can offer.
- **Why citations are excerpts.** A generated paraphrase with a
  citation invites the reviewer to trust the paraphrase. An excerpt
  lets the reviewer verify in seconds, and the test
  `test_answered_question_has_citations_for_every_claim` proves every
  claim's text is contained in its cited passage.
- **The authorizer's two-event subtlety.** A view read fires events for
  both the base table (tagged with the view) and the view. An
  authorizer that only checks the table name breaks every view read;
  one that only checks the view name is bypassable. Checking both is
  the correct rule, and the tests prove it with real queries.
- **Honest numbers.** 60 tests, 6 regression questions, 6/6 answered
  with the expected source cited, unrelated questions refused with zero
  claims. No claim is made beyond those sample sizes.
- **The known weakness to volunteer first.** Citations can be merely
  related (demo cites a general retention passage next to the specific
  one), and TF-IDF misses synonyms and negation. Naming this before
  being asked is the point of `docs/limitations.md`.
- **What I would do next.** Real embeddings behind the swap point,
  a labelled evaluation set an order of magnitude larger, and a durable
  escalation queue — in that order, because measurement comes before
  scale.
