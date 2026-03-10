"""GrammarProfile graph: list by CEFR or guidewords."""

from __future__ import annotations

import falkordb

from app.schemas.english.inventory.grammar import GrammarProfile

_QUERY_BY_CEFR = (
    "MATCH (g:GrammarProfile)-[:GRAMMAR_LEVEL]->(c:CefrLevel {code: $cefr}) "
    "RETURN g.guideword, g.super_category, g.sub_category, g.type, "
    "g.can_do, g.example, g.lexical_range, c.code"
)

_LIST_BY_GUIDEWORDS_QUERY = (
    "MATCH (g:GrammarProfile) WHERE g.guideword IN $guidewords "
    "OPTIONAL MATCH (g)-[:GRAMMAR_LEVEL]->(c:CefrLevel) "
    "RETURN g.guideword, g.super_category, g.sub_category, g.type, "
    "g.can_do, g.example, g.lexical_range, c.code"
)


def _row_to_profile(row: tuple) -> GrammarProfile:
    return GrammarProfile(
        guideword=row[0],
        super_category=row[1],
        sub_category=row[2],
        type=row[3],
        can_do=row[4] or None,
        example=row[5] or None,
        lexical_range=row[6] or None,
        cefr_level=(row[7].lower() if row[7] else None),
    )


def list_by_cefr(graph: falkordb.Graph, cefr: str) -> list[GrammarProfile]:
    result = graph.query(_QUERY_BY_CEFR, params={"cefr": cefr.lower()})
    return [_row_to_profile(row) for row in result.result_set]


def list_by_guidewords(
    graph: falkordb.Graph, guidewords: list[str]
) -> list[GrammarProfile]:
    if not guidewords:
        return []
    result = graph.query(
        _LIST_BY_GUIDEWORDS_QUERY, params={"guidewords": guidewords}
    )
    return [_row_to_profile(row) for row in result.result_set]
