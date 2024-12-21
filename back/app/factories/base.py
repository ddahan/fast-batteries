# type: ignore - no stub files

import factory
from sqlalchemy.orm import Session


class MySQLAlchemyModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Custom base SQLAlchemyModelFactory able to handle different sessions dynamically.
    This allows to use the same factories in both:
     * a local context (e.g. seeding local db, shell command, ...)
     * a unit test context
    without providing the session for each factory instanciation.
    However, this requires to call 'set_session(<session>)' before each usage.
    """

    @classmethod
    def get_session(cls) -> Session:
        if hasattr(cls, "_session"):
            return cls._session
        raise RuntimeError(
            "No session set for the factory. Please use 'set_session' method before using a factory."
        )

    @classmethod
    def set_session(cls, session: Session) -> None:
        cls._session = session

    class Meta:
        abstract = True
