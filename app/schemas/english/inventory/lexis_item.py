"""Response schemas for LexisItem (inventory)."""

from __future__ import annotations

from pydantic import BaseModel


class LexisItemSchema(BaseModel):
    """Response schema for a single lexis set item."""

    item_id: str
    headword: str
    pos: str | None
    definition: str
    cefr: str | None = None


class LexisItemWithProfile(LexisItemSchema):
    """LexisItem with optional LexisProfile (total_freq, total_nb_doc)."""

    total_freq: float | None = None
    total_nb_doc: int | None = None
