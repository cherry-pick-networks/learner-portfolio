from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.falkordb import get_graph_conn
from app.crud.english.inventory.lexical_set import LexicalSetMeta, list_all
from app.crud.english.inventory.lexis_item import (
    LexisItemSchema,
    list_by_lexical_set,
)

router = APIRouter(prefix="/lexical-set", tags=["inventory_lexical_set"])


@router.get("", response_model=list[LexicalSetMeta])
def list_lexical_sets(
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[LexicalSetMeta]:
    return list_all(graph)


@router.get("/{set_id}", response_model=list[LexisItemSchema])
def get_lexical_set_items(
    set_id: str,
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[LexisItemSchema]:
    return list_by_lexical_set(graph, set_id)
