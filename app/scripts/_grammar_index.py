"""Load grammar CSV index by SuperCategory for tag_grammar."""

from __future__ import annotations

import csv
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_GRAMMAR_DIR = _ROOT / "temp" / "data" / "english"
DEFAULT_GRAMMAR_CSV = _GRAMMAR_DIR / "grammar_profile.csv"


def load_grammar_index(path: Path) -> dict[str, list[dict]]:
    """Read grammar CSV; return SuperCategory -> list of guideword entries."""
    by_super: dict[str, list[dict]] = {}
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            guideword = (row.get("guideword") or "").strip()
            level = (row.get("Level") or "").strip().lower()
            super_cat = (row.get("SuperCategory") or "").strip()
            sub_cat = (row.get("SubCategory") or "").strip()
            if not guideword or not super_cat:
                continue
            entry = {
                "guideword": guideword,
                "sub_category": sub_cat,
                "cefr": level,
            }
            by_super.setdefault(super_cat, []).append(entry)
    return by_super
