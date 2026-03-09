from __future__ import annotations

from sqlmodel import Field, SQLModel


class Concept(SQLModel, table=True):
    """Allowed level within a scheme. Classification must reference these."""

    __tablename__ = "common_concept"
    scheme_id: str = Field(
        primary_key=True, foreign_key="common_object_type.id"
    )
    level: str = Field(primary_key=True)
