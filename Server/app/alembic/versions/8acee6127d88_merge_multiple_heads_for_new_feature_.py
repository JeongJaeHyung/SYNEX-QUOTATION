"""Merge multiple heads for new feature branch

Revision ID: 8acee6127d88
Revises: 7f5b2c1a9e31, 9b6422db51b7
Create Date: 2025-12-15 07:34:29.238804

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8acee6127d88'
down_revision: Union[str, None] = ('7f5b2c1a9e31', '9b6422db51b7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
