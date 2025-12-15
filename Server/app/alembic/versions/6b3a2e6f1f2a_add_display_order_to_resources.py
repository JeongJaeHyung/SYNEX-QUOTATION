"""Add display_order to resources

Revision ID: 6b3a2e6f1f2a
Revises: 3c7a8a4bb0d2
Create Date: 2025-12-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6b3a2e6f1f2a"
down_revision: Union[str, None] = "3c7a8a4bb0d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("resources", sa.Column("display_order", sa.Integer(), nullable=True))

    # Backfill using insert order approximation (created_at ASC). Ties are broken by PK.
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                maker_id,
                row_number() OVER (
                    ORDER BY created_at ASC, maker_id ASC, id ASC
                ) - 1 AS rn
            FROM resources
        )
        UPDATE resources r
        SET display_order = ranked.rn
        FROM ranked
        WHERE r.id = ranked.id
          AND r.maker_id = ranked.maker_id
        """
    )

    op.alter_column(
        "resources",
        "display_order",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        "ix_resources_display_order",
        "resources",
        ["display_order"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_resources_display_order", table_name="resources")
    op.drop_column("resources", "display_order")
