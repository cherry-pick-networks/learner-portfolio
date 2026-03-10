"""Lexis review schedule (FSRS): list and upsert."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlmodel import Session, select

from app.crud.english.records._fsrs_upsert import ITEM_TYPE_LEXIS, fsrs_upsert
from app.models.english.learner_item import LearnerItem


def list_lexis_review_schedule(
    session: Session, learner_id: str
) -> list[LearnerItem]:
    """List all lexis learner items for a learner."""
    return list(
        session.exec(
            select(LearnerItem)
            .where(LearnerItem.learner_id == learner_id)
            .where(LearnerItem.item_type == ITEM_TYPE_LEXIS)
        ).all()
    )


def list_due_lexis_items(
    session: Session,
    learner_id: str,
    as_of: datetime | None = None,
) -> list[LearnerItem]:
    """List due lexis items (due_date <= as_of)."""
    if as_of is None:
        as_of = datetime.now(ZoneInfo("UTC"))
    return list(
        session.exec(
            select(LearnerItem)
            .where(LearnerItem.learner_id == learner_id)
            .where(LearnerItem.item_type == ITEM_TYPE_LEXIS)
            .where(LearnerItem.due_date <= as_of)
        ).all()
    )


def upsert_lexis_review_schedule(
    session: Session,
    learner_id: str,
    item_id: str,
    attempt_quality: int,
) -> LearnerItem:
    """Upsert FSRS state for a lexis item (item_type=lexis)."""
    return fsrs_upsert(
        session,
        learner_id=learner_id,
        item_type=ITEM_TYPE_LEXIS,
        item_id=item_id,
        attempt_quality=attempt_quality,
    )
