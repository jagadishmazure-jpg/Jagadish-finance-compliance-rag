"""Chunking: split regulation text into AI-readable pieces.

A chunk is a bounded slice of one source document, with a stable id of the
form ``<source_id>#<index>`` so every later citation can point at exactly
one slice. Chunks overlap by a fixed number of characters so a rule that
straddles a boundary is not lost, and no chunk is ever empty.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source_id: str
    index: int
    text: str


def chunk_text(text: str, source_id: str, max_chars: int = 600,
               overlap: int = 100) -> list[Chunk]:
    """Split ``text`` into overlapping chunks.

    Rules enforced (and tested):
    - empty / whitespace-only input yields no chunks;
    - every chunk is non-empty and at most ``max_chars`` long;
    - consecutive chunks overlap by exactly ``overlap`` characters when the
      source is long enough, so boundary rules survive splitting;
    - ``max_chars`` must exceed ``overlap``, otherwise slicing would loop.
    """
    if max_chars <= overlap:
        raise ValueError("max_chars must exceed overlap")
    if max_chars <= 0 or overlap < 0:
        raise ValueError("max_chars must be positive and overlap non-negative")
    text = text.strip()
    if not text:
        return []
    chunks: list[Chunk] = []
    start = 0
    index = 0
    step = max_chars - overlap
    while start < len(text):
        piece = text[start:start + max_chars].strip()
        if piece:
            chunks.append(Chunk(f"{source_id}#{index}", source_id, index, piece))
            index += 1
        if start + max_chars >= len(text):
            break
        start += step
    return chunks
