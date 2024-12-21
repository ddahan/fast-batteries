from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import (
    admin_engine,
    create_database_user,
    create_database_with_owner,
    drop_database_if_it_exists,
    drop_role_if_it_exists,
    engine,
    terminate_active_connections,
)
from app.factories.base import MySQLAlchemyModelFactory
from app.main import app
from app.models.base import Base

settings = get_settings()


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True, scope="session")
def setup_test_database():
    """Prepare the test database before running tests for the whole session."""

    # NOTE: with env overriding, these are not "local" values (cf. pyproject.toml)
    db = settings.POSTGRES_DB
    user = settings.POSTGRES_USER
    password = settings.POSTGRES_PASSWORD
    with admin_engine.connect() as connection:
        terminate_active_connections(connection, db=db)
        drop_database_if_it_exists(connection, db=db)
        drop_role_if_it_exists(connection, user=user)
        create_database_user(connection, user=user, password=password)
        create_database_with_owner(connection, db=db, user=user)

    yield  # Run all tests


@pytest.fixture(autouse=True, scope="function")
def reset_database():
    """
    Drop all tables and recreate them before each test.
    NOTE: this is not performant, as all test functions will run this.
    However, this will prevent from any leakage between test.
    """
    # Drop and recreate tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Run the test
    yield


@pytest.fixture()
def session() -> Generator[Session]:
    """Provide a database session for unit tests."""
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True, scope="function")
def setup_factories(session: Session):  # the passed session is the fixture above!
    """Inject test session into all factories."""
    MySQLAlchemyModelFactory.set_session(session)
