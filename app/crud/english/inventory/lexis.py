from __future__ import annotations

from typing import cast

import kuzu
from kuzu.query_result import QueryResult
from pydantic import BaseModel


class LexicalItem(BaseModel):
    headword: str
    pos: str | None
    synset_id: str | None
    ngsl_rank: int | None


_QUERY = (
    "MATCH (l:LexicalItem)-[:LEXICAL_LEVEL]->(c:CefrLevel {code: $cefr}) "
    "RETURN l.headword AS headword, l.pos AS pos, l.synset_id AS synset_id,"
    " l.ngsl_rank AS ngsl_rank"
)


def list_by_cefr(conn: kuzu.Connection, cefr: str) -> list[LexicalItem]:
    raw = conn.execute(_QUERY, parameters={"cefr": cefr.upper()})
    result = raw if not isinstance(raw, list) else raw[0] if raw else None
    if result is None:
        return []
    cursor = cast(QueryResult, result)
    items: list[LexicalItem] = []
    while cursor.has_next():
        row = cast(tuple[object, ...], cursor.get_next())
        items.append(
            LexicalItem(
                headword=cast(str, row[0]),
                pos=cast(str | None, row[1]),
                synset_id=cast(str | None, row[2]),
                ngsl_rank=cast(int | None, row[3]),
            )
        )
    return items
