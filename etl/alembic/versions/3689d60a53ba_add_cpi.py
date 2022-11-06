"""Add CPI

Revision ID: 3689d60a53ba
Revises: 501b15b2071c
Create Date: 2022-09-19 20:18:07.464874

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3689d60a53ba"
down_revision = "501b15b2071c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cpi",
        sa.Column("date", sa.TIMESTAMP(), nullable=False, primary_key=True),
        sa.Column("area_code", sa.String(length=4), nullable=False, primary_key=True),
        sa.Column("item_code", sa.String(length=7), nullable=False, primary_key=True),
        sa.Column("value", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("footnotes", sa.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint("date", "area_code", "item_code", name=op.f("pk_cpi")),
        schema="economy",
    )


def downgrade() -> None:
    op.drop_table("cpi", schema="economy")
