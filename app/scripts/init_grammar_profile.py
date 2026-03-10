"""Init FalkorDB grammar profile from CSV."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

import falkordb

_ROOT = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _ROOT / "temp" / "data" / "english"
_TEMP_DIR = _ROOT / "temp" / "english_profile_load"
DEFAULT_GRAMMAR_PATH = _DATA_DIR / "grammar_profile.csv"


def init_grammar_profile(
    graph: falkordb.Graph,
    _session: object | None = None,
    *,
    path: Path | None = None,
) -> int:
    """Load grammar CSV into FalkorDB (all fields as node properties).
    Returns rows loaded. _session is accepted but unused (call-site compat)."""
    from app.crud.english.inventory import grammar

    src = path or DEFAULT_GRAMMAR_PATH
    if not src.exists():
        return 0
    use_direct = path is not None
    if not use_direct:
        _TEMP_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _TEMP_DIR / "grammar_profile.csv"
        shutil.copy(src, tmp)
        src = tmp
    count = 0
    try:
        with open(src, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                guideword = (row.get("guideword") or "").strip()
                level = (row.get("Level") or "").strip().lower()
                if not guideword or not level:
                    continue
                count += 1
                grammar.upsert_grammar_profile(
                    graph,
                    guideword=guideword,
                    cefr=level,
                    super_category=(row.get("SuperCategory") or "").strip()
                    or None,
                    sub_category=(row.get("SubCategory") or "").strip() or None,
                    type_=(row.get("type") or "").strip() or None,
                    can_do=(row.get("Can-do statement") or "").strip() or None,
                    example=(row.get("Example") or "").strip() or None,
                    lexical_range=(row.get("Lexical Range") or "").strip()
                    or None,
                )
    finally:
        if not use_direct and src.exists():
            src.unlink(missing_ok=True)
    return count
