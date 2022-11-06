""" CLI. """
import logging
import os
import sys
from logging.config import dictConfig

import click
from dotenv import load_dotenv
from loader import __version__
from loader.config import config
from loader.load import loader_registry
from loader.log import get_log_config

from typing import List

logger = logging.getLogger(__name__)


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
    "--log-file",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="File to be used for logging",
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
    log_file: str,
    log_level: str,
    verbose: bool,
) -> None:
    """Main entry point"""
    dictConfig(
        get_log_config(
            __name__.split(".")[0],
            log_level=log_level if not verbose else "DEBUG",
            log_file=log_file,
        )
    )
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

    if name:
        for n in name:
            loader_registry.load_one(n)
    elif all:
        loader_registry.load_all()
    else:
        logger.error("No loaders to run")

    logger.info("Finished loading data without errors")


def run_cli() -> None:
    load_dotenv()
    cli(auto_envvar_prefix="PAH")


if __name__ == "__main__":
    run_cli()
