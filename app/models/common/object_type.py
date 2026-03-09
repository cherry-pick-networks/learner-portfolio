from __future__ import annotations

from sqlmodel import Field, SQLModel


class ObjectType(SQLModel, table=True):
    """Classification scheme or entity type (cefr, doctype, kice_source)."""

    __tablename__ = "common_object_type"
    id: str = Field(primary_key=True)
    name: str
