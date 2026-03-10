from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.sqlite import get_session
from app.crud.english.records import recall_event as crud
from app.models.english.recall_event import RecallEventCreate, RecallEventRead

router = APIRouter(prefix="/recall-event", tags=["recall-event"])


@router.post("", response_model=RecallEventRead)
def create_recall_event(
    body: RecallEventCreate,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> RecallEventRead:
    return crud.create_recall_event(session, body)  # type: ignore[return-value]


@router.get("/unprocessed", response_model=list[RecallEventRead])
def list_unprocessed_recall_events(
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[RecallEventRead]:
    return crud.list_unprocessed_recall_events(session)  # type: ignore[return-value]


@router.post("/{event_id}/mark-processed", response_model=RecallEventRead)
def mark_recall_event_processed(
    event_id: int,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> RecallEventRead:
    try:
        return crud.mark_processed(session, event_id)  # type: ignore[return-value]
    except ValueError:
        raise HTTPException(status_code=404, detail="not found")
