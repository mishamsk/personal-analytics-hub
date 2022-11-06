import logging
import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml
from dataclasses_json import DataClassJsonMixin
from dataclasses_json import config as dcj_config
from dotenv import dotenv_values
from marshmallow import fields

logger = logging.getLogger(__name__)


@dataclass
class CPIConfig(DataClassJsonMixin):
    """Configuration for CPI data."""

    start_date: date = field(
        default=date(1990, 1, 1),
        metadata=dcj_config(
            encoder=date.isoformat,
            decoder=date.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        ),
    )
    area_code: str = field(default="0000")
    item_codes: list[str] = field(default_factory=lambda: ["SA0"])


@dataclass
class Config(DataClassJsonMixin):
    DATABASE_URL: str = field(metadata=dcj_config(field_name="PAH_DATABASE_URL"))
    DREBEDENGI_API_KEY: str = field(metadata=dcj_config(field_name="PAH_DREBEDENGI_API_KEY"))
    DREBEDENGI_LOGIN: str = field(metadata=dcj_config(field_name="PAH_DREBEDENGI_LOGIN"))
    DREBEDENGI_PASSWORD: str = field(metadata=dcj_config(field_name="PAH_DREBEDENGI_PASSWORD"))
    NERDDIARY_API_ENDPOINT: str = field(
        metadata=dcj_config(field_name="PAH_NERDDIARY_API_ENDPOINT")
    )

    cpi_config: CPIConfig = field(default_factory=CPIConfig)


def load_config(path: Path | None = Path("config.yml")) -> Config:
    config_dict = {}

    # First load from path (least priority)
    if path is not None and path.exists():
        logger.info(f"Loading config from {path}")
        try:
            file_config = yaml.safe_load(path.read_text())
            if file_config is not None:
                config_dict.update(file_config)
        except Exception:
            logger.warning(f"Failed to load config from {path}", exc_info=True)

    # Then try .env file (medium priority)
    if Path(".env").exists():
        try:
            dotenv_config = dotenv_values(".env")
            if dotenv_config is not None:
                config_dict.update(dotenv_config)
        except Exception:
            logger.warning("Could not load .env file", exc_info=True)

    # Finally load from environment (highest priority)
    config_dict.update(os.environ)

    try:
        return Config.from_dict(config_dict)
    except Exception:
        logger.exception("Could not load config")
        raise RuntimeError("Could not load config")


config = load_config()
