"""Init grammar_item table (SQLite) from grammar_outlines.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTLINES = (
    _ROOT / "temp" / ".json" / "grammar_item" / "grammar_outlines.json"
)

_OLD_BOOK_UNIT_PATTERN = re.compile(r"^book-grammar-(.+):unit_(\d+)$")


def _normalize_book_unit(ref: str) -> str:
    """Normalize book-grammar ref to set_id (e.g. basic-unit-01)."""
    ref = (ref or "").strip()
    m = _OLD_BOOK_UNIT_PATTERN.match(ref)
    if m:
        source, num = m.group(1), int(m.group(2))
        return f"{source}-unit-{num:02d}"
    return ref


def init_from_json(path: Path, session) -> int:
    """Load grammar_outlines.json; upsert curriculum sessions.
    Returns total sessions upserted."""
    from app.crud.english.inventory.curriculum import upsert

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        sessions = data
    elif isinstance(data, dict):
        sessions = data.get("sessions", [])
    else:
        sessions = []

    for s in sessions:
        if not isinstance(s, dict):
            continue
        raw_units = s.get("book_units") or []
        book_units = [
            _normalize_book_unit(u) for u in raw_units if isinstance(u, str)
        ]
        upsert(
            session,
            curriculum_id=s.get("curriculum_id", ""),
            session_number=int(s.get("session_number", 0)),
            topic=s.get("topic", ""),
            book_units=book_units,
        )
    return len(sessions)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Init grammar_item from grammar_outlines.json"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_OUTLINES,
        help="Path to grammar_outlines.json",
    )
    args = parser.parse_args()

    path = args.input.resolve()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    try:
        from app.core.sqlite import get_session
    except ImportError:
        print(
            "Run from repo root and ensure app is on PYTHONPATH.",
            file=sys.stderr,
        )
        return 1

    session = next(get_session())
    total = init_from_json(path, session)
    print(f"Done: {total} grammar item sessions upserted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
