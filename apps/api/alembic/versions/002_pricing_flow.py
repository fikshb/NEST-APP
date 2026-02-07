"""Pricing flow: rename list_price to initial_price, make deal_price nullable

Revision ID: 002
Revises: 001
Create Date: 2025-01-02 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("deals", "list_price", new_column_name="initial_price")
    op.alter_column("deals", "deal_price", nullable=True)


def downgrade() -> None:
    op.alter_column("deals", "deal_price", nullable=False)
    op.alter_column("deals", "initial_price", new_column_name="list_price")
