from __future__ import annotations

from typing import cast

import kuzu
from kuzu.query_result import QueryResult
from pydantic import BaseModel


class LexisItem(BaseModel):
    lemma: str
    pos: str | None
    synset_id: str | None
    ngsl_rank: int | None


_QUERY = (
    "MATCH (l:LexisItem)-[:LEXIS_AT_LEVEL]->(c:CefrLevel {code: $cefr}) "
    "RETURN l.lemma AS lemma, l.pos AS pos, l.synset_id AS synset_id,"
    " l.ngsl_rank AS ngsl_rank"
)


def list_by_cefr(conn: kuzu.Connection, cefr: str) -> list[LexisItem]:
    raw = conn.execute(_QUERY, parameters={"cefr": cefr.upper()})
    result = raw if not isinstance(raw, list) else raw[0] if raw else None
    if result is None:
        return []
    cursor = cast(QueryResult, result)
    items: list[LexisItem] = []
    while cursor.has_next():
        row = cast(tuple[object, ...], cursor.get_next())
        items.append(
            LexisItem(
                lemma=cast(str, row[0]),
                pos=cast(str | None, row[1]),
                synset_id=cast(str | None, row[2]),
                ngsl_rank=cast(int | None, row[3]),
            )
        )
    return items
