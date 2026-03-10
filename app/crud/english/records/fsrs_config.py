from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.fsrs_config import FsrsConfig


def get_fsrs_config(session: Session, learner_id: str) -> FsrsConfig | None:
    return session.exec(
        select(FsrsConfig).where(FsrsConfig.learner_id == learner_id)
    ).first()


def upsert_fsrs_config(
    session: Session, learner_id: str, w_vector: str
) -> FsrsConfig:
    row = get_fsrs_config(session, learner_id)
    if row is None:
        row = FsrsConfig(learner_id=learner_id, w_vector=w_vector)
        session.add(row)
    else:
        row.w_vector = w_vector
        session.add(row)
    session.commit()
    session.refresh(row)
    return row
