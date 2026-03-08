from __future__ import annotations

from typing import cast

import kuzu
from kuzu.query_result import QueryResult
from pydantic import BaseModel


class GrammarItem(BaseModel):
    guideword: str
    source: str


_QUERY = (
    "MATCH (g:GrammarItem)-[:AT_LEVEL]->(l:CefrLevel {code: $cefr}) "
    "RETURN g.guideword AS guideword, g.source AS source"
)


def list_by_cefr(conn: kuzu.Connection, cefr: str) -> list[GrammarItem]:
    raw = conn.execute(_QUERY, parameters={"cefr": cefr.upper()})
    result = raw if not isinstance(raw, list) else raw[0] if raw else None
    if result is None:
        return []
    cursor = cast(QueryResult, result)
    items: list[GrammarItem] = []
    while cursor.has_next():
        row = cast(tuple[object, ...], cursor.get_next())
        items.append(
            GrammarItem(
                guideword=cast(str, row[0]),
                source=cast(str, row[1]),
            )
        )
    return items
