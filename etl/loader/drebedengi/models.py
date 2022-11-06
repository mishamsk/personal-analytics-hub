""" Drebedengi database models, map to Drebdengi API models. """

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from drebedengi.model import ActionType, ObjectType, TransactionType
from sqlalchemy.dialects.postgresql import BIGINT, TEXT
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean, Enum, Integer, Numeric, String

from ..db import Base

# Config model and constants
SCHEMA_NAME = "drebedengi"
LAST_LOADED_REVISION_KEY = "revision"


# Drebedengi API models
class Transaction(Base):
    __table_args__ = {"schema": SCHEMA_NAME}

    id: int = sa.Column(BIGINT, primary_key=True)
    budget_object_id: int = sa.Column(BIGINT)
    user_nuid: int = sa.Column(BIGINT)
    budget_family_id: int = sa.Column(BIGINT)
    is_loan_transfer: bool = sa.Column(Boolean)
    operation_date: datetime = sa.Column(TIMESTAMP)
    currency_id: int = sa.Column(BIGINT)
    operation_type: TransactionType = sa.Column(Enum(TransactionType))
    account_id: int = sa.Column(BIGINT)
    amount: int = sa.Column(Integer)
    comment: str | None = sa.Column(
        TEXT,
    )
    oper_utc_timestamp: datetime | None = sa.Column(TIMESTAMP)
    group_id: int | None = sa.Column(Integer)
    last_modified: datetime = sa.Column(TIMESTAMP)
    tombstone: datetime = sa.Column(TIMESTAMP)


class ChangeRecord(Base):
    __table_args__ = {"schema": SCHEMA_NAME}

    revision_id: int = sa.Column(BIGINT, primary_key=True)
    action_type: ActionType = sa.Column(Enum(ActionType))
    change_object_type: ObjectType = sa.Column(Enum(ObjectType))
    object_id: int = sa.Column(BIGINT)
    date: datetime = sa.Column(TIMESTAMP)
    last_modified: datetime = sa.Column(TIMESTAMP)


class ExpenseCategory(Base):
    __table_args__ = {"schema": SCHEMA_NAME}

    id: int = sa.Column(BIGINT, primary_key=True)
    parent_id: int = sa.Column(BIGINT)
    budget_family_id: int = sa.Column(BIGINT)
    object_type: ObjectType = sa.Column(Enum(ObjectType))
    name: str = sa.Column(String(255))
    is_hidden: bool = sa.Column(Boolean)
    sort: int = sa.Column(Integer)
    last_modified: datetime = sa.Column(TIMESTAMP)
    tombstone: datetime = sa.Column(TIMESTAMP)


class IncomeSource(Base):
    __table_args__ = {"schema": SCHEMA_NAME}

    id: int = sa.Column(BIGINT, primary_key=True)
    parent_id: int = sa.Column(BIGINT)
    budget_family_id: int = sa.Column(BIGINT)
    object_type: ObjectType = sa.Column(Enum(ObjectType))
    name: str = sa.Column(String(255))
    is_hidden: bool = sa.Column(Boolean)
    sort: int = sa.Column(Integer)
    last_modified: datetime = sa.Column(TIMESTAMP)
    tombstone: datetime = sa.Column(TIMESTAMP)


class Tag(Base):
    __table_args__ = {"schema": SCHEMA_NAME}

    id: int = sa.Column(BIGINT, primary_key=True)
    parent_id: int = sa.Column(BIGINT)
    budget_family_id: int = sa.Column(BIGINT)
    name: str = sa.Column(String(255))
    is_hidden: bool = sa.Column(Boolean)
    is_shared: bool = sa.Column(Boolean)
    sort: int = sa.Column(Integer)
    last_modified: datetime = sa.Column(TIMESTAMP)
    tombstone: datetime = sa.Column(TIMESTAMP)


class Currency(Base):
    __table_args__ = {"schema": SCHEMA_NAME}

    id: int = sa.Column(BIGINT, primary_key=True)
    user_name: str = sa.Column(String(255))
    currency_code: str = sa.Column(String(3))
    exchange_rate: float = sa.Column(Numeric(precision=10, scale=2))
    budget_family_id: int = sa.Column(BIGINT)
    is_default: bool = sa.Column(Boolean)
    is_autoupdate: bool = sa.Column(Boolean)
    is_hidden: bool = sa.Column(Boolean)
    last_modified: datetime = sa.Column(TIMESTAMP)
    tombstone: datetime = sa.Column(TIMESTAMP)


class Account(Base):
    __table_args__ = {"schema": SCHEMA_NAME}

    id: int = sa.Column(BIGINT, primary_key=True)
    budget_family_id: int = sa.Column(BIGINT)
    object_type: ObjectType = sa.Column(Enum(ObjectType))
    name: str = sa.Column(String(255))
    is_hidden: bool = sa.Column(Boolean)
    is_autohide: bool = sa.Column(Boolean)
    is_loan: bool = sa.Column(Boolean)
    sort: int = sa.Column(Integer)
    wallet_user_id: int | None = sa.Column(BIGINT)
    icon_id: str | None = sa.Column(TEXT)
    last_modified: datetime = sa.Column(TIMESTAMP)
    tombstone: datetime = sa.Column(TIMESTAMP)
