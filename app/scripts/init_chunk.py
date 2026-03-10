"""Init Source + Task + TaskItem from chunk JSON."""

from __future__ import annotations

import json
from pathlib import Path

import falkordb
from sqlmodel import Session

from app.scripts._chunk_processor import process_one_chunk


def init_from_json(
    json_path: Path,
    session: Session,
    graph: falkordb.Graph,
    *,
    dry_run: bool = False,
) -> tuple[int, int, list[tuple[str, str]]]:
    """Load chunk JSON; upsert Source, Tasks, TaskItems.

    Expects a list of chunk objects: {source, split?, id, article, questions[]}.
    Returns (n_sources, n_tasks, [(task_id, text), ...]) for grammar tagging.
    """
    with open(json_path, encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        raw = [raw] if isinstance(raw, dict) else []

    total_sources = 0
    total_tasks = 0
    tagged_list: list[tuple[str, str]] = []
    seen_sources: set[str] = set()

    for item in raw:
        if not isinstance(item, dict):
            continue
        _n_sources, n_tasks, tagged = process_one_chunk(
            item, session, graph, dry_run
        )
        total_tasks += n_tasks
        tagged_list.extend(tagged)
        source_id = str(item.get("source") or "").strip()
        if source_id:
            seen_sources.add(source_id)

    total_sources = len(seen_sources)
    return total_sources, total_tasks, tagged_list
