"""Parsers for init_chunk: answer mapping."""

from __future__ import annotations

CHUNK_ANSWER_MAP = {"A": 1, "B": 2, "C": 3, "D": 4}


def chunk_answer_to_int(a: str) -> int:
    a = (a or "").strip().upper()
    return CHUNK_ANSWER_MAP.get(a, 0)
