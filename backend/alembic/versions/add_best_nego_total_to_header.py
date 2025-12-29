"""add_best_nego_total_to_header

Revision ID: f1234567890a
Revises: ee387dbc2598
Create Date: 2025-12-26 15:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1234567890a"
down_revision: str | None = "ee387dbc2598"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add best_nego_total column to header table
    op.add_column("header", sa.Column("best_nego_total", sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove best_nego_total column from header table
    op.drop_column("header", "best_nego_total")
