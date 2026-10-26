# Related repos

Cross-links, not duplication: each repo below covers a neighbouring
concern; this repo does not re-implement them.

- **Finance KYC/AML pipeline** (sibling finance scaffold): customer due
  diligence workflows and sanctions-style screening with auditable
  steps. This repo covers the *question-answering* side (what does the
  rule say, with a citation); the KYC/AML repo covers the *workflow*
  side (collect, check, escalate a case).
- **Finance credit memo** (sibling finance scaffold): turning structured
  findings into explained credit narratives. Overlap: explainability and
  citation discipline; difference: memos synthesise across sources,
  this repo refuses unless a passage supports the answer.
- **Finance governance proof-of-concept** (sibling finance scaffold):
  governance, risk, and auditability framing for finance AI. This repo
  is one concrete implementation of the controls that framing calls for.
- **Agentic RAG / permission-aware RAG** (existing portfolio repos):
  general retrieval patterns. This repo narrows them to compliance
  questions, adds the abstention trust boundary, and uses a synthetic
  regulation corpus instead of a general corpus.
- **Fraud detection agents** (existing portfolio repo): detection and
  triage. This repo does not detect fraud; it answers "what does the
  rule require" questions that a triage workflow might ask.

Note: sibling finance scaffolds are named as planned portfolio
neighbours; links are added once their repos exist. No repo content is
duplicated here.
