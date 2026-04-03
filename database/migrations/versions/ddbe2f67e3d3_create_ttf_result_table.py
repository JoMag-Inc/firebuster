"""create_ttf_result_table

Revision ID: ddbe2f67e3d3
Revises: a02d9b7d413c
Create Date: 2026-03-31 05:43:41.394669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ddbe2f67e3d3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ttfresult",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ttf_minutes", sa.JSON(), nullable=False),
        sa.Column("weather_input", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("ttfresult")
