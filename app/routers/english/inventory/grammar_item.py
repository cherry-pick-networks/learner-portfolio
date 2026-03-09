from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.sqlite import get_session
from app.crud.english.inventory import grammar_item as crud
from app.models.english.grammar_item import GrammarItemRead

router = APIRouter(prefix="/grammar-items", tags=["inventory_grammar_item"])


@router.get(
    "/{curriculum_id}",
    response_model=list[GrammarItemRead],
)
def list_sessions(
    curriculum_id: str,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[GrammarItemRead]:
    return crud.list_by_curriculum(session, curriculum_id)


@router.get(
    "/{curriculum_id}/{session_number}",
    response_model=GrammarItemRead,
)
def get_session(
    curriculum_id: str,
    session_number: int,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> GrammarItemRead:
    item = crud.get(session, curriculum_id, session_number)
    if item is None:
        raise HTTPException(status_code=404, detail="Not found")
    return item
