from __future__ import annotations

from collections.abc import Generator

import kuzu

from app.core.config import settings

db = kuzu.Database(settings.kuzu_path)

_NODE_DDLS = [
    (
        "CREATE NODE TABLE IF NOT EXISTS GrammarItem"
        "(guideword STRING, source STRING, PRIMARY KEY (guideword))"
    ),
    (
        "CREATE NODE TABLE IF NOT EXISTS LexisItem"
        "(lemma STRING, pos STRING, synset_id STRING, ngsl_rank INT64,"
        " PRIMARY KEY (lemma))"
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
        "(exam_id STRING, year INT64, month INT64, issuer STRING, exam_type STRING,"
        " PRIMARY KEY (exam_id))"
    ),
    (
        "CREATE NODE TABLE IF NOT EXISTS ExamPassage"
        "(passage_id STRING, question_group STRING, text STRING, paragraphs STRING,"
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
        "CREATE REL TABLE IF NOT EXISTS LEXIS_AT_LEVEL"
        "(FROM LexisItem TO CefrLevel)"
    ),
    "CREATE REL TABLE IF NOT EXISTS IN_EXAM(FROM ExamPassage TO Exam)",
    "CREATE REL TABLE IF NOT EXISTS QUESTION_OF(FROM ExamQuestion TO ExamPassage)",
]


def get_graph_conn() -> Generator[kuzu.Connection, None, None]:
    conn = kuzu.Connection(db)
    yield conn


def init_graph_schema() -> None:
    conn = kuzu.Connection(db)
    for ddl in _NODE_DDLS + _REL_DDLS:
        conn.execute(ddl)
