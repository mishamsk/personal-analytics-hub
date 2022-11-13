""" CLI. """
import logging
import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from loader import __version__
from loader.config import config
from loader.load import loader_registry
from loader.log import config_logging

from typing import List

logger = logging.getLogger(__name__)

cwd = Path.cwd()


def version_msg() -> str:
    """Return the version, location and Python powering it."""
    python_version = sys.version
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    message = "Financier %(version)s from {} (Python {})"
    return message.format(location, python_version)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(__version__, "-V", "--version", message=version_msg())
@click.option("-v", "--verbose", is_flag=True, help="Force all log levels to debug", default=False)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run interactively - will output log to stdout",
    default=False,
)
@click.option(
    "--log-path",
    type=click.Path(exists=True, writable=True, dir_okay=True, file_okay=False, path_type=Path),
    default=cwd,
    help="Folder for log file(s). Defaults to the current directory",
)
@click.option(
    "--log-level",
    type=click.Choice(
        [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ],
        case_sensitive=False,
    ),
    help="Log level",
    default="INFO",
    show_default=True,
)
def cli(
    interactive: bool,
    log_path: Path,
    log_level: str,
    verbose: bool,
) -> None:
    """Main entry point"""
    config_logging(
        "loader",
        interactive=interactive,
        log_level=log_level if not verbose else "DEBUG",
        log_path=log_path,
        tracebacks_suppress=["click"],
    )

    zeep_logger = logging.getLogger("zeep")
    zeep_logger.setLevel(logging.ERROR)

    logger.debug("Init cli successful")


@cli.command()
@click.option(
    "--all",
    "-a",
    is_flag=True,
    help="Load all",
    default=True,
)
@click.option(
    "--name",
    "-n",
    help="Name of the loader to run. Allows multiple",
    type=click.Choice(list(loader_registry.get_loader_names())),
    multiple=True,
    required=False,
)
def load(all: bool, name: List[str] | None) -> None:
    """Load data from the source."""
    logger.debug(f"Loading for user {config.DREBEDENGI_LOGIN}")

    loaded_successfully = True

    if name:
        for n in name:
            try:
                if not loader_registry.load_one(n):
                    loaded_successfully = False
            except Exception:
                logger.exception(f"Failed to load {n}")
                loaded_successfully = False
    elif all:
        loaded_successfully = loader_registry.load_all()
    else:
        logger.warning("No loaders to run")

    if loaded_successfully:
        logger.info("Finished loading data without errors")
    else:
        logger.error("Finished loading data with errors")
        exit(1)


def run_cli() -> None:
    load_dotenv()
    cli(auto_envvar_prefix="PAH")


if __name__ == "__main__":
    run_cli()
