from __future__ import annotations

import csv
import io
import logging
import zipfile
from datetime import datetime, timedelta

import requests
from loader.drebedengi.models import Currency, Transaction
from loader.session import get_session
from sqlalchemy.sql import func

from ..load import loader_registry
from .models import XChangeRate

import typing as t

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

# For fiat currencies using European Central Bank rates
FIAT_XCHANGE_RATE_ARCHIVE_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
FIAT_XCHANGE_RATE_BASE_CURRENCY_CODE = "EUR"

# Crypto currencies list & API URL
CRPYTO_CURRENCY_CODE_LIST = ["BTC"]
CRPYTO_CURRENCY_HIST_API_URL = "https://min-api.cryptocompare.com/data/v2/histoday?fsym={crypto}&tsym={fiat}&limit={limit}&toTs={to_ts}"

logger = logging.getLogger(__name__)


def get_first_transaction_date(session: Session) -> datetime | None:
    return session.query(func.min(Transaction.operation_date)).scalar()  # type: ignore


def get_last_xchange_rate(session: Session) -> datetime | None:
    return session.query(func.max(XChangeRate.ts)).scalar()  # type: ignore


def get_currency_list(session: Session) -> t.List[str]:
    currencies: t.List[Currency] = session.query(Currency).all()
    return [currency.currency_code for currency in currencies]


def load_xchange_rates(
    session: Session, currency_code_list: t.List[str], start_date: datetime
) -> None:
    if start_date.date() >= datetime.now().date():
        logger.info("All rates up-to today already exist. No xchange rates to load")
        return

    fiat_code_list = [
        currency for currency in currency_code_list if currency not in CRPYTO_CURRENCY_CODE_LIST
    ]
    logger.debug(f"Loading fiat xchange rates for {fiat_code_list}")

    with requests.Session() as s:
        logger.debug(f"Downloading fiat xchange rates archive from {FIAT_XCHANGE_RATE_ARCHIVE_URL}")
        hist_rates_zip = s.get(FIAT_XCHANGE_RATE_ARCHIVE_URL)

        with zipfile.ZipFile(io.BytesIO(hist_rates_zip.content)) as z:
            with io.TextIOWrapper(z.open("eurofxref-hist.csv"), encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dt = datetime.strptime(row["Date"], "%Y-%m-%d")

                    for currency_code, rate in row.items():
                        if rate == "N/A":
                            continue

                        if currency_code not in fiat_code_list:
                            continue

                        if dt <= start_date:
                            # TODO: double check rates always go in reverse order and we can bail out early this way
                            break

                        session.add(
                            XChangeRate(
                                ts=dt,
                                base_currency_code=FIAT_XCHANGE_RATE_BASE_CURRENCY_CODE,
                                currency_code=currency_code,
                                rate=float(rate),
                            )
                        )

    crypto_code_list = [
        currency for currency in currency_code_list if currency in CRPYTO_CURRENCY_CODE_LIST
    ]
    logger.debug(
        f"Loading crypto xchange rates for the following list of coins: {crypto_code_list}. Using API: {CRPYTO_CURRENCY_HIST_API_URL}"
    )

    if crypto_code_list:
        for crypto in crypto_code_list:
            logger.debug(f"Loading crypto xchange rates for {crypto}")
            with requests.Session() as s:
                days_to_load = datetime.now() - start_date
                limit = min(2000, days_to_load.days)
                to_ts = int(datetime.now().timestamp())
                min_loaded_date = datetime.now()

                while limit > 0:
                    url = CRPYTO_CURRENCY_HIST_API_URL.format(
                        crypto=crypto, fiat="USD", limit=limit, to_ts=to_ts
                    )

                    hist_rates_json = s.get(url).json()

                    for hist_rate in hist_rates_json["Data"]["Data"]:
                        dt = datetime.fromtimestamp(hist_rate["time"])
                        min_loaded_date = min(min_loaded_date, dt)

                        if dt <= start_date:
                            continue

                        if float(hist_rate["close"]) == 0:
                            break

                        session.add(
                            XChangeRate(
                                ts=dt,
                                base_currency_code="USD",
                                currency_code=crypto,
                                rate=float(hist_rate["close"]),
                            )
                        )

                    days_to_load = min_loaded_date - start_date
                    if days_to_load.days > 0:
                        limit = limit = min(2000, days_to_load.days)
                        to_ts = int(min_loaded_date.timestamp())
                    else:
                        break


def do_full_load(session: Session) -> None:
    logger.debug("Getting first transaction date")
    first_transaction_date = get_first_transaction_date(session)
    logger.debug(f"First transaction date: {first_transaction_date or 'None'}")

    if first_transaction_date is not None:
        load_xchange_rates(
            session,
            get_currency_list(session),
            first_transaction_date - timedelta(days=1),
        )

        session.commit()
    else:
        logger.warning("No transactions found, skipping xchange rates load")


def do_incremental_load(session: Session, last_ts: datetime) -> None:
    load_xchange_rates(session, get_currency_list(session), last_ts)

    session.commit()


def load() -> None:
    logger.info("XChange rate loader started")
    with get_session() as session:
        logger.debug("Getting last loaded xchange rate")
        last_ts = get_last_xchange_rate(session)
        logger.debug(f"Last loaded xchange rate: {last_ts or 'None'}")

        if last_ts is None:
            logger.info("No xchange rates loaded yet, doing full load")
            do_full_load(session)
        else:
            logger.info(f"Last loaded xchange rate: {last_ts}. Doing incremental load")
            do_incremental_load(session, last_ts)

    logger.info("XChange rate loader finished")


loader_registry.register_loader("xchange_rates", load, prio=1)
