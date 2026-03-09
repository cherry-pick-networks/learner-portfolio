from __future__ import annotations

from sqlmodel import Field, SQLModel


class LinkType(SQLModel, table=True):
    """Relationship type for concept/object graph (tagged_with, belongs_to)."""

    __tablename__ = "common_link_type"
    id: str = Field(primary_key=True)
