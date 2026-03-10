"""add_lexis_review_schedule

Revision ID: 977959203a40
Revises: 866116224ac8
Create Date: 2026-03-10 12:07:34.366098

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlmodel.sql import sqltypes

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "977959203a40"
down_revision: Union[str, Sequence[str], None] = "866116224ac8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
        op.f("ix_lexis_review_schedule_due_date"),
        "lexis_review_schedule",
        ["due_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lexis_review_schedule_item_id"),
        "lexis_review_schedule",
        ["item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lexis_review_schedule_learner_id"),
        "lexis_review_schedule",
        ["learner_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_lexis_review_schedule_learner_id"),
        table_name="lexis_review_schedule",
    )
    op.drop_index(
        op.f("ix_lexis_review_schedule_item_id"),
        table_name="lexis_review_schedule",
    )
    op.drop_index(
        op.f("ix_lexis_review_schedule_due_date"),
        table_name="lexis_review_schedule",
    )
    op.drop_table("lexis_review_schedule")
