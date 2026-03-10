"""Process one chunk dict: upsert Source, Task, TaskItems."""

from __future__ import annotations

from typing import Any

import falkordb
from sqlmodel import Session

from app.scripts._chunk_parsers import chunk_answer_to_int


def process_one_chunk(
    data: dict[str, Any],
    session: Session,
    graph: falkordb.Graph,
    dry_run: bool,
) -> tuple[int, int, list[tuple[str, str]]]:
    """Process a single chunk dict; upsert Source, Task, TaskItems.

    Returns (n_sources, n_tasks, [(task_id, text), ...]) for grammar tagging.
    """
    from app.crud.english.inventory import task
    from app.crud.english.inventory import task_item as task_item_crud
    from app.crud.english.records import source as source_crud

    source_id = str(data.get("source") or "").strip()
    chunk_id = str(data.get("id") or "").strip()
    if not source_id or not chunk_id:
        return 0, 0, []

    tagged_list: list[tuple[str, str]] = []
    article = str(data.get("article") or "").strip()
    questions = data.get("questions")
    if not isinstance(questions, list):
        questions = []

    if not dry_run:
        source_crud.upsert_source(
            session,
            source_id=source_id,
            year=None,
            month=None,
            exam_type="external",
            academic_year=None,
            form=None,
            issuer="external",
            source_type="chunk",
        )

    task_id = chunk_id
    question_group = chunk_id

    if not dry_run:
        task.upsert_task(
            graph,
            task_id=task_id,
            source_id=source_id,
            question_group=question_group,
            text=article,
            footnotes="",
        )

    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            continue
        stem = str(q.get("question") or "").strip()
        raw_opts = q.get("options")
        if isinstance(raw_opts, list):
            options_list: list[str] = [
                str(o or "").strip() for o in raw_opts[:5]
            ]
        else:
            options_list = []
        while len(options_list) < 5:
            options_list.append("")
        answer = chunk_answer_to_int(str(q.get("answer") or ""))

        if not dry_run:
            task_item_crud.upsert_task_item(
                graph,
                task_id=task_id,
                number=i + 1,
                section="reading",
                question_type="",
                stem=stem,
                options=options_list,
                answer=answer,
                score=1,
            )

    if not dry_run and article:
        tagged_list.append((task_id, article))

    return 1, 1, tagged_list
