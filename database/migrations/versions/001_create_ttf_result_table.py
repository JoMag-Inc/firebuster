"""create_ttf_result_table

Revision ID: 001
Revises:
Create Date: 2026-04-05 12:00:00.000000

Creates the TTFResult table for storing Time To Flashover calculations
with associated weather data.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the ttfresult table with ttf_points column."""
    op.create_table(
        "ttfresult",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ttf_points", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    """Drop the ttfresult table."""
    op.drop_table("ttfresult")
