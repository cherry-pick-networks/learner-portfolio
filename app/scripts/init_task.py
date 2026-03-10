"""Init Source + Task + TaskItem from flat JSON (temp/.json/task/*.json)."""

from __future__ import annotations

import json
from pathlib import Path

import falkordb
from sqlmodel import Session

from app.scripts._task_source_processor import process_one_source


def init_from_json(
    json_path: Path,
    session: Session,
    graph: falkordb.Graph,
    *,
    dry_run: bool = False,
) -> tuple[int, int, list[tuple[str, str]]]:
    """Load flat JSON; upsert Source, Tasks, TaskItems.

    Accepts a single object or a list of objects (e.g. all_test_chunks.json).
    Returns (n_sources, n_tasks, [(task_id, text), ...]) for upserted
    tasks with non-empty text (for grammar tagging).
    """
    with open(json_path, encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, list):
        total_sources = 0
        total_tasks = 0
        tagged_list: list[tuple[str, str]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            n_sources, n_tasks, tagged = process_one_source(
                item, session, graph, dry_run
            )
            total_sources += n_sources
            total_tasks += n_tasks
            tagged_list.extend(tagged)
        return total_sources, total_tasks, tagged_list

    return process_one_source(raw, session, graph, dry_run)
