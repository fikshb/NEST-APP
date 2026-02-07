"""Add move_in_date and move_in_notes fields to deals

Revision ID: 003
Revises: 002
Create Date: 2025-01-03 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("deals", sa.Column("move_in_date", sa.Date, nullable=True))
    op.add_column("deals", sa.Column("move_in_notes", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("deals", "move_in_notes")
    op.drop_column("deals", "move_in_date")
