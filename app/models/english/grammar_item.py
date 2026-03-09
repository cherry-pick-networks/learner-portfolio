from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class GrammarItemBase(SQLModel):
    curriculum_id: str = Field(index=True)
    session_number: int
    topic: str
    book_units: str  # JSON array: ["book-grammar-basic:unit_1", ...]


class GrammarItem(GrammarItemBase, table=True):
    __tablename__ = "grammar_item"
    __table_args__ = (UniqueConstraint("curriculum_id", "session_number"),)
    id: int | None = Field(default=None, primary_key=True)


class GrammarItemRead(SQLModel):
    id: int
    curriculum_id: str
    session_number: int
    topic: str
    book_units: list[str]
