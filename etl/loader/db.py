from __future__ import annotations

import re

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base

meta = sa.MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


class _Base:
    @declared_attr
    def __tablename__(cls) -> str:
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)  # type: ignore
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


Base = declarative_base(metadata=meta, cls=_Base)
