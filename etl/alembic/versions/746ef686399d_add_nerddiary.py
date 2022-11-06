""" Add NerdDiary

Revision ID: 746ef686399d
Revises: 3689d60a53ba
Create Date: 2022-11-06 03:38:49.889875

"""
import sqlalchemy as sa
from alembic import op
from loader.nerddiary.models import ND_SCHEMA_NAME

# revision identifiers, used by Alembic.
revision = "746ef686399d"
down_revision = "3689d60a53ba"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {ND_SCHEMA_NAME}")

    op.create_table(
        "headache_maria_log",
        sa.Column("poll_id", sa.BIGINT(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.BIGINT(), nullable=False, primary_key=True),
        sa.Column("poll_ts", sa.TIMESTAMP(), nullable=True),
        sa.Column("drug_dose", sa.TEXT(), nullable=True),
        sa.Column("drug_helped", sa.TEXT(), nullable=True),
        sa.Column("comment", sa.TEXT(), nullable=True),
        sa.Column("end_time", sa.TEXT(), nullable=True),
        sa.Column("drug_used", sa.TEXT(), nullable=True),
        sa.Column("start_time", sa.TEXT(), nullable=True),
        sa.Column("drug_type", sa.TEXT(), nullable=True),
        sa.Column("preiod_day", sa.TEXT(), nullable=True),
        sa.Column("period", sa.TEXT(), nullable=True),
        sa.Column("headache_type", sa.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint("poll_id", "user_id", name=op.f("pk_headache_maria_log")),
        schema=ND_SCHEMA_NAME,
    )
    op.create_table(
        "headache_mike_log",
        sa.Column("poll_id", sa.BIGINT(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.BIGINT(), nullable=False, primary_key=True),
        sa.Column("poll_ts", sa.TIMESTAMP(), nullable=True),
        sa.Column("drug_dose", sa.TEXT(), nullable=True),
        sa.Column("drug_helped", sa.TEXT(), nullable=True),
        sa.Column("comment", sa.TEXT(), nullable=True),
        sa.Column("end_time", sa.TEXT(), nullable=True),
        sa.Column("drug_used", sa.TEXT(), nullable=True),
        sa.Column("start_time", sa.TEXT(), nullable=True),
        sa.Column("drug_type", sa.TEXT(), nullable=True),
        sa.Column("headache_type", sa.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint("poll_id", "user_id", name=op.f("pk_headache_mike_log")),
        schema=ND_SCHEMA_NAME,
    )
    op.create_table(
        "morning_log",
        sa.Column("poll_id", sa.BIGINT(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.BIGINT(), nullable=False, primary_key=True),
        sa.Column("poll_ts", sa.TIMESTAMP(), nullable=True),
        sa.Column("fatigue", sa.TEXT(), nullable=True),
        sa.Column("slept_enough", sa.TEXT(), nullable=True),
        sa.Column("midnight_woke_up", sa.TEXT(), nullable=True),
        sa.Column("cramping", sa.TEXT(), nullable=True),
        sa.Column("awaken_by", sa.TEXT(), nullable=True),
        sa.Column("sleep_end_time", sa.TEXT(), nullable=True),
        sa.Column("sleep_start_time", sa.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint("poll_id", "user_id", name=op.f("pk_morning_log")),
        schema=ND_SCHEMA_NAME,
    )
    op.create_table(
        "pill_log",
        sa.Column("poll_id", sa.BIGINT(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.BIGINT(), nullable=False, primary_key=True),
        sa.Column("poll_ts", sa.TIMESTAMP(), nullable=True),
        sa.Column("drug_type", sa.TEXT(), nullable=True),
        sa.Column("drug_dose", sa.TEXT(), nullable=True),
        sa.Column("drug_purpose", sa.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint("poll_id", "user_id", name=op.f("pk_pill_log")),
        schema=ND_SCHEMA_NAME,
    )


def downgrade() -> None:
    op.drop_table("pill_log", schema=ND_SCHEMA_NAME)
    op.drop_table("morning_log", schema=ND_SCHEMA_NAME)
    op.drop_table("headache_mike_log", schema=ND_SCHEMA_NAME)
    op.drop_table("headache_maria_log", schema=ND_SCHEMA_NAME)

    op.execute(f"DROP SCHEMA {ND_SCHEMA_NAME}")
