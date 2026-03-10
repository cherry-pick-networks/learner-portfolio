"""normalize_book_units

Revision ID: a1b2c3d4e5f6
Revises: 977959203a40
Create Date: 2026-03-10 14:00:00.000000

Normalize grammar_item.book_units from "book-grammar-{source}:unit_{n}"
to GrammaticalSet set_id format "{source}-unit-{n:02d}".

"""

from __future__ import annotations

import json
import re
from typing import Sequence, Union

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "977959203a40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_OLD_PATTERN = re.compile(r"^book-grammar-(.+):unit_(\d+)$")
_SET_ID_PATTERN = re.compile(r"^(.+)-unit-(\d{2})$")


def _to_set_id(ref: str) -> str:
    """Convert book-grammar-{source}:unit_{n} to {source}-unit-{n:02d}."""
    m = _OLD_PATTERN.match(ref.strip())
    if m:
        source, num = m.group(1), int(m.group(2))
        return f"{source}-unit-{num:02d}"
    return ref


def _to_legacy(ref: str) -> str:
    """Convert {source}-unit-{nn} to book-grammar-{source}:unit_{n}."""
    m = _SET_ID_PATTERN.match(ref.strip())
    if m:
        source, nn = m.group(1), int(m.group(2))
        return f"book-grammar-{source}:unit_{nn}"
    return ref


def upgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(
        text("SELECT id, book_units FROM grammar_item")
    ).fetchall()
    for row in rows:
        row_id, book_units_str = row[0], row[1]
        try:
            units = json.loads(book_units_str or "[]")
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(units, list):
            continue
        normalized = [str(_to_set_id(u)) for u in units if isinstance(u, str)]
        new_json = json.dumps(normalized)
        conn.execute(
            text("UPDATE grammar_item SET book_units = :val WHERE id = :id"),
            {"val": new_json, "id": row_id},
        )


def downgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(
        text("SELECT id, book_units FROM grammar_item")
    ).fetchall()
    for row in rows:
        row_id, book_units_str = row[0], row[1]
        try:
            units = json.loads(book_units_str or "[]")
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(units, list):
            continue
        legacy = [str(_to_legacy(u)) for u in units if isinstance(u, str)]
        new_json = json.dumps(legacy)
        conn.execute(
            text("UPDATE grammar_item SET book_units = :val WHERE id = :id"),
            {"val": new_json, "id": row_id},
        )
