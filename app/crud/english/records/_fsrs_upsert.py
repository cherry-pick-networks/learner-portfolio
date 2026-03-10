"""Shared FSRS upsert logic for learner_item (task_item and lexis)."""

from __future__ import annotations

from sqlmodel import Session, select

from app.core.fsrs import initialise_item_state, schedule_review
from app.models.english.fsrs_config import FsrsConfig
from app.models.english.learner_item import LearnerItem

ITEM_TYPE_LEXIS = "lexis"
ITEM_TYPE_TASK_ITEM = "task_item"


def fsrs_upsert(
    session: Session,
    *,
    learner_id: str,
    item_type: str,
    item_id: str,
    attempt_quality: int,
) -> LearnerItem:
    """Load or create LearnerItem, run FSRS schedule_review, commit, return."""
    row = session.exec(
        select(LearnerItem).where(
            LearnerItem.learner_id == learner_id,
            LearnerItem.item_type == item_type,
            LearnerItem.item_id == item_id,
        )
    ).first()
    model_weights_json: str | None = None
    config = session.exec(
        select(FsrsConfig).where(FsrsConfig.learner_id == learner_id)
    ).first()
    if config:
        model_weights_json = config.model_weights
    if row is None:
        item_state = initialise_item_state()
        (
            item_state,
            due_date,
            memory_stability,
            item_difficulty,
            retrievability,
        ) = schedule_review(item_state, attempt_quality, model_weights_json)
        row = LearnerItem(
            learner_id=learner_id,
            item_type=item_type,
            item_id=item_id,
            item_state=item_state,
            memory_stability=memory_stability,
            item_difficulty=item_difficulty,
            due_date=due_date,
            retrievability=retrievability,
        )
        session.add(row)
    else:
        item_state = row.item_state or initialise_item_state()
        (
            item_state,
            due_date,
            memory_stability,
            item_difficulty,
            retrievability,
        ) = schedule_review(item_state, attempt_quality, model_weights_json)
        row.item_state = item_state
        row.memory_stability = memory_stability
        row.item_difficulty = item_difficulty
        row.due_date = due_date
        row.retrievability = retrievability
        session.add(row)
    session.commit()
    session.refresh(row)
    return row
