"""unify_learner_items

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-10 16:00:00.000000

Unify review_schedule and lexis_review_schedule into learner_item.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text
from sqlmodel.sql import sqltypes

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "learner_item",
        sa.Column("learner_id", sqltypes.AutoString(), nullable=False),
        sa.Column("item_type", sqltypes.AutoString(), nullable=False),
        sa.Column("item_id", sqltypes.AutoString(), nullable=False),
        sa.Column("fsrs_state", sa.Text(), nullable=True),
        sa.Column("stability", sa.Float(), nullable=False),
        sa.Column("difficulty", sa.Float(), nullable=False),
        sa.Column("due_date", sa.DateTime(), nullable=False),
        sa.Column("retrievability", sa.Float(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "learner_id",
            "item_type",
            "item_id",
            name="uq_learner_item_learner_id_item_type_item_id",
        ),
    )
    op.create_index(
        op.f("ix_learner_item_learner_id"),
        "learner_item",
        ["learner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learner_item_item_type"),
        "learner_item",
        ["item_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learner_item_item_id"),
        "learner_item",
        ["item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learner_item_due_date"),
        "learner_item",
        ["due_date"],
        unique=False,
    )

    conn = op.get_bind()
    conn.execute(
        text("""
            INSERT INTO learner_item
                (learner_id, item_type, item_id, fsrs_state, stability,
                 difficulty, due_date, retrievability)
            SELECT learner_id, 'task_item', task_item_id, card_state,
                   stability, difficulty, due_date, retrievability
            FROM review_schedule
        """)
    )
    conn.execute(
        text("""
            INSERT INTO learner_item
                (learner_id, item_type, item_id, fsrs_state, stability,
                 difficulty, due_date, retrievability)
            SELECT learner_id, 'lexis', item_id, card_state,
                   stability, difficulty, due_date, retrievability
            FROM lexis_review_schedule
        """)
    )

    op.drop_table("review_schedule")
    op.drop_table("lexis_review_schedule")


def downgrade() -> None:
    op.create_table(
        "review_schedule",
        sa.Column("learner_id", sqltypes.AutoString(), nullable=False),
        sa.Column("task_item_id", sqltypes.AutoString(), nullable=False),
        sa.Column("card_state", sa.Text(), nullable=True),
        sa.Column("stability", sa.Float(), nullable=False),
        sa.Column("difficulty", sa.Float(), nullable=False),
        sa.Column("due_date", sa.DateTime(), nullable=False),
        sa.Column("retrievability", sa.Float(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_review_schedule_learner_id"),
        "review_schedule",
        ["learner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_review_schedule_task_item_id"),
        "review_schedule",
        ["task_item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_review_schedule_due_date"),
        "review_schedule",
        ["due_date"],
        unique=False,
    )

    op.create_table(
        "lexis_review_schedule",
        sa.Column("learner_id", sqltypes.AutoString(), nullable=False),
        sa.Column("item_id", sqltypes.AutoString(), nullable=False),
        sa.Column("card_state", sa.Text(), nullable=True),
        sa.Column("stability", sa.Float(), nullable=False),
        sa.Column("difficulty", sa.Float(), nullable=False),
        sa.Column("due_date", sa.DateTime(), nullable=False),
        sa.Column("retrievability", sa.Float(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_lexis_review_schedule_learner_id"),
        "lexis_review_schedule",
        ["learner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lexis_review_schedule_item_id"),
        "lexis_review_schedule",
        ["item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lexis_review_schedule_due_date"),
        "lexis_review_schedule",
        ["due_date"],
        unique=False,
    )

    conn = op.get_bind()
    conn.execute(
        text("""
            INSERT INTO review_schedule
                (learner_id, task_item_id, card_state, stability,
                 difficulty, due_date, retrievability)
            SELECT learner_id, item_id, fsrs_state, stability,
                   difficulty, due_date, retrievability
            FROM learner_item
            WHERE item_type = 'task_item'
        """)
    )
    conn.execute(
        text("""
            INSERT INTO lexis_review_schedule
                (learner_id, item_id, card_state, stability,
                 difficulty, due_date, retrievability)
            SELECT learner_id, item_id, fsrs_state, stability,
                   difficulty, due_date, retrievability
            FROM learner_item
            WHERE item_type = 'lexis'
        """)
    )

    op.drop_table("learner_item")
