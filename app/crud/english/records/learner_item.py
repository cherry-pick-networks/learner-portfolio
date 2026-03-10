from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlmodel import Session, select

from app.core.fsrs import initialise_item, schedule_item
from app.models.english.fsrs_config import FsrsConfig
from app.models.english.learner_item import LearnerItem

ITEM_TYPE_LEXIS = "lexis"
ITEM_TYPE_TASK_ITEM = "task_item"


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
    response_rating: int,
) -> LearnerItem:
    """Upsert FSRS state for a task_item (item_type=task_item)."""
    return _upsert(
        session,
        learner_id=learner_id,
        item_type=ITEM_TYPE_TASK_ITEM,
        item_id=task_item_id,
        response_rating=response_rating,
    )


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
    response_rating: int,
) -> LearnerItem:
    """Upsert FSRS state for a lexis item (item_type=lexis)."""
    return _upsert(
        session,
        learner_id=learner_id,
        item_type=ITEM_TYPE_LEXIS,
        item_id=item_id,
        response_rating=response_rating,
    )


def _upsert(
    session: Session,
    *,
    learner_id: str,
    item_type: str,
    item_id: str,
    response_rating: int,
) -> LearnerItem:
    row = session.exec(
        select(LearnerItem).where(
            LearnerItem.learner_id == learner_id,
            LearnerItem.item_type == item_type,
            LearnerItem.item_id == item_id,
        )
    ).first()
    w_vector_json: str | None = None
    config = session.exec(
        select(FsrsConfig).where(FsrsConfig.learner_id == learner_id)
    ).first()
    if config:
        w_vector_json = config.w_vector
    if row is None:
        fsrs_state = initialise_item()
        fsrs_state, due_date, stability, difficulty, retrievability = (
            schedule_item(fsrs_state, response_rating, w_vector_json)
        )
        row = LearnerItem(
            learner_id=learner_id,
            item_type=item_type,
            item_id=item_id,
            fsrs_state=fsrs_state,
            stability=stability,
            difficulty=difficulty,
            due_date=due_date,
            retrievability=retrievability,
        )
        session.add(row)
    else:
        fsrs_state = row.fsrs_state or initialise_item()
        fsrs_state, due_date, stability, difficulty, retrievability = (
            schedule_item(fsrs_state, response_rating, w_vector_json)
        )
        row.fsrs_state = fsrs_state
        row.stability = stability
        row.difficulty = difficulty
        row.due_date = due_date
        row.retrievability = retrievability
        session.add(row)
    session.commit()
    session.refresh(row)
    return row
