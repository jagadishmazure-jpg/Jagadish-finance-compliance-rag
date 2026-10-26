# Architecture

```mermaid
flowchart TD
    Docs[Synthetic regulation documents] --> Chunker[Chunker: overlap, stable ids]
    Chunker --> Chunks[Chunks: BB-CDD-01#0, ...]
    Chunks --> Index[TF-IDF index, stdlib only]
    Index --> Retriever[Retriever: cosine ranking]
    Q[Compliance question] --> Retriever
    Retriever --> Boundary{Trust boundary}
    Boundary -->|score >= 0.35| Answered[Answered: claims, each an excerpt of a cited passage]
    Boundary -->|0.20 - 0.35| Review[Draft: escalate to human review]
    Boundary -->|< 0.20 or none| Abstain[Abstained: zero claims]
    Answered --> Redact[PII redaction]
    Redact --> Gate[Confirmation gate: named approval, explicit yes]
    Gate --> Publish[Published answer]
    Chunks --> Store[SQLite store: views only, authorizer enforced]
    Store --> Retriever
```

Key design choice: the trust boundary sits *between* retrieval and
answer construction, not after it. A weak retrieval result never reaches
a sentence generator, so there is nothing to hallucinate with — the
refusal path produces no claims at all, by construction, not by asking
a model to be careful.

Swap point: `Retriever` accepts a `vectorizer` callable. Replacing
TF-IDF with real embeddings means passing a different vectorizer, not
rewriting the answer flow. The store is separate: it holds the passage
catalogue behind views, and the authorizer — not application code — is
what enforces view-only access.
