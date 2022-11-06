"""Initial

Revision ID: 501b15b2071c
Revises:
Create Date: 2022-08-27 13:31:57.119132

"""
import sqlalchemy as sa
from alembic import op
from drebedengi.model import ActionType, ObjectType, TransactionType
from loader.drebedengi.models import SCHEMA_NAME as DREBEDENGI_SCHEMA_NAME
from loader.economy.models import SCHEMA_NAME as ECONOMY_SCHEMA_NAME
from loader.models import SCHEMA_NAME as LOADER_SCHEMA_NAME

# revision identifiers, used by Alembic.
revision = "501b15b2071c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {DREBEDENGI_SCHEMA_NAME}")
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {ECONOMY_SCHEMA_NAME}")
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {LOADER_SCHEMA_NAME}")

    op.create_table(
        "account",
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("budget_family_id", sa.BIGINT(), nullable=True),
        sa.Column(
            "object_type",
            sa.Enum(ObjectType),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), nullable=True),
        sa.Column("is_autohide", sa.Boolean(), nullable=True),
        sa.Column("is_loan", sa.Boolean(), nullable=True),
        sa.Column("sort", sa.Integer(), nullable=True),
        sa.Column("wallet_user_id", sa.BIGINT(), nullable=True),
        sa.Column("icon_id", sa.BIGINT(), nullable=True),
        sa.Column("last_modified", sa.TIMESTAMP, nullable=True),
        sa.Column("tombstone", sa.TIMESTAMP, nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account")),
        schema=DREBEDENGI_SCHEMA_NAME,
    )
    op.create_table(
        "change_record",
        sa.Column("revision_id", sa.BIGINT(), nullable=False),
        sa.Column("action_type", sa.Enum(ActionType), nullable=True),
        sa.Column(
            "change_object_type",
            sa.Enum(ObjectType),
            nullable=True,
        ),
        sa.Column("object_id", sa.BIGINT(), nullable=True),
        sa.Column("date", sa.TIMESTAMP(), nullable=True),
        sa.Column("last_modified", sa.TIMESTAMP, nullable=True),
        sa.PrimaryKeyConstraint("revision_id", name=op.f("pk_change_record")),
        schema=DREBEDENGI_SCHEMA_NAME,
    )
    op.create_table(
        "config",
        sa.Column("param", sa.String(length=50), nullable=False),
        sa.Column("value", sa.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint("param", name=op.f("pk_config")),
        schema=LOADER_SCHEMA_NAME,
    )
    op.create_table(
        "currency",
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("user_name", sa.String(length=255), nullable=True),
        sa.Column("currency_code", sa.String(length=3), nullable=True),
        sa.Column("exchange_rate", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("budget_family_id", sa.BIGINT(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=True),
        sa.Column("is_autoupdate", sa.Boolean(), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), nullable=True),
        sa.Column("last_modified", sa.TIMESTAMP, nullable=True),
        sa.Column("tombstone", sa.TIMESTAMP, nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_currency")),
        schema=DREBEDENGI_SCHEMA_NAME,
    )
    op.create_table(
        "expense_category",
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("parent_id", sa.BIGINT(), nullable=True),
        sa.Column("budget_family_id", sa.BIGINT(), nullable=True),
        sa.Column(
            "object_type",
            sa.Enum(ObjectType),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), nullable=True),
        sa.Column("sort", sa.Integer(), nullable=True),
        sa.Column("last_modified", sa.TIMESTAMP, nullable=True),
        sa.Column("tombstone", sa.TIMESTAMP, nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_expense_category")),
        schema=DREBEDENGI_SCHEMA_NAME,
    )
    op.create_table(
        "income_source",
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("parent_id", sa.BIGINT(), nullable=True),
        sa.Column("budget_family_id", sa.BIGINT(), nullable=True),
        sa.Column(
            "object_type",
            sa.Enum(ObjectType),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), nullable=True),
        sa.Column("sort", sa.Integer(), nullable=True),
        sa.Column("last_modified", sa.TIMESTAMP, nullable=True),
        sa.Column("tombstone", sa.TIMESTAMP, nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_income_source")),
        schema=DREBEDENGI_SCHEMA_NAME,
    )
    op.create_table(
        "tag",
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("parent_id", sa.BIGINT(), nullable=True),
        sa.Column("budget_family_id", sa.BIGINT(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), nullable=True),
        sa.Column("is_shared", sa.Boolean(), nullable=True),
        sa.Column("sort", sa.Integer(), nullable=True),
        sa.Column("last_modified", sa.TIMESTAMP, nullable=True),
        sa.Column("tombstone", sa.TIMESTAMP, nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tag")),
        schema=DREBEDENGI_SCHEMA_NAME,
    )
    op.create_table(
        "transaction",
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("budget_object_id", sa.BIGINT(), nullable=True),
        sa.Column("user_nuid", sa.BIGINT(), nullable=True),
        sa.Column("budget_family_id", sa.BIGINT(), nullable=True),
        sa.Column("is_loan_transfer", sa.Boolean(), nullable=True),
        sa.Column("operation_date", sa.TIMESTAMP(), nullable=True),
        sa.Column("currency_id", sa.BIGINT(), nullable=True),
        sa.Column(
            "operation_type",
            sa.Enum(TransactionType),
            nullable=True,
        ),
        sa.Column("account_id", sa.BIGINT(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=True),
        sa.Column("comment", sa.TEXT(), nullable=True),
        sa.Column("oper_utc_timestamp", sa.TIMESTAMP(), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("last_modified", sa.TIMESTAMP, nullable=True),
        sa.Column("tombstone", sa.TIMESTAMP, nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_transaction")),
        schema=DREBEDENGI_SCHEMA_NAME,
    )
    op.create_table(
        "x_change_rate",
        sa.Column("id", sa.BIGINT(), sa.Identity(always=False, cycle=True), nullable=False),
        sa.Column("ts", sa.TIMESTAMP(), nullable=True),
        sa.Column("base_currency_code", sa.String(length=3), nullable=True),
        sa.Column("currency_code", sa.String(length=3), nullable=True),
        sa.Column("rate", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_x_change_rate")),
        schema=ECONOMY_SCHEMA_NAME,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_table("x_change_rate", schema=ECONOMY_SCHEMA_NAME)
    op.drop_table("transaction", schema=DREBEDENGI_SCHEMA_NAME)
    op.drop_table("tag", schema=DREBEDENGI_SCHEMA_NAME)
    op.drop_table("income_source", schema=DREBEDENGI_SCHEMA_NAME)
    op.drop_table("expense_category", schema=DREBEDENGI_SCHEMA_NAME)
    op.drop_table("currency", schema=DREBEDENGI_SCHEMA_NAME)
    op.drop_table("config", schema=ECONOMY_SCHEMA_NAME)
    op.drop_table("change_record", schema=DREBEDENGI_SCHEMA_NAME)
    op.drop_table("account", schema=DREBEDENGI_SCHEMA_NAME)
    op.execute(f"DROP SCHEMA {ECONOMY_SCHEMA_NAME}")
    op.execute(f"DROP SCHEMA {LOADER_SCHEMA_NAME}")
    op.execute(f"DROP SCHEMA {DREBEDENGI_SCHEMA_NAME}")
