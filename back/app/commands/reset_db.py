#!/usr/local/bin/python

from datetime import timedelta
from decimal import Decimal

import typer
from alembic import command
from alembic.config import Config
from loguru import logger
from pydantic import SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from rich.prompt import Confirm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import (
    admin_engine,
    create_database_with_owner,
    drop_database_if_it_exists,
    engine,
    terminate_active_connections,
)
from app.factories.badge import BadgeFactory
from app.factories.base import MySQLAlchemyModelFactory
from app.models.db_parameters import DBParameters
from app.models.periodic_task import PeriodicTask
from app.models.user import User
from app.schemas.periodic_task import PeriodicTaskIn
from app.schemas.user import UserClassicIn
from app.utils.filesystem import create_directory_if_not_exist, erase

app = typer.Typer()


@app.command()
def reset_db() -> None:
    """Init or reset existing database using seed data."""

    settings = get_settings()

    # Ensure environment is compatible with this operation
    if not settings.DATABASE_ALLOW_RESET:
        logger.error(
            "Can't seed fake data in this environment as DATABASE_ALLOW_RESET env var is not True."
        )
        return

    if not Confirm.ask("This will drop your database and all its data. Continue?"):
        logger.info("Exiting without any action.")
        return

    with admin_engine.connect() as connection:
        db = settings.POSTGRES_DB
        user = settings.POSTGRES_USER
        terminate_active_connections(connection, db=db)
        drop_database_if_it_exists(connection, db=db)
        create_database_with_owner(connection, db=db, user=user)

    # Clear old migration data
    erase(settings.ALEMBIC_MIGRATION_VERSION_PATH)
    create_directory_if_not_exist(settings.ALEMBIC_MIGRATION_VERSION_PATH)

    # Generate initial migration then apply it
    alembic_cfg = Config(settings.ALEMBIC_CONFIG_PATH)
    # Workaround as the script location in .ini file seems to be relative to the
    # execution path, and then lead to errors when executing scripts."""
    alembic_cfg.set_main_option("script_location", str(settings.ALEMBIC_MIGRATION_PATH))
    command.revision(alembic_cfg, message="initial", autogenerate=True)
    command.upgrade(alembic_cfg, "head")
    logger.success("Database and tables have been created.")

    # Seed database with fake db
    with Session(engine) as session:
        logger.success(f"{settings.POSTGRES_DB} database seeding has started …")
        seed_db(session)
        logger.success(f"{settings.POSTGRES_DB} database seeding finished succesfully.")


def seed_db(session: Session) -> None:
    # Configure the session to use for all incoming factories
    MySQLAlchemyModelFactory.set_session(session)

    ######################################################################################
    # fake data
    ######################################################################################

    db_params = DBParameters.load(session)  # init object
    db_params.APP_TAGLINE = "My Super app!"

    david = User.register_super_user(
        user_payload=UserClassicIn(
            # dirty data is passed to ensure right cleaning with Pydantic
            first_name="david ",
            last_name="dahan ",
            phone_number=PhoneNumber("06 62102508"),
            email="DaviD@mail.com",
            password=SecretStr("azerty123"),
            balance=Decimal("3.40"),
        ),
        session=session,
    )

    periodic_task_create = PeriodicTaskIn(
        name="Add the same numbers every 10s",
        task="app.tasks.tasks.add",
        interval=timedelta(seconds=10),
        args=[3, 7],
    )
    periodic_task = PeriodicTask(**periodic_task_create.model_dump())

    ######################################################################################
    # save fake data
    ######################################################################################

    for item in (db_params, david, periodic_task):
        session.add(item)
    session.commit()

    BadgeFactory.create_batch(32)  # type: ignore # create 32 users too.


if __name__ == "__main__":
    app()
