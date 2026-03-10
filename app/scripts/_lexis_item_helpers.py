"""Helpers for init_lexis_item: book slug from path."""

from __future__ import annotations

from pathlib import Path


def book_slug(path: Path) -> str:
    """e.g. lexis-middle-basic.json -> middle-basic."""
    stem = path.stem
    if stem.startswith("lexis-"):
        return stem[6:]
    return stem
