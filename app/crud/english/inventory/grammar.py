from __future__ import annotations

import falkordb
from pydantic import BaseModel


class GrammarItem(BaseModel):
    guideword: str
    source: str


_QUERY = (
    "MATCH (g:GrammarItem)-[:GRAMMATICAL_LEVEL]->(l:CefrLevel {code: $cefr}) "
    "RETURN g.guideword AS guideword, g.source AS source"
)


def list_by_cefr(graph: falkordb.Graph, cefr: str) -> list[GrammarItem]:
    result = graph.query(_QUERY, params={"cefr": cefr.upper()})
    return [
        GrammarItem(guideword=row[0], source=row[1])
        for row in result.result_set
    ]
