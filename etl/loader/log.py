"""Module for setting up logging."""
from typing import Any, Dict

FORMATTERS = {
    "DEBUG": {"format": "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s"},
    "INFO": {"format": "%(asctime)s - %(levelname)s - %(message)s"},
    "WARNING": {"format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"},
    "ERROR": {"format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"},
    "CRITICAL": {"format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"},
}

HANDLERS_BASE = {
    "console": {
        "class": "logging.StreamHandler",
        "formatter": "INFO",
        "stream": "ext://sys.stdout",
    },
    "file": {
        "class": "logging.FileHandler",
        "formatter": "INFO",
        "filename": "app.log",
    },
}


def get_log_config(
    name: str, log_level: str = "INFO", log_file: str | None = None
) -> Dict[str, Any]:
    """Return a dict usable in dictConfig
    Set up logging to stdout with ``log_level``. If ``log_file`` is given use it instead.
    """

    if log_file is not None:
        handlers = {"handler": HANDLERS_BASE["file"]}
        handlers["handler"]["filename"] = log_file
    else:
        handlers = {"handler": HANDLERS_BASE["console"]}
    handlers["console"] = HANDLERS_BASE["console"]

    handlers["handler"]["formatter"] = log_level
    log_conf = {"level": log_level, "handlers": ["handler"]}

    res = {
        "version": 1,
        "formatters": FORMATTERS,
        "handlers": handlers,
        "loggers": {
            name: log_conf,
            "zeep": log_conf,
            # "root": log_conf,
            # "uvicorn": {"level": "INFO", "handlers": ["console", "handler"]},
        },
    }

    return res
