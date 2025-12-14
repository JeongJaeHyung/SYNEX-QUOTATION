"""Add order_index to machine_resources

Revision ID: 3c7a8a4bb0d2
Revises: 26232116a2b1
Create Date: 2025-12-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3c7a8a4bb0d2"
down_revision: Union[str, None] = "26232116a2b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("machine_resources", sa.Column("order_index", sa.Integer(), nullable=True))

    op.execute(
        """
        WITH ranked AS (
            SELECT
                machine_id,
                maker_id,
                resources_id,
                row_number() OVER (
                    PARTITION BY machine_id
                    ORDER BY maker_id ASC, resources_id ASC
                ) - 1 AS rn
            FROM machine_resources
        )
        UPDATE machine_resources mr
        SET order_index = ranked.rn
        FROM ranked
        WHERE mr.machine_id = ranked.machine_id
          AND mr.maker_id = ranked.maker_id
          AND mr.resources_id = ranked.resources_id
        """
    )

    op.alter_column(
        "machine_resources",
        "order_index",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_unique_constraint(
        "uq_machine_resources_machine_id_order_index",
        "machine_resources",
        ["machine_id", "order_index"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_machine_resources_machine_id_order_index",
        "machine_resources",
        type_="unique",
    )
    op.drop_column("machine_resources", "order_index")
