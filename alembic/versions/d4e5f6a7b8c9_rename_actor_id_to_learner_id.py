"""rename_actor_id_to_learner_id

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-10 18:00:00.000000

Rename recall_event.actor_id to learner_id for consistency.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "recall_event",
        "actor_id",
        new_column_name="learner_id",
    )


def downgrade() -> None:
    op.alter_column(
        "recall_event",
        "learner_id",
        new_column_name="actor_id",
    )
