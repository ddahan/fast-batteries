from collections.abc import Generator
from typing import Annotated

import logfire
from fastapi import Depends
from loguru import logger
from sqlalchemy import Connection, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

##########################################################################################
# Engines
# The engine is that single object that we share with all the code, and that is in charge
# of communicating with the database, handling the connections.
##########################################################################################

engine = create_engine(
    settings.POSTGRES_URI,
    echo=settings.DATABASE_ECHO,  # prints all the SQL statements the engine executes
)

# Admin engine to manage databases (connects to the "postgres" default database)
# It has its own USER/PASSWORD settings because local one are overrided when running tests
admin_engine = create_engine(
    settings.POSTGRES_ADMIN_URI,
    echo=settings.DATABASE_ECHO,
    isolation_level="AUTOCOMMIT",  # required from operation like DROP DATABASE
)

##########################################################################################
# Logging
##########################################################################################

if settings.USE_LOGFIRE:
    logfire.configure(token=settings.LOGFIRE_TOKEN)
    logfire.instrument_sqlalchemy(engine=engine)

##########################################################################################
# Session
##########################################################################################

SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Generator[Session]:
    """Injectable dependency"""
    # using with will automatically create and close the session (like with open files)
    with SessionFactory() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

##########################################################################################
# PostgreSQL raw queries
##########################################################################################


def terminate_active_connections(connection: Connection, db: str):
    connection.execute(
        text(
            f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{db}'
                    AND pid <> pg_backend_pid();
                    """
        )
    )


def drop_database_if_it_exists(connection: Connection, db: str):
    connection.execute(text(f"DROP DATABASE IF EXISTS {db};"))
    logger.info(f"Database '{db}' has been dropped if it existed.")


def drop_role_if_it_exists(connection: Connection, user: str):
    connection.execute(text(f"DROP ROLE IF EXISTS {user};"))
    logger.info(f"Role '{user}' has been dropped if it existed.")


def create_database_user(connection: Connection, user: str, password: str):
    connection.execute(text(f"CREATE USER {user} WITH PASSWORD '{password}';"))
    connection.execute(text(f"ALTER USER {user} WITH CREATEDB;"))
    logger.info(f"Created user '{user}'.")


def create_database_with_owner(connection: Connection, db: str, user: str):
    connection.execute(text(f"CREATE DATABASE {db};"))
    connection.execute(text(f"ALTER DATABASE {db} OWNER TO {user};"))
    logger.info(f"Created database '{db}' and assigned ownership to '{user}'.")
