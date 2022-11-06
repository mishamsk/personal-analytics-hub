""" Top level models for the loader app. """

from __future__ import annotations

import sqlalchemy as sa
from loader.db import Base
from loader.drebedengi import models as drebedengi_models  # noqa: F401
from loader.economy import models as economy_models  # noqa: F401
from loader.nerddiary import models as nerddiary_models  # noqa: F401
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.sql.sqltypes import String

# Config model and constants
SCHEMA_NAME = "loader"


class Config(Base):
    """Model for config table

    Args:
        param (str): Parameter name
        value (str): Parameter value
    """

    __table_args__ = {"schema": SCHEMA_NAME}

    param: str = sa.Column(String(50), primary_key=True)
    value: str = sa.Column(TEXT)
