"""Init LexisSet (SQLite) and LexisItem (FalkorDB) from lexis JSON files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.scripts._lexis_item_helpers import book_slug

_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_LEXIS_INPUT = _ROOT / "temp" / "lexis"


def init_from_json(
    path: Path,
    graph,
    session,
    *,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Load one JSON; upsert LexisSet and LexisItem. Returns (sets, items)."""
    from app.crud.english.inventory import lexis, lexis_item, lexis_set

    with open(path, encoding="utf-8") as f:
        items = json.load(f)
    if not items:
        return 0, 0

    source = book_slug(path)
    set_ids_seen: set[str] = set()
    item_count = 0

    for raw in items:
        index = raw.get("index")
        headword = (raw.get("headword") or "").strip()
        unit_num = int(raw.get("day", 0))
        definition = (raw.get("oewnDef") or "").strip()
        pos = (raw.get("oewnPos") or "").strip() or None
        if not headword:
            continue

        item_id = f"{source}-{index}"
        set_id = f"{source}-day-{unit_num:02d}"
        set_ids_seen.add(set_id)

        if not dry_run:
            lexis_item.upsert_lexis_item(
                graph,
                item_id=item_id,
                headword=headword,
                pos=pos,
                definition=definition,
            )
            lexis_item.link_profile(graph, item_id=item_id, headword=headword)
            cefr = lexis.get_dominant_cefr(graph, headword)
            if cefr:
                lexis_item.link_cefr(graph, item_id=item_id, cefr=cefr)

            lexis_set.upsert_lexis_set(
                session,
                set_id=set_id,
                source=source,
                unit_num=unit_num,
            )
            lexis_set.link_item(session, set_id=set_id, item_id=item_id)

        item_count += 1

    if not dry_run and item_count:
        session.commit()
    return len(set_ids_seen), item_count


if __name__ == "__main__":
    import sys

    from app.scripts._lexis_item_cli import main

    sys.exit(main())
