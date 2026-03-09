"""CefrLevel node helpers for FalkorDB inventory graph."""

from __future__ import annotations

import falkordb
from sqlmodel import Session, select

from app.models.common.concept import Concept


def ensure_cefr_levels(graph: falkordb.Graph, session: Session) -> None:
    """Ensure CefrLevel nodes from Concept (scheme_id=cefr). Idempotent."""
    stmt = (
        select(Concept.level)
        .where(Concept.scheme_id == "cefr")
        .order_by(Concept.level)
    )
    rows = session.exec(stmt).all()
    for level in rows:
        graph.query(
            "MERGE (c:CefrLevel {code: $code})",
            params={"code": level},
        )
