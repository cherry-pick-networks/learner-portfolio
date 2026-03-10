"""GrammarProfile graph: upsert and re-export queries."""

from __future__ import annotations

import falkordb

from app.crud.english.inventory.grammar_queries import (  # noqa: F401
    list_by_cefr,
    list_by_guidewords,
)
from app.schemas.english.inventory.grammar import GrammarProfile  # noqa: F401


def upsert_grammar_profile(
    graph: falkordb.Graph,
    *,
    guideword: str,
    cefr: str,
    super_category: str | None = None,
    sub_category: str | None = None,
    type_: str | None = None,
    can_do: str | None = None,
    example: str | None = None,
    lexical_range: str | None = None,
) -> None:
    """Create or update GrammarProfile and link to CefrLevel. Idempotent."""
    q = (
        "MERGE (g:GrammarProfile {guideword: $guideword}) "
        "ON CREATE SET g.super_category = $super_category, "
        "g.sub_category = $sub_category, g.type = $type, "
        "g.can_do = $can_do, g.example = $example, "
        "g.lexical_range = $lexical_range "
        "ON MATCH SET g.super_category = $super_category, "
        "g.sub_category = $sub_category, g.type = $type, "
        "g.can_do = $can_do, g.example = $example, "
        "g.lexical_range = $lexical_range "
        "WITH g MERGE (c:CefrLevel {code: $cefr}) "
        "MERGE (g)-[:GRAMMAR_LEVEL]->(c)"
    )
    graph.query(
        q,
        params={
            "guideword": guideword,
            "cefr": cefr.lower(),
            "super_category": super_category or "",
            "sub_category": sub_category or "",
            "type": type_ or "",
            "can_do": can_do or "",
            "example": example or "",
            "lexical_range": lexical_range or "",
        },
    )
