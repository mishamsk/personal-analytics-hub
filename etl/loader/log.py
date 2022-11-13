"""Module for setting up logging."""
import logging
import logging.handlers
from pathlib import Path
from types import ModuleType

from colorama import init
from rich.logging import RichHandler

import typing as t

init()

FILE_FORMATTERS = {
    "DEBUG": logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(lineno)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ),
    "INFO": logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ),
    "WARNING": logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ),
    "ERROR": logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ),
    "CRITICAL": logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ),
}


class LogLevelFilter(logging.Filter):
    """Filter log messages based on log level."""

    def __init__(self, level: str | t.List[str]) -> None:
        super().__init__()
        if isinstance(level, str):
            level = [level]
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelname in self.level


def config_logging(
    name: str,
    interactive: bool = False,
    log_level: str = "INFO",
    log_path: Path | None = None,
    tracebacks_suppress: t.Iterable[str | ModuleType] | None = None,
) -> None:
    """Configure logging for the application."""
    logger = logging.getLogger(name)

    if interactive:
        if tracebacks_suppress is None:
            tracebacks_suppress = []

        console_info_handler = RichHandler(
            markup=True,
            show_time=True,
            omit_repeated_times=False,
            show_level=False,
            show_path=False,
            log_time_format="[%X]",
        )
        console_info_handler.addFilter(LogLevelFilter("INFO"))
        console_info_handler.setFormatter(logging.Formatter(fmt="%(message)s", datefmt="[%X]"))

        console_warn_error_handler = RichHandler(
            markup=True,
            show_time=True,
            omit_repeated_times=False,
            show_level=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_suppress=tracebacks_suppress,
            log_time_format="[%Y-%m-%d %H:%M:%S]",
        )
        console_warn_error_handler.addFilter(LogLevelFilter(["WARNING", "ERROR", "CRITICAL"]))
        console_warn_error_handler.setFormatter(
            logging.Formatter(fmt="%(message)s", datefmt="[%Y-%m-%d %H:%M:%S]")
        )

        console_debug_handler = RichHandler(
            markup=True,
            show_time=True,
            omit_repeated_times=False,
            show_level=True,
            show_path=True,
            rich_tracebacks=True,
            tracebacks_suppress=tracebacks_suppress,
            log_time_format="[%Y-%m-%d %H:%M:%S]",
        )
        console_debug_handler.addFilter(LogLevelFilter("DEBUG"))
        console_debug_handler.setFormatter(
            logging.Formatter(fmt="%(message)s", datefmt="[%Y-%m-%d %H:%M:%S]")
        )

        logger.setLevel(log_level)

        logger.addHandler(console_info_handler)
        logger.addHandler(console_warn_error_handler)
        logger.addHandler(console_debug_handler)

    if log_path is not None:
        # File logger
        log_file_name = name.strip().replace(" ", "_").lower() + ".log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / log_file_name, maxBytes=1000000, backupCount=5
        )
        file_handler.setFormatter(FILE_FORMATTERS[log_level])

        # stderr handler
        stderr_handler = logging.StreamHandler()
        stderr_handler.setFormatter(FILE_FORMATTERS[log_level])
        stderr_handler.setLevel(logging.ERROR)

        logger.addHandler(file_handler)
        logger.addHandler(stderr_handler)
