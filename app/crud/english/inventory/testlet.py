"""Testlet graph: Source, Testlet (passage + questions in one node)."""

from __future__ import annotations

import json
from typing import Any

import falkordb


def upsert_source(
    graph: falkordb.Graph,
    *,
    source_id: str,
    year: int,
    month: int,
    exam_type: str,
    academic_year: int,
    issuer: str = "KICE",
) -> None:
    """Create or update a Source node.
    Call before upsert_testlet.
    """
    q = (
        "MERGE (s:Source {source_id: $source_id}) "
        "ON CREATE SET s.year = $year, s.month = $month, "
        "s.exam_type = $exam_type, s.academic_year = $academic_year, "
        "s.issuer = $issuer"
    )
    graph.query(
        q,
        params={
            "source_id": source_id,
            "year": year,
            "month": month,
            "exam_type": exam_type,
            "academic_year": academic_year,
            "issuer": issuer,
        },
    )


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
    """Create/update Testlet (passage + questions) and link to Source.
    Call upsert_source first.
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
        "t.questions = $questions "
        "WITH t MERGE (s:Source {source_id: $source_id}) "
        "MERGE (t)-[:IN_SOURCE]->(s)"
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
