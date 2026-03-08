from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.falkordb import get_graph_conn
from app.crud.english.inventory.lexis import LexicalItem, list_by_cefr

router = APIRouter(prefix="/lexis", tags=["inventory_lexis"])


@router.get("/{cefr}", response_model=list[LexicalItem])
def list_lexis_by_cefr(
    cefr: str,
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[LexicalItem]:
    return list_by_cefr(graph, cefr)
