"""add_review_schedule_card_state

Revision ID: 866116224ac8
Revises: 32c438b425b6
Create Date: 2026-03-10 11:57:57.775752

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "866116224ac8"
down_revision: Union[str, Sequence[str], None] = "32c438b425b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "review_schedule",
        sa.Column("card_state", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("review_schedule", "card_state")
