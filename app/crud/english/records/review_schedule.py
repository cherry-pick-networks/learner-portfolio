"""Task-item review schedule (FSRS): list and upsert."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlmodel import Session, select

from app.crud.english.records._fsrs_upsert import (
    ITEM_TYPE_TASK_ITEM,
    fsrs_upsert,
)
from app.models.english.learner_item import LearnerItem


def list_review_schedule(
    session: Session, learner_id: str
) -> list[LearnerItem]:
    """List all task_item learner items for a learner."""
    return list(
        session.exec(
            select(LearnerItem)
            .where(LearnerItem.learner_id == learner_id)
            .where(LearnerItem.item_type == ITEM_TYPE_TASK_ITEM)
        ).all()
    )


def list_due_items(
    session: Session,
    learner_id: str,
    as_of: datetime | None = None,
) -> list[LearnerItem]:
    """List due task_item items (due_date <= as_of)."""
    if as_of is None:
        as_of = datetime.now(ZoneInfo("UTC"))
    return list(
        session.exec(
            select(LearnerItem)
            .where(LearnerItem.learner_id == learner_id)
            .where(LearnerItem.item_type == ITEM_TYPE_TASK_ITEM)
            .where(LearnerItem.due_date <= as_of)
        ).all()
    )


def upsert_review_schedule(
    session: Session,
    learner_id: str,
    task_item_id: str,
    attempt_quality: int,
) -> LearnerItem:
    """Upsert FSRS state for a task_item (item_type=task_item)."""
    return fsrs_upsert(
        session,
        learner_id=learner_id,
        item_type=ITEM_TYPE_TASK_ITEM,
        item_id=task_item_id,
        attempt_quality=attempt_quality,
    )
