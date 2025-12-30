"""add_quotation_number_to_header

Revision ID: f1234567890b
Revises: f1234567890a
Create Date: 2025-12-30 12:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1234567890b"
down_revision: str | None = "f1234567890a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add quotation_number column to header table
    op.add_column("header", sa.Column("quotation_number", sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove quotation_number column from header table
    op.drop_column("header", "quotation_number")
