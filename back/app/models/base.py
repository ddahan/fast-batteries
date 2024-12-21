from collections.abc import Sequence
from datetime import datetime
from typing import Any, Literal, Self

from pydantic.alias_generators import to_snake
from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
)

from app.schemas.base import MySchema
from app.utils.strings import SecretId, get_secret_id


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Automatically set the table name based on the class name"""

        return "tb_" + to_snake(cls.__name__)


class CrudLogic:
    """This classes add basic CRUD operations, supposed to be injected in all models."""

    def save(self: Self, session: Session) -> Self:
        """Save an object to the database without repeating these 3 steps.
        This can be used when creating or updating an object.
        """
        session.add(self)
        # The session is holding in memory all the objects that should be saved in the
        # database later.
        # And once we are ready, we can commit those changes, and then the session will use
        # the engine underneath to save all the data by sending the appropriate SQL to the
        # database, and that way it will create all the rows. All in a single atomic
        # transaction.
        session.commit()
        # At this point, the object is empty because SQLAlchemy marks the object "expired"
        # So we need to explicitely refresh the object to get the new data from db.
        session.refresh(self)
        # Note that SQLAlchemy will refresh automatically the object if we try to access to an
        # attribute.
        return self

    @classmethod
    def create(cls, payload: MySchema, session: Session) -> Self:
        """Sugar to save, specifically for a create object."""

        new_obj = cls(**payload.model_dump())

        return new_obj.save(session)

    def update(self: Self, payload: MySchema, partial: bool, session: Session) -> Self:
        """Sugar to save, specifically for a full or partial object update"""

        for key, value in payload.model_dump(exclude_defaults=partial).items():
            setattr(self, key, value)

        return self.save(session)

    @classmethod
    def get_by(cls, field_name: str, field_value: str, session: Session) -> Self | None:
        """Read an object from a field name and value
        Return None if no object is found
        Raise MultipleResultsFound if multiple objects are found
        """

        field = getattr(cls, field_name)  # can raise AttributeError
        stmt = select(cls).where(field == field_value)
        obj = session.execute(stmt).scalars().one_or_none()
        return obj

    @classmethod
    def get_by_id(
        cls, obj_id: Any, session: Session, exc: Exception | None = None
    ) -> Self | None:
        """
        Read an object from its id into the database.
        If 'exc' is provided, the exception will be raised if the object is not found.
        """

        obj = session.get(cls, obj_id)
        if exc and obj is None:
            raise exc
        return obj

    @classmethod
    def get_all(cls, session: Session) -> Sequence[Self]:
        """Read all objects from its id into the database"""

        stmt = select(cls)
        return session.execute(stmt).scalars().all()

    def delete(self, session: Session) -> Literal[True]:
        """
        Delete a given object from the database.
        Return True to be consistant with 'delete_by_id'.
        NOTE: the Python object will still exist in memory (state == detached) afterthat.
        This is because SQLAlchemy session lifecycle and Python's garbage collection
        are separate concepts.
        """

        session.delete(self)
        session.commit()
        return True

    @classmethod
    def delete_by_id(
        cls, obj_id: Any, session: Session, exc: Exception | None = None
    ) -> bool:
        """
        Delete an object from the database, using its id.
        If 'exc' is provided, the exception will be raised if the object is not found.
        Return True if correctly deleted, False otherwise.
        """

        obj = cls.get_by_id(obj_id, session, exc=exc)
        if obj:
            obj.delete(session)
            return True
        return False

    @classmethod
    def count(cls, session: Session) -> int:
        """Count the number of objects of this type in the database."""
        stmt: Select[Any] = select(func.count()).select_from(cls)
        result = session.execute(stmt).scalars().one_or_none()
        return int(result or 0)


class MyModel(CrudLogic, Base):
    __abstract__ = True


##########################################################################################
# Mixins for models
##########################################################################################


class SecretIdModel(MyModel):
    __abstract__ = True

    id: Mapped[SecretId] = mapped_column(primary_key=True, insert_default=get_secret_id)


class SingletonModel(MyModel):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not kwargs.pop("_allow_direct_init", False):
            raise NotImplementedError(
                "Direct instantiation of SingletonModel is not allowed. Use the `load` method instead."
            )
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, session: Session) -> Self:
        """Get the instance, or create an empty one (with no values set)."""

        statement = select(cls).where(cls.id == 1)
        instance = session.execute(statement).scalars().one_or_none()
        if instance:
            return instance
        else:
            # Create the singleton if it doesn't exist
            new_instance = cls(id=1, _allow_direct_init=True)
            return new_instance.save(session)


class TimeStampModel(MyModel):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), server_onupdate=func.now()
    )


class ExpireModel(MyModel):
    __abstract__ = True

    expire_at: Mapped[datetime | None]

    # The expired property below can be used in both Python logic and SQLAlchemy queries.
    # However, since the SQL expression requires its own implementation, there is no
    # guarantee that the returned results will always be consistent between the two methods.

    @hybrid_property
    def expired(self) -> bool:  # type: ignore
        return self.expire_at is not None and datetime.now() > self.expire_at

    @expired.expression
    @classmethod
    def expired(cls):
        return and_(cls.expire_at.isnot(None), func.now() > cls.expire_at)


class DeactivateModel(MyModel):
    __abstract__ = True

    is_active: Mapped[bool]

    def invert_activity(self, session: Session) -> Self:
        self.is_active = not self.is_active
        # Actually, since the ORM keeps a link with the object, we don't really need
        # to return the object itself.
        return self.save(session)

    def activate(self, session: Session) -> None:
        self.is_active = True
        self.save(session)

    def deactivate(self, session: Session) -> None:
        self.is_active = False
        self.save(session)
