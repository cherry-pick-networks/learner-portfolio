from __future__ import annotations

from collections.abc import Generator

import kuzu

from app.core.config import settings

_db: kuzu.Database | None = None

_NODE_DDLS = [
    (
        "CREATE NODE TABLE IF NOT EXISTS GrammarItem"
        "(guideword STRING, source STRING, PRIMARY KEY (guideword))"
    ),
    (
        "CREATE NODE TABLE IF NOT EXISTS LexicalItem"
        "(headword STRING, pos STRING, synset_id STRING, ngsl_rank INT64,"
        " PRIMARY KEY (headword))"
    ),
    (
        "CREATE NODE TABLE IF NOT EXISTS CefrLevel"
        "(code STRING, PRIMARY KEY (code))"
    ),
    (
        "CREATE NODE TABLE IF NOT EXISTS Passage"
        "(passage_id STRING, year INT64, grade_group STRING,"
        " curriculum STRING, subject STRING, publisher STRING, unit STRING,"
        " text STRING, source_file STRING, PRIMARY KEY (passage_id))"
    ),
    (
        "CREATE NODE TABLE IF NOT EXISTS Exam"
        "(exam_id STRING, year INT64, month INT64, issuer STRING, exam_type STRING,"  # noqa: E501
        " PRIMARY KEY (exam_id))"
    ),
    (
        "CREATE NODE TABLE IF NOT EXISTS ExamPassage"
        "(passage_id STRING, question_group STRING, text STRING, paragraphs STRING,"  # noqa: E501
        " PRIMARY KEY (passage_id))"
    ),
    (
        "CREATE NODE TABLE IF NOT EXISTS ExamQuestion"
        "(question_id STRING, number INT64, question_type STRING, stem STRING,"
        " options STRING, answer INT64, score INT64, PRIMARY KEY (question_id))"
    ),
]

_REL_DDLS = [
    "CREATE REL TABLE IF NOT EXISTS AT_LEVEL(FROM GrammarItem TO CefrLevel)",
    (
        "CREATE REL TABLE IF NOT EXISTS LEXICAL_LEVEL"
        "(FROM LexicalItem TO CefrLevel)"
    ),
    "CREATE REL TABLE IF NOT EXISTS IN_EXAM(FROM ExamPassage TO Exam)",
    "CREATE REL TABLE IF NOT EXISTS QUESTION_OF(FROM ExamQuestion TO ExamPassage)",  # noqa: E501
]


def get_graph_conn() -> Generator[kuzu.Connection, None, None]:
    if _db is None:
        raise RuntimeError(
            "Kuzu database not initialized; ensure app lifespan has run"
        )
    conn = kuzu.Connection(_db)
    yield conn


def init_graph_schema() -> None:
    global _db
    _db = kuzu.Database(settings.kuzu_path)
    conn = kuzu.Connection(_db)
    for ddl in _NODE_DDLS + _REL_DDLS:
        conn.execute(ddl)
