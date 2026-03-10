"""Init GrammarSet (SQLite) and GrammarProfile (FalkorDB) from grammar JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.scripts._grammar_unit_helpers import (
    iter_grammar_profiles,
    source_slug,
    unit_title,
)

_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_GRAMMAR_INPUT = _ROOT / "temp" / ".json" / "grammar_set"


def init_from_json(
    path: Path,
    graph,
    session,
    *,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Load one grammar-*.json; upsert profile and set. Returns (sets, items)."""  # noqa: E501
    from app.crud.english.inventory import grammar, grammar_set

    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        return 0, 0
    items = data if isinstance(data, list) else [data]

    source = source_slug(path)
    set_ids_seen: set[str] = set()
    item_count = 0

    for raw, unit_num in iter_grammar_profiles(items):
        guideword = (raw.get("guideword") or "").strip()
        level = (raw.get("level") or "").strip().lower()
        if not guideword or not level:
            continue

        set_id = f"{source}-unit-{unit_num:02d}"
        set_ids_seen.add(set_id)

        if not dry_run:
            grammar.upsert_grammar_profile(
                graph,
                guideword=guideword,
                cefr=level,
                super_category=(raw.get("category") or "").strip() or None,
                sub_category=(raw.get("sub_category") or "").strip() or None,
                can_do=(raw.get("can_do") or "").strip() or None,
            )
            grammar_set.upsert_grammar_set(
                session,
                set_id=set_id,
                source=source,
                unit_num=unit_num,
                title=unit_title(source, unit_num),
            )
            grammar_set.link_grammar(
                session, set_id=set_id, guideword=guideword
            )

        item_count += 1

    if not dry_run and item_count:
        session.commit()
    return len(set_ids_seen), item_count


if __name__ == "__main__":
    from app.scripts._grammar_unit_cli import main

    sys.exit(main())
