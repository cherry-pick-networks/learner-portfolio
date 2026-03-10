"""rename_fsrs_columns_cambridge

Revision ID: f7a8b9c0d1e2
Revises: e5f6a7b8c9d0
Create Date: 2026-03-10 18:00:00.000000

Rename learner_item and fsrs_config columns to Cambridge terminology.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE learner_item RENAME COLUMN fsrs_state TO item_state"
    )
    op.execute(
        "ALTER TABLE learner_item RENAME COLUMN stability TO memory_stability"
    )
    op.execute(
        "ALTER TABLE learner_item RENAME COLUMN difficulty TO item_difficulty"
    )
    op.execute(
        "ALTER TABLE fsrs_config RENAME COLUMN w_vector TO model_weights"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE learner_item RENAME COLUMN item_state TO fsrs_state"
    )
    op.execute(
        "ALTER TABLE learner_item RENAME COLUMN memory_stability TO stability"
    )
    op.execute(
        "ALTER TABLE learner_item RENAME COLUMN item_difficulty TO difficulty"
    )
    op.execute(
        "ALTER TABLE fsrs_config RENAME COLUMN model_weights TO w_vector"
    )
