"""Resolve curriculum session to GrammarProfiles via GrammaticalSet."""

from __future__ import annotations

import falkordb
from sqlmodel import Session

from app.crud.english.inventory import curriculum as curriculum_crud
from app.crud.english.inventory import grammatical_set as grammatical_set_crud
from app.crud.english.inventory.grammar import GrammarProfile


def list_profiles_for_session(
    curriculum_id: str,
    session_number: int,
    session: Session,
    graph: falkordb.Graph,
) -> list[GrammarProfile]:
    """Return GrammarProfiles to study for the given curriculum session."""
    item = curriculum_crud.get(session, curriculum_id, session_number)
    if not item:
        return []
    return [
        profile
        for set_id in item.book_units
        for profile in grammatical_set_crud.list_by_grammatical_set(
            graph, set_id
        )
    ]
