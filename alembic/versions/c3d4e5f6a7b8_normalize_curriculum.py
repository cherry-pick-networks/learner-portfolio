"""normalize_curriculum

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-10 17:00:00.000000

Normalize grammar_item into curriculum, curriculum_session,
curriculum_session_unit.
"""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text
from sqlmodel.sql import sqltypes

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "curriculum",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("curriculum_id", sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "curriculum_id", name="uq_curriculum_curriculum_id"
        ),
    )
    op.create_index(
        op.f("ix_curriculum_curriculum_id"),
        "curriculum",
        ["curriculum_id"],
        unique=True,
    )

    op.create_table(
        "curriculum_session",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "curriculum_id",
            sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column("session_number", sa.Integer(), nullable=False),
        sa.Column("topic", sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["curriculum_id"],
            ["curriculum.curriculum_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "curriculum_id",
            "session_number",
            name="uq_curriculum_session_curriculum_id_session_number",
        ),
    )
    op.create_index(
        op.f("ix_curriculum_session_curriculum_id"),
        "curriculum_session",
        ["curriculum_id"],
        unique=False,
    )

    op.create_table(
        "curriculum_session_unit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("set_id", sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["curriculum_session.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_id",
            "set_id",
            name="uq_curriculum_session_unit_session_id_set_id",
        ),
    )
    op.create_index(
        op.f("ix_curriculum_session_unit_session_id"),
        "curriculum_session_unit",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_curriculum_session_unit_set_id"),
        "curriculum_session_unit",
        ["set_id"],
        unique=False,
    )

    conn = op.get_bind()
    rows = conn.execute(
        text(
            "SELECT id, curriculum_id, session_number, topic, book_units "
            "FROM grammar_item"
        )
    ).fetchall()
    seen_curricula: set[str] = set()
    for row in rows:
        gi_id, curriculum_id, session_number, topic, book_units_str = row
        if curriculum_id not in seen_curricula:
            conn.execute(
                text("INSERT INTO curriculum (curriculum_id) VALUES (:cid)"),
                {"cid": curriculum_id},
            )
            seen_curricula.add(curriculum_id)
        conn.execute(
            text("""
                INSERT INTO curriculum_session
                    (curriculum_id, session_number, topic)
                VALUES (:cid, :sn, :topic)
            """),
            {"cid": curriculum_id, "sn": session_number, "topic": topic or ""},
        )
        session_row = conn.execute(
            text("""
                SELECT id FROM curriculum_session
                WHERE curriculum_id = :cid AND session_number = :sn
            """),
            {"cid": curriculum_id, "sn": session_number},
        ).fetchone()
        if session_row:
            session_id = session_row[0]
            try:
                units = json.loads(book_units_str or "[]")
            except (json.JSONDecodeError, TypeError):
                units = []
            if not isinstance(units, list):
                units = []
            for set_id in units:
                if isinstance(set_id, str):
                    conn.execute(
                        text("""
                            INSERT INTO curriculum_session_unit
                                (session_id, set_id)
                            VALUES (:sid, :set_id)
                        """),
                        {"sid": session_id, "set_id": set_id},
                    )

    op.drop_index(
        op.f("ix_grammar_item_curriculum_id"), table_name="grammar_item"
    )
    op.drop_table("grammar_item")


def downgrade() -> None:
    op.create_table(
        "grammar_item",
        sa.Column("curriculum_id", sqltypes.AutoString(), nullable=False),
        sa.Column("session_number", sa.Integer(), nullable=False),
        sa.Column("topic", sqltypes.AutoString(), nullable=False),
        sa.Column("book_units", sqltypes.AutoString(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("curriculum_id", "session_number"),
    )
    op.create_index(
        op.f("ix_grammar_item_curriculum_id"),
        "grammar_item",
        ["curriculum_id"],
        unique=False,
    )

    conn = op.get_bind()
    sessions = conn.execute(
        text(
            "SELECT id, curriculum_id, session_number, topic "
            "FROM curriculum_session"
        )
    ).fetchall()
    for i, (session_id, curriculum_id, session_number, topic) in enumerate(
        sessions
    ):
        units = conn.execute(
            text(
                "SELECT set_id FROM curriculum_session_unit "
                "WHERE session_id = :sid"
            ),
            {"sid": session_id},
        ).fetchall()
        set_ids = [u[0] for u in units]
        book_units_json = json.dumps(set_ids)
        conn.execute(
            text("""
                INSERT INTO grammar_item
                    (id, curriculum_id, session_number, topic, book_units)
                VALUES (:id, :cid, :sn, :topic, :book_units)
            """),
            {
                "id": i + 1,
                "cid": curriculum_id,
                "sn": session_number,
                "topic": topic or "",
                "book_units": book_units_json,
            },
        )

    op.drop_table("curriculum_session_unit")
    op.drop_table("curriculum_session")
    op.drop_table("curriculum")
