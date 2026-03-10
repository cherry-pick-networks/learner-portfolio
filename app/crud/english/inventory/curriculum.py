"""Curriculum: upsert session/units; re-export queries."""

from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.curriculum import (
    Curriculum,
    CurriculumSession,
    CurriculumSessionUnit,
)


def _replace_units(
    session: Session,
    session_id: int,
    book_units: list[str],
) -> None:
    """Delete existing CurriculumSessionUnits for session_id; add new ones."""
    for unit in session.exec(
        select(CurriculumSessionUnit).where(
            CurriculumSessionUnit.session_id == session_id
        )
    ).all():
        session.delete(unit)
    for set_id in book_units:
        session.add(
            CurriculumSessionUnit(
                session_id=session_id,
                set_id=set_id,
            )
        )


def upsert(
    session: Session,
    *,
    curriculum_id: str,
    session_number: int,
    topic: str,
    book_units: list[str],
) -> None:
    """Create or update a curriculum session. Idempotent."""
    curriculum = session.exec(
        select(Curriculum).where(Curriculum.curriculum_id == curriculum_id)
    ).first()
    if curriculum is None:
        curriculum = Curriculum(curriculum_id=curriculum_id)
        session.add(curriculum)
        session.flush()

    existing_session = session.exec(
        select(CurriculumSession).where(
            CurriculumSession.curriculum_id == curriculum_id,
            CurriculumSession.session_number == session_number,
        )
    ).first()
    if existing_session is None:
        existing_session = CurriculumSession(
            curriculum_id=curriculum_id,
            session_number=session_number,
            topic=topic,
        )
        session.add(existing_session)
        session.flush()
    else:
        existing_session.topic = topic
        session.add(existing_session)

    _replace_units(session, existing_session.id, book_units)  # type: ignore[arg-type]
    session.commit()
