"""Testlet graph: Testlet (passage + questions). Source is in SQLite."""

from __future__ import annotations

import json
from typing import Any

import falkordb


def upsert_testlet(
    graph: falkordb.Graph,
    *,
    testlet_id: str,
    source_id: str,
    question_group: str,
    text: str,
    footnotes: str = "",
    questions: list[dict[str, Any]] | None = None,
) -> None:
    """Create or update Testlet node (passage + questions).
    source_id references Source in SQLite; caller must ensure it exists.
    questions: list of dicts with number, section, question_type, stem,
    options, answer, score.
    """
    questions_json = json.dumps(questions if questions is not None else [])
    q = (
        "MERGE (t:Testlet {testlet_id: $testlet_id}) "
        "ON CREATE SET t.source_id = $source_id, "
        "t.question_group = $question_group, t.text = $text, "
        "t.footnotes = $footnotes, t.questions = $questions "
        "ON MATCH SET t.text = $text, t.footnotes = $footnotes, "
        "t.questions = $questions"
    )
    graph.query(
        q,
        params={
            "testlet_id": testlet_id,
            "source_id": source_id,
            "question_group": question_group,
            "text": text,
            "footnotes": footnotes,
            "questions": questions_json,
        },
    )
