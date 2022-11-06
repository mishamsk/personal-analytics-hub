""" Nerdiary database models, maps to concrete polls. """

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import BIGINT, TEXT
from sqlalchemy.sql.sqltypes import TIMESTAMP

from ..db import Base

# Config model and constants
ND_SCHEMA_NAME = "nerddiary"


class PillLog(Base):
    __table_args__ = {"schema": ND_SCHEMA_NAME}

    poll_id: int = sa.Column(BIGINT, primary_key=True)
    user_id: int = sa.Column(BIGINT, primary_key=True)
    poll_ts: datetime = sa.Column(TIMESTAMP)
    drug_type: str = sa.Column(TEXT)
    drug_dose: str = sa.Column(TEXT)
    drug_purpose: str = sa.Column(TEXT)


class MorningLog(Base):
    __table_args__ = {"schema": ND_SCHEMA_NAME}

    poll_id: int = sa.Column(BIGINT, primary_key=True)
    user_id: int = sa.Column(BIGINT, primary_key=True)
    poll_ts: datetime = sa.Column(TIMESTAMP)
    fatigue: str = sa.Column(TEXT)
    slept_enough: str = sa.Column(TEXT)
    midnight_woke_up: str = sa.Column(TEXT)
    cramping: str = sa.Column(TEXT)
    awaken_by: str = sa.Column(TEXT)
    sleep_end_time: str = sa.Column(TEXT)
    sleep_start_time: str = sa.Column(TEXT)


class HeadacheMikeLog(Base):
    __table_args__ = {"schema": ND_SCHEMA_NAME}

    poll_id: int = sa.Column(BIGINT, primary_key=True)
    user_id: int = sa.Column(BIGINT, primary_key=True)
    poll_ts: datetime = sa.Column(TIMESTAMP)
    drug_dose: str = sa.Column(TEXT)
    drug_helped: str = sa.Column(TEXT)
    comment: str = sa.Column(TEXT)
    end_time: str = sa.Column(TEXT)
    drug_used: str = sa.Column(TEXT)
    start_time: str = sa.Column(TEXT)
    drug_type: str = sa.Column(TEXT)
    headache_type: str = sa.Column(TEXT)


class HeadacheMariaLog(Base):
    __table_args__ = {"schema": ND_SCHEMA_NAME}

    poll_id: int = sa.Column(BIGINT, primary_key=True)
    user_id: int = sa.Column(BIGINT, primary_key=True)
    poll_ts: datetime = sa.Column(TIMESTAMP)
    drug_dose: str = sa.Column(TEXT)
    drug_helped: str = sa.Column(TEXT)
    drug_type: str = sa.Column(TEXT)
    comment: str = sa.Column(TEXT)
    end_time: str = sa.Column(TEXT)
    drug_used: str = sa.Column(TEXT)
    start_time: str = sa.Column(TEXT)
    preiod_day: str = sa.Column(TEXT)
    period: str = sa.Column(TEXT)
    headache_type: str = sa.Column(TEXT)
