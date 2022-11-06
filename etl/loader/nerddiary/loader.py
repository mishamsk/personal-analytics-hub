from __future__ import annotations

import logging
from datetime import datetime

import requests
from loader.config import config
from loader.load import loader_registry
from loader.nerddiary.models import HeadacheMariaLog, HeadacheMikeLog, MorningLog, PillLog
from loader.session import get_session
from nerddiary.server.schema import PollLogsSchema
from sqlalchemy.sql import func

import typing as t

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

MIKE_TELEGRAM_ID = 1581080
MARIA_TELEGRAM_ID = 62657914
ND_LOG_API_URL = config.NERDDIARY_API_ENDPOINT + "/logs"


def get_last_log_per_user(
    session: Session,
    model: t.Type[HeadacheMariaLog]
    | t.Type[HeadacheMikeLog]
    | t.Type[PillLog]
    | t.Type[MorningLog],
) -> dict[int, datetime]:
    logger.debug(f"Getting the latestlog date for model {model.__name__} each user id")
    user_pill_log_last_load = (
        session.query(model.user_id, func.max(model.poll_ts).label("max_date"))
        .group_by(model.user_id)
        .all()
    )

    if not user_pill_log_last_load:
        logger.debug("No data found")
        return {}
    else:
        ret = {
            t.cast(int, i.user_id): t.cast(datetime, i.max_date) for i in user_pill_log_last_load
        }
        logger.debug("Found data")
        return ret


def do_poll_load(
    session: Session,
    poll_name: str,
    model: t.Type[HeadacheMariaLog]
    | t.Type[HeadacheMikeLog]
    | t.Type[PillLog]
    | t.Type[MorningLog],
    user_ids: list[int],
) -> None:
    last_loads = get_last_log_per_user(session, model)

    for user_id in user_ids:
        params = {"poll_name": poll_name}
        load_func = session.add
        if user_id in last_loads:
            load_func = session.merge  # type: ignore
            params["date_from"] = last_loads[user_id].isoformat()

        logger.debug(
            f"Loading poll logs for poll {poll_name} for user {user_id} ad {ND_LOG_API_URL}/{user_id}\nWith params: {params}"
        )
        r = requests.get(
            f"{ND_LOG_API_URL}/{user_id}",
            params=params,
        )
        logger.debug(f"Request sent {r.request.url}")
        logger.debug(f"Got response: {r.status_code} {r.text}")

        logs = PollLogsSchema.parse_obj(r.json())

        for log in logs.logs:
            load_func(
                model(
                    poll_id=log.id,
                    user_id=user_id,
                    poll_ts=log.poll_ts,
                    **log.data,
                )
            )

    session.commit()


def load() -> None:
    logger.info("NerdDiary loader started")
    with get_session() as session:
        logger.info("Loading pill logs")
        do_poll_load(session, "Pain relief", PillLog, [MIKE_TELEGRAM_ID, MARIA_TELEGRAM_ID])
        logger.info("Pill logs loaded")
        logger.info("Loading morning logs")
        do_poll_load(session, "Morning", MorningLog, [MIKE_TELEGRAM_ID])
        logger.info("Morning logs loaded")
        logger.info("Loading headache logs")
        do_poll_load(session, "Headache", HeadacheMikeLog, [MIKE_TELEGRAM_ID])
        do_poll_load(session, "Headache", HeadacheMariaLog, [MARIA_TELEGRAM_ID])
        logger.info("Headache logs loaded")

    logger.info("NerdDiary loader finished")


loader_registry.register_loader("nerddiary", load)
