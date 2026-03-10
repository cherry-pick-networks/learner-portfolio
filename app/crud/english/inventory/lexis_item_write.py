"""LexisItem graph: upsert and link to CefrLevel, LexisProfile."""

from __future__ import annotations

import falkordb


def upsert_lexis_item(
    graph: falkordb.Graph,
    *,
    item_id: str,
    headword: str,
    pos: str | None,
    definition: str,
) -> None:
    """Create or update LexisItem node. Idempotent."""
    q = (
        "MERGE (i:LexisItem {item_id: $item_id}) "
        "ON CREATE SET i.headword = $headword, i.pos = $pos, "
        "i.definition = $definition "
        "ON MATCH SET i.headword = $headword, i.pos = $pos, "
        "i.definition = $definition"
    )
    graph.query(
        q,
        params={
            "item_id": item_id,
            "headword": headword,
            "pos": pos or "",
            "definition": definition or "",
        },
    )


def link_cefr(
    graph: falkordb.Graph,
    *,
    item_id: str,
    cefr: str,
) -> None:
    """Link LexisItem to CefrLevel via LEXIS_LEVEL. Idempotent."""
    q = (
        "MATCH (i:LexisItem {item_id: $item_id}) "
        "MERGE (c:CefrLevel {code: $cefr}) "
        "MERGE (i)-[:LEXIS_LEVEL]->(c)"
    )
    graph.query(q, params={"item_id": item_id, "cefr": cefr.lower()})


def link_profile(
    graph: falkordb.Graph,
    *,
    item_id: str,
    headword: str,
) -> None:
    """Link LexisItem to LexisProfile (HAS_PROFILE). No-op if absent."""
    q = (
        "MATCH (i:LexisItem {item_id: $item_id}), "
        "(l:LexisProfile {headword: $headword}) "
        "MERGE (i)-[:HAS_PROFILE]->(l)"
    )
    graph.query(q, params={"item_id": item_id, "headword": headword})
