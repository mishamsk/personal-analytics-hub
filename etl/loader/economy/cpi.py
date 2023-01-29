from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime

import requests
from loader.config import config
from loader.session import get_session
from sqlalchemy.sql import func

from ..load import loader_registry
from .models import CPI

import typing as t

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

BLS_API_V1_ENDPOINT = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

logger = logging.getLogger(__name__)


def get_earliest_cpi_data(
    session: Session, area_code: str, item_codes: t.List[str]
) -> datetime | None:
    logger.debug(f"Getting latest date for each item code for the given area code: {area_code}")
    item_code_last_load = (
        session.query(CPI.item_code, func.max(CPI.date).label("max_date"))
        .filter(CPI.area_code == area_code, CPI.item_code.in_(item_codes))
        .group_by(CPI.item_code)
        .all()
    )

    if not item_code_last_load:
        logger.debug("No CPI data found for area code: {area_code} and item codes: {item_codes}")
        return None
    else:
        ret = min([t.cast(datetime, i.max_date) for i in item_code_last_load])
        logger.debug(
            f"Found CPI data for area code: {area_code} and item codes: {item_codes}. Returning the minimal date of all found items: {ret}"
        )
        return ret


def load_cpi_data(
    session: Session,
    start_date: datetime | date,
    area_code: str,
    item_codes: t.List[str],
) -> bool:

    if datetime.now().replace(
        month=12 if datetime.now().month == 12 else datetime.now().month - 1, day=1
    ).strftime("%Y-%m") == start_date.strftime("%Y-%m"):
        logger.info("No CPI data to load")
        return True

    headers = {"Content-type": "application/json"}
    # TODO: it doesn't check for the limit of 10 years
    data = json.dumps(
        {
            "seriesid": [f"CUUR{area_code}{item_code}" for item_code in item_codes],
            "startyear": start_date.strftime("%Y"),
            "endyear": datetime.now().strftime("%Y"),
        }
    )
    series_re = re.compile(r"CUUR(?P<area_code>\w{4})(?P<item_code>\w+)")

    with requests.Session() as s:
        cpi_data = s.post(BLS_API_V1_ENDPOINT, data=data, headers=headers, timeout=(3, 30)).json()

        if (
            cpi_data["status"] != "REQUEST_SUCCEEDED"
            or "Results" not in cpi_data
            or "series" not in cpi_data["Results"]
        ):
            logger.error(
                f"Failed to load CPI data for area_code: {area_code} and item_codes: {item_codes}. Got response:\n {cpi_data}"
            )
            return False

        for series in cpi_data["Results"]["series"]:
            series_id = series["seriesID"]
            m = series_re.match(series_id)
            if not m:
                logger.warning(f"Unexpected series ID: {series_id}. Skipping")
                continue

            area_code = m.group("area_code")
            item_code = m.group("item_code")

            for item in series["data"]:
                year = int(item["year"])
                month = -1
                period = item["period"]
                value = float(item["value"])
                footnotes = ",".join([f["text"] for f in item["footnotes"] if "text" in f])

                if not "M01" <= period <= "M12":
                    logger.warning(f"Unexpected period: {period}. Skipping")
                    continue
                else:
                    month = int(period[1:])

                session.merge(
                    CPI(
                        date=datetime(year, month, 1),
                        area_code=area_code,
                        item_code=item_code,
                        value=value,
                        footnotes=footnotes,
                    )
                )

    return True


def load() -> bool:
    logger.info(
        f"CPI loader started. Area code: {config.cpi_config.area_code}. Item codes: {config.cpi_config.item_codes}"
    )

    res = True
    try:
        with get_session() as session:
            item_codes_start = 0
            item_codes_end = min(25, len(config.cpi_config.item_codes))

            while item_codes_start < len(config.cpi_config.item_codes):
                logger.debug(
                    f"Loading CPI data for item codes: {config.cpi_config.item_codes[item_codes_start:item_codes_end]}"
                )

                item_codes = config.cpi_config.item_codes[item_codes_start:item_codes_end]

                last_cpi_ts = get_earliest_cpi_data(
                    session, config.cpi_config.area_code, item_codes
                )

                if last_cpi_ts is None:
                    logger.info(
                        f"No previous records found. Loading all data since config start date: {config.cpi_config.start_date}"
                    )
                    res = load_cpi_data(
                        session,
                        config.cpi_config.start_date,
                        config.cpi_config.area_code,
                        item_codes,
                    )
                else:
                    logger.info(f"Loading data since: {last_cpi_ts}")
                    res = load_cpi_data(
                        session, last_cpi_ts, config.cpi_config.area_code, item_codes
                    )

                item_codes_start = item_codes_end
                item_codes_end = min(item_codes_end + 25, len(config.cpi_config.item_codes))

            session.commit()
    except Exception:
        logger.exception("Error loading CPI")
        return False

    logger.info("CPI loader finished")
    return res


loader_registry.register_loader("cpi", load)
