from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta

from attrs import asdict
from drebedengi import DrebedengiAPI
from drebedengi.model import ActionType, ObjectType, ReportPeriod
from loader.config import config
from loader.drebedengi.models import (
    LAST_LOADED_REVISION_KEY,
    SCHEMA_NAME,
    Account,
    ChangeRecord,
    Currency,
    ExpenseCategory,
    IncomeSource,
    Tag,
    Transaction,
)
from loader.load import loader_registry
from loader.models import Config
from loader.session import get_session
from sqlalchemy.sql import func
from sqlalchemy.sql import text as sa_text

import typing as t

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_last_loaded_revision(session: Session) -> int:
    db_config = (
        session.query(Config.value).filter(Config.param == LAST_LOADED_REVISION_KEY).scalar()
    )
    if db_config is None:
        return -1
    return int(db_config)


def get_last_revision_date(session: Session) -> datetime | None:
    return session.query(func.max(ChangeRecord.last_modified)).scalar()  # type: ignore


def set_current_revision(session: Session, revision: int) -> None:
    db_config = session.query(Config).filter(Config.param == LAST_LOADED_REVISION_KEY).first()
    if db_config is None:
        db_config = Config(param=LAST_LOADED_REVISION_KEY, value=str(revision))
        session.add(db_config)
    else:
        db_config.value = str(revision)


def do_full_load(session: Session) -> None:
    api = DrebedengiAPI(
        api_key=config.DREBEDENGI_API_KEY,
        login=config.DREBEDENGI_LOGIN,
        password=config.DREBEDENGI_PASSWORD,
    )

    session.execute(sa_text(f"TRUNCATE TABLE {SCHEMA_NAME}.{ChangeRecord.__tablename__}"))
    session.execute(sa_text(f"TRUNCATE TABLE {SCHEMA_NAME}.{Currency.__tablename__}"))
    session.execute(sa_text(f"TRUNCATE TABLE {SCHEMA_NAME}.{Account.__tablename__}"))
    session.execute(sa_text(f"TRUNCATE TABLE {SCHEMA_NAME}.{Tag.__tablename__}"))
    session.execute(sa_text(f"TRUNCATE TABLE {SCHEMA_NAME}.{IncomeSource.__tablename__}"))
    session.execute(sa_text(f"TRUNCATE TABLE {SCHEMA_NAME}.{ExpenseCategory.__tablename__}"))
    session.execute(sa_text(f"TRUNCATE TABLE {SCHEMA_NAME}.{Transaction.__tablename__}"))
    session.commit()

    # Get current revision
    cur_rev = api.get_current_revision()

    # Assign last modified timestamp
    last_modified = datetime.now()

    # Load changes
    changes = api.get_changes(revision=-1)

    for change in changes:
        session.add(ChangeRecord(**asdict(change), last_modified=last_modified))

    # Load currencies
    currencies = api.get_currencies()

    for currency in currencies:
        session.add(Currency(**asdict(currency), last_modified=last_modified))

    # Load accounts
    accounts = api.get_accounts()

    for account in accounts:
        session.add(Account(**asdict(account), last_modified=last_modified))

    # Load tags
    tags = api.get_tags()

    for tag in tags:
        session.add(Tag(**asdict(tag), last_modified=last_modified))

    # Load income sources
    income_sources = api.get_income_sources()

    for income_source in income_sources:
        session.add(IncomeSource(**asdict(income_source), last_modified=last_modified))

    # Load expense categories
    expense_categories = api.get_expense_categories()

    for expense_category in expense_categories:
        session.add(ExpenseCategory(**asdict(expense_category), last_modified=last_modified))

    # Load transactions
    trs = api.get_transactions(report_period=ReportPeriod.ALL_TIME)

    for tr in trs:
        session.add(Transaction(**asdict(tr), last_modified=last_modified))

    set_current_revision(session, cur_rev)

    session.commit()


def do_incremental_load(session: Session, last_rev: int) -> None:
    api = DrebedengiAPI(
        api_key=config.DREBEDENGI_API_KEY,
        login=config.DREBEDENGI_LOGIN,
        password=config.DREBEDENGI_PASSWORD,
    )

    # Get current revision
    cur_rev = api.get_current_revision()
    if cur_rev == last_rev:
        logger.info(f"Data already loaded up-to reveision {last_rev}. Nothing to load.")
        return

    # Assign last modified timestamp
    last_modified = datetime.now()

    # Load changes
    changes = api.get_changes(revision=last_rev)

    for change in changes:
        session.add(ChangeRecord(**asdict(change), last_modified=last_modified))

    # Process changes
    new_ids: t.Dict[ObjectType, t.Set[int]] = defaultdict(set)
    updated_ids: t.Dict[ObjectType, t.Set[int]] = defaultdict(set)
    deleted_ids: t.Dict[ObjectType, t.Set[int]] = defaultdict(set)

    changes.sort(key=lambda x: x.date)
    for change in changes:
        if change.action_type == ActionType.CREATE:
            new_ids[change.change_object_type].add(change.object_id)
        elif change.action_type == ActionType.UPDATE:
            # Only add to update list if object was not created in this same batch
            if change.object_id not in new_ids[change.change_object_type]:
                updated_ids[change.change_object_type].add(change.object_id)
        elif change.action_type == ActionType.DELETE:
            # If an objecty was created and deleted, we just ignore it
            if change.object_id not in new_ids[change.change_object_type]:
                deleted_ids[change.change_object_type].add(change.object_id)

                # Later delete overwrites create/update
                updated_ids[change.change_object_type].discard(change.object_id)

            new_ids[change.change_object_type].discard(change.object_id)

    # Load currencies
    if len(new_ids[ObjectType.CURRENCY]) > 0:
        new_and_updated_currencies = api.get_currencies(id_list=list(new_ids[ObjectType.CURRENCY]))

        for currency in new_and_updated_currencies:
            session.add(Currency(**asdict(currency), last_modified=last_modified))

    if len(deleted_ids[ObjectType.CURRENCY]) > 0:
        session.query(Currency).filter(Currency.id.in_(deleted_ids[ObjectType.CURRENCY])).update(
            {"tombstone": last_modified}, synchronize_session=False
        )

    if len(updated_ids[ObjectType.CURRENCY]) > 0:
        updated_currencies = api.get_currencies(id_list=list(updated_ids[ObjectType.CURRENCY]))

        for currency in updated_currencies:
            d = asdict(currency)
            d["last_modified"] = last_modified
            d.pop("id")

            session.query(Currency).filter(Currency.id == currency.id).update(
                d, synchronize_session=False
            )

    # Load accounts
    if len(new_ids[ObjectType.ACCOUNT]) > 0:
        new_and_updated_accounts = api.get_accounts(id_list=list(new_ids[ObjectType.ACCOUNT]))

        for account in new_and_updated_accounts:
            session.add(Account(**asdict(account), last_modified=last_modified))

    if len(deleted_ids[ObjectType.ACCOUNT]) > 0:
        session.query(Account).filter(Account.id.in_(deleted_ids[ObjectType.ACCOUNT])).update(
            {"tombstone": last_modified}, synchronize_session=False
        )

    if len(updated_ids[ObjectType.ACCOUNT]) > 0:
        updated_accounts = api.get_accounts(id_list=list(updated_ids[ObjectType.ACCOUNT]))

        for account in updated_accounts:
            d = asdict(account)
            d["last_modified"] = last_modified
            d.pop("id")

            session.query(Account).filter(Account.id == account.id).update(
                d, synchronize_session=False
            )

    # Load tags
    if len(new_ids[ObjectType.BUDGET_TAGS]) > 0:
        new_and_updated_tags = api.get_tags(id_list=list(new_ids[ObjectType.BUDGET_TAGS]))

        for tag in new_and_updated_tags:
            session.add(Tag(**asdict(tag), last_modified=last_modified))

    if len(deleted_ids[ObjectType.BUDGET_TAGS]) > 0:
        session.query(Tag).filter(Tag.id.in_(deleted_ids[ObjectType.BUDGET_TAGS])).update(
            {"tombstone": last_modified}, synchronize_session=False
        )

    if len(updated_ids[ObjectType.BUDGET_TAGS]) > 0:
        updated_tags = api.get_tags(id_list=list(updated_ids[ObjectType.BUDGET_TAGS]))

        for tag in updated_tags:
            d = asdict(tag)
            d["last_modified"] = last_modified
            d.pop("id")

            session.query(Tag).filter(Tag.id == tag.id).update(d, synchronize_session=False)

    # Load income sources
    if len(new_ids[ObjectType.INCOME_SOURCE]) > 0:
        new_and_updated_income_sources = api.get_income_sources(
            id_list=list(new_ids[ObjectType.INCOME_SOURCE])
        )

        for income_source in new_and_updated_income_sources:
            session.add(IncomeSource(**asdict(income_source), last_modified=last_modified))

    if len(deleted_ids[ObjectType.INCOME_SOURCE]) > 0:
        session.query(IncomeSource).filter(
            IncomeSource.id.in_(deleted_ids[ObjectType.INCOME_SOURCE])
        ).update({"tombstone": last_modified}, synchronize_session=False)

    if len(updated_ids[ObjectType.INCOME_SOURCE]) > 0:
        updated_income_sources = api.get_income_sources(
            id_list=list(updated_ids[ObjectType.INCOME_SOURCE])
        )

        for income_source in updated_income_sources:
            d = asdict(income_source)
            d["last_modified"] = last_modified
            d.pop("id")

            session.query(IncomeSource).filter(IncomeSource.id == income_source.id).update(
                d, synchronize_session=False
            )

    # Load expense categories
    if len(new_ids[ObjectType.EXPENSE_CATEGORY]) > 0:
        new_and_updated_expense_categories = api.get_expense_categories(
            id_list=list(new_ids[ObjectType.EXPENSE_CATEGORY])
        )

        for expense_category in new_and_updated_expense_categories:
            session.add(ExpenseCategory(**asdict(expense_category), last_modified=last_modified))

    if len(deleted_ids[ObjectType.EXPENSE_CATEGORY]) > 0:
        session.query(ExpenseCategory).filter(
            ExpenseCategory.id.in_(deleted_ids[ObjectType.EXPENSE_CATEGORY])
        ).update({"tombstone": last_modified}, synchronize_session=False)

    if len(updated_ids[ObjectType.EXPENSE_CATEGORY]) > 0:
        updated_expense_categories = api.get_expense_categories(
            id_list=list(updated_ids[ObjectType.EXPENSE_CATEGORY])
        )

        for expense_category in updated_expense_categories:
            d = asdict(expense_category)
            d["last_modified"] = last_modified
            d.pop("id")

            session.query(ExpenseCategory).filter(ExpenseCategory.id == expense_category.id).update(
                d, synchronize_session=False
            )

    # Load transactions
    if len(new_ids[ObjectType.TRANSACTION]) > 0:
        new_and_updated_trs = api.get_transactions(id_list=list(new_ids[ObjectType.TRANSACTION]))

        for tr in new_and_updated_trs:
            session.add(Transaction(**asdict(tr), last_modified=last_modified))

    if len(deleted_ids[ObjectType.TRANSACTION]) > 0:
        session.query(Transaction).filter(
            Transaction.id.in_(deleted_ids[ObjectType.TRANSACTION])
        ).update({"tombstone": last_modified}, synchronize_session=False)

    if len(updated_ids[ObjectType.TRANSACTION]) > 0:
        updated_trs = api.get_transactions(id_list=list(updated_ids[ObjectType.TRANSACTION]))

        for tr in updated_trs:
            d = asdict(tr)
            d["last_modified"] = last_modified
            d.pop("id")

            session.query(Transaction).filter(Transaction.id == tr.id).update(
                d, synchronize_session=False
            )

    set_current_revision(session, cur_rev)

    session.commit()


def load() -> bool:
    logger.info("Drebedengi loader started")
    try:
        with get_session() as session:
            logger.debug("Getting last revision from Drebedengi")
            last_rev = get_last_loaded_revision(session)
            logger.debug(f"Last revision: {last_rev}")

            if last_rev == -1:
                logger.info("No last revision found, loading all data")
                do_full_load(session)
            else:
                logger.info("Checking time since last transaction")
                last_rev_dt = get_last_revision_date(session)
                if last_rev_dt is not None and last_rev_dt > datetime.now() - timedelta(days=30):
                    logger.info(f"Last loaded revision: {last_rev}. Doing incremental load")
                    do_incremental_load(session, last_rev)
                else:
                    logger.info(
                        f"Last loaded revision: {last_rev}. Last revision is too old, doing full load"
                    )
                    do_full_load(session)
    except Exception:
        logger.exception("Error loading NerdDiary")
        return False

    logger.info("Drebedengi loader finished")
    return True


loader_registry.register_loader("drebedengi", load)
