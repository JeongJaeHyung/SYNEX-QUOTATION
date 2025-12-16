"""Add display fields to machine_resources

Revision ID: 7f5b2c1a9e31
Revises: 6b3a2e6f1f2a
Create Date: 2025-12-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7f5b2c1a9e31"
down_revision: Union[str, None] = "6b3a2e6f1f2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("machine_resources", sa.Column("display_major", sa.String(length=50), nullable=True))
    op.add_column("machine_resources", sa.Column("display_minor", sa.String(length=50), nullable=True))
    op.add_column("machine_resources", sa.Column("display_model_name", sa.String(length=100), nullable=True))
    op.add_column("machine_resources", sa.Column("display_maker_name", sa.String(length=100), nullable=True))
    op.add_column("machine_resources", sa.Column("display_unit", sa.String(length=10), nullable=True))


def downgrade() -> None:
    op.drop_column("machine_resources", "display_unit")
    op.drop_column("machine_resources", "display_maker_name")
    op.drop_column("machine_resources", "display_model_name")
    op.drop_column("machine_resources", "display_minor")
    op.drop_column("machine_resources", "display_major")

