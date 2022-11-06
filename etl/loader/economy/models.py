""" Source database models, mostly map to Drebdengi API models and add a couple of additional ones. """

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import BIGINT, TEXT
from sqlalchemy.sql.sqltypes import TIMESTAMP, Numeric, String

from ..db import Base

# Config model and constants
SCHEMA_NAME = "economy"


# Xchange rates
class XChangeRate(Base):
    __table_args__ = {"schema": SCHEMA_NAME}

    id: int = sa.Column(BIGINT, sa.Identity(cycle=True), primary_key=True)
    ts: datetime = sa.Column(TIMESTAMP)
    base_currency_code: str = sa.Column(String(3))
    currency_code: str = sa.Column(String(3))
    rate: float = sa.Column(Numeric(precision=10, scale=2))


# CPI data
class CPI(Base):
    __table_args__ = {"schema": SCHEMA_NAME}

    date: datetime = sa.Column(TIMESTAMP, primary_key=True)
    area_code: str = sa.Column(String(4), primary_key=True)
    item_code: str = sa.Column(String(7), primary_key=True)
    value: float = sa.Column(Numeric(precision=10, scale=2))
    footnotes: str = sa.Column(TEXT)
