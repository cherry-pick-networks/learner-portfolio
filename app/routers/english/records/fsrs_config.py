from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, SQLModel

from app.core.auth import verify_token
from app.core.sqlite import get_session
from app.crud.english.records import fsrs_config as crud
from app.models.english.fsrs_config import FsrsConfigRead

router = APIRouter(prefix="/fsrs/config", tags=["fsrs_config"])


class FsrsConfigUpdateBody(SQLModel):
    model_weights: str


@router.get("/{learner_id}", response_model=FsrsConfigRead | None)
def get_fsrs_config(
    learner_id: str,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> FsrsConfigRead | None:
    return crud.get_fsrs_config(session, learner_id)  # type: ignore[return-value]


@router.put("/{learner_id}", response_model=FsrsConfigRead)
def upsert_fsrs_config(
    learner_id: str,
    body: FsrsConfigUpdateBody,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> FsrsConfigRead:
    return crud.upsert_fsrs_config(  # type: ignore[return-value]
        session, learner_id, body.model_weights
    )
