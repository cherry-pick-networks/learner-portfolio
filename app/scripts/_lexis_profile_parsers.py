"""Parsers and constants for init_lexis_profile CSV."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _ROOT / "temp" / "data" / "english"
_TEMP_DIR = _ROOT / "temp" / "english_profile_load"
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
KNOWN_LEVIS_COLS = frozenset(
    {"word", "tag"}
    | {f"level_freq@{lev}" for lev in LEVELS}
    | {"total_freq@total"}
    | {f"nb_doc@{lev}" for lev in LEVELS}
    | {"nb_doc@total"}
)
DEFAULT_LEXIS_PATH = _DATA_DIR / "lexis_profile.csv"


def parse_float(value: str) -> float:
    if not value or not value.strip():
        return 0.0
    try:
        return float(value.strip())
    except ValueError:
        return 0.0


def parse_int(value: str) -> int:
    if not value or not value.strip():
        return 0
    try:
        return int(float(value.strip()))
    except ValueError:
        return 0
