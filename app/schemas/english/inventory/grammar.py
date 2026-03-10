"""Response schema for GrammarProfile (inventory)."""

from __future__ import annotations

from pydantic import BaseModel


class GrammarProfile(BaseModel):
    """Grammar profile node (guideword, categories, CEFR)."""

    guideword: str
    super_category: str | None
    sub_category: str | None
    type: str | None
    can_do: str | None = None
    example: str | None = None
    lexical_range: str | None = None
    cefr_level: str | None = None
