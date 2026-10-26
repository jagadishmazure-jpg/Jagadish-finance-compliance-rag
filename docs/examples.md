# Real code excerpts and their real output

All output below is from actual runs in this repo (see README for the
full demo transcript).

## A cited answer

```python
from compliance_rag.corpus import load_corpus
from compliance_rag.qa import answer_question
from compliance_rag.retrieval import Retriever

answer = answer_question(
    "How long must identity verification records be kept after an account closes?",
    Retriever(load_corpus()))
answer.status        # 'answered'
answer.confidence    # 0.466 (rounded display; exact value from the run)
answer.citations     # ['BB-CDD-01#0', 'BB-REC-02#0']
```

## A refusal

```python
refused = answer_question("What is the capital of France?", Retriever(load_corpus()))
refused.status            # 'abstained'
refused.claims             # []
refused.escalate_to_human  # True
refused.refusal_reason    # 'no passage retrieved for this question'
```

## The authorizer, in one query each

```python
from compliance_rag.store import create_store
conn = create_store()
conn.execute("SELECT chunk_id FROM v_passages").fetchall()   # succeeds
conn.execute("SELECT * FROM passages").fetchall()            # DatabaseError: denied
conn.execute("SELECT name FROM sqlite_master").fetchall()    # DatabaseError: denied
```

## A refused confirmation

```python
from compliance_rag.gates import ConfirmationGate
gate = ConfirmationGate("publish-answer")
gate.request("Priya Nair")
gate.confirm("yes, wait, no")   # GateError: self-contradicting consent
gate.confirm("yes")             # True -- but only once; a second call fails (single-use)
```
