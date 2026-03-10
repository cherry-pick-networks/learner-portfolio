"""Helpers for init_grammar_unit: source slug, unit title, profile iteration."""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_GRAMMAR_MD_ROOT = _ROOT / "temp" / "grammar"
_TITLE_RE = re.compile(
    r"^#{2,4}\s+(?:Unit|Appendix)\s+\d+\s+(.+)", re.MULTILINE
)


def source_slug(path: Path) -> str:
    """e.g. grammar-basic.json -> basic."""
    stem = path.stem
    if stem.startswith("grammar-"):
        return stem[8:]
    return stem


def unit_title(source: str, unit_num: int) -> str | None:
    """Extract title from temp/grammar/{source}/unit_{unit_num}.md."""
    md = _GRAMMAR_MD_ROOT / source / f"unit_{unit_num}.md"
    if not md.exists():
        return None
    m = _TITLE_RE.search(md.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else None


def iter_grammar_profiles(items: list) -> list[tuple[dict, int]]:
    """Yield (profile_dict, unit_num) for each grammar profile.
    Supports both flat format (guideword/level at top) and nested format
    (units with grammar_profiles array)."""
    result: list[tuple[dict, int]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        profiles = raw.get("grammar_profiles")
        if profiles is not None:
            unit_id = (raw.get("unit_id") or "").strip()
            unit_num = 0
            if unit_id.startswith("unit_"):
                try:
                    unit_num = int(unit_id[5:])
                except ValueError:
                    pass
            for p in profiles:
                if isinstance(p, dict):
                    result.append((p, unit_num))
        else:
            unit_num = int(raw.get("unit", 0))
            result.append((raw, unit_num))
    return result
