"""Curriculum: list and get (read-only)."""

from __future__ import annotations

from sqlmodel import Session, col, select

from app.models.english.curriculum import (
    CurriculumSession,
    CurriculumSessionUnit,
)
from app.schemas.english.inventory.curriculum import GrammarItemRead


def list_by_curriculum(
    session: Session, curriculum_id: str
) -> list[GrammarItemRead]:
    rows = session.exec(
        select(CurriculumSession)
        .where(CurriculumSession.curriculum_id == curriculum_id)
        .order_by(col(CurriculumSession.session_number))
    ).all()
    result: list[GrammarItemRead] = []
    for row in rows:
        units = session.exec(
            select(CurriculumSessionUnit.set_id).where(
                CurriculumSessionUnit.session_id == row.id
            )
        ).all()
        result.append(
            GrammarItemRead(
                id=row.id,  # type: ignore[arg-type]
                curriculum_id=row.curriculum_id,
                session_number=row.session_number,
                topic=row.topic,
                book_units=list(units),
            )
        )
    return result


def get(
    session: Session,
    curriculum_id: str,
    session_number: int,
) -> GrammarItemRead | None:
    row = session.exec(
        select(CurriculumSession).where(
            CurriculumSession.curriculum_id == curriculum_id,
            CurriculumSession.session_number == session_number,
        )
    ).first()
    if row is None:
        return None
    units = session.exec(
        select(CurriculumSessionUnit.set_id).where(
            CurriculumSessionUnit.session_id == row.id
        )
    ).all()
    return GrammarItemRead(
        id=row.id,  # type: ignore[arg-type]
        curriculum_id=row.curriculum_id,
        session_number=row.session_number,
        topic=row.topic,
        book_units=list(units),
    )
