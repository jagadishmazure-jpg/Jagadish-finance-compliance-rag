"""Finance compliance RAG: cited answers over a synthetic regulation corpus.

All data in this package is SYNTHETIC and fictional. Nothing here is legal
advice, and nothing here describes a real bank, regulator, or regulation.
"""

from compliance_rag.chunking import Chunk, chunk_text
from compliance_rag.retrieval import Retriever, ScoredPassage, TFIDFIndex
from compliance_rag.qa import Answer, Claim, answer_question
from compliance_rag.corpus import REGRESSION_SET, load_corpus

__all__ = [
    "Chunk", "chunk_text", "Retriever", "ScoredPassage", "TFIDFIndex",
    "Answer", "Claim", "answer_question", "REGRESSION_SET", "load_corpus",
]
