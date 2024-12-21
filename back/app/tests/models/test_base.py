from collections import Counter
from datetime import datetime, timedelta

import pytest
import sqlalchemy
from sqlalchemy import func, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.models.base import (
    Base,
    CrudLogic,
    DeactivateModel,
    ExpireModel,
    MyModel,
    SecretIdModel,
    SingletonModel,
    TimeStampModel,
)
from app.schemas.base import MySchema


class BaseObj(Base, CrudLogic):
    """Simple object used for these tests only, to avoid coupling with real objects."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


class BaseSchemaIn(MySchema):
    name: str


class BaseSchemaOut(MySchema):
    id: int
    name: str


@pytest.fixture
def data(session: Session) -> list[BaseObj]:
    objs = [BaseObj(name="Jean"), BaseObj(name="Tom"), BaseObj(name="Rob")]
    session.add_all(objs)
    session.commit()
    return objs


def _get_obj_count(session: Session) -> int:
    obj_count_stmt = select(func.count()).select_from(BaseObj)
    obj_count = int(session.execute(obj_count_stmt).scalars().one_or_none() or 0)
    return obj_count


##########################################################################################


class BaseTestObject(SecretIdModel, Base): ...


def test_table_name():
    assert BaseTestObject().__tablename__ == "tb_base_test_object"


class TestCrudLogic:
    def test_save_for_create_ok(self, session: Session):
        assert _get_obj_count(session) == 0
        obj = BaseObj(name="John")
        assert obj.id is None
        obj.save(session)
        assert obj.id is not None
        assert _get_obj_count(session) == 1

    def test_save_for_update_ok(self, data: list[BaseObj], session: Session):
        old_obj_count = _get_obj_count(session)
        get_stmt = select(BaseObj).where(BaseObj.name == "Jean")
        obj = session.execute(get_stmt).scalars().one_or_none()
        assert obj and obj.name == "Jean"
        obj.name = "Juan"
        obj.save(session)
        new_obj_count = _get_obj_count(session)
        assert new_obj_count == old_obj_count
        assert obj.name == "Juan"

    def test_create_ok(self, session: Session):
        old_obj_count = _get_obj_count(session)
        payload = BaseSchemaIn(name="Jules")
        new_obj = BaseObj.create(payload, session)
        assert type(new_obj) is BaseObj
        assert _get_obj_count(session) == old_obj_count + 1

    def test_update_partial_ok(self, data: list[BaseObj], session: Session):
        # TODO: better test with more attrs in schemas (sothat "partial" make sense)
        old_obj_count = _get_obj_count(session)
        obj = data[0]
        update_payload = BaseSchemaIn(name="Jeannot")
        obj.update(update_payload, partial=False, session=session)
        assert obj.name == "Jeannot"
        assert _get_obj_count(session) == old_obj_count

    def test_update_full_ok(self, data: list[BaseObj], session: Session):
        # TODO: better test with more attrs in schemas (sothat "full" make sense)
        old_obj_count = _get_obj_count(session)
        obj = data[0]
        update_payload = BaseSchemaIn(name="Jeannot")
        obj.update(update_payload, partial=True, session=session)
        assert obj.name == "Jeannot"
        assert _get_obj_count(session) == old_obj_count

    def test_get_by_ok_one_object(self, data: list[BaseObj], session: Session):
        obj = BaseObj.get_by(field_name="name", field_value="Jean", session=session)
        assert type(obj) is BaseObj
        assert obj.name == "Jean"

    def test_get_ok_zero_object(self, session: Session):  # no data fixture injected
        obj = BaseObj.get_by(field_name="name", field_value="Jean", session=session)
        assert obj is None

    def test_get_by_ko_many_objects(self, data: list[BaseObj], session: Session):
        BaseObj.create(BaseSchemaIn(name="Jean"), session)  # second object
        with pytest.raises(sqlalchemy.exc.MultipleResultsFound):
            BaseObj.get_by(field_name="name", field_value="Jean", session=session)

    def test_get_by_ko_field_does_not_exist(self, data: list[BaseObj], session: Session):
        with pytest.raises(AttributeError):
            BaseObj.get_by(
                field_name="unexisting_field", field_value="Jean", session=session
            )

    def test_get_by_id_ok(self, data: list[BaseObj], session: Session):
        assert data[0].id == 1  # just to check that id is 1
        obj = BaseObj.get_by_id(obj_id=1, session=session)
        assert type(obj) is BaseObj
        assert obj.name == "Jean"

    def test_get_by_id_ok_zero_object(self, data: list[BaseObj], session: Session):
        obj = BaseObj.get_by_id(obj_id=999, session=session)
        assert obj is None

    def test_get_by_id_ko_with_given_exc(self, data: list[BaseObj], session: Session):
        with pytest.raises(ValueError):
            BaseObj.get_by_id(obj_id=999, session=session, exc=ValueError())

    def test_get_all_ok(self, data: list[BaseObj], session: Session):
        assert _get_obj_count(session) == 3
        assert [type(obj) is BaseObj for obj in BaseObj.get_all(session)]

    def test_get_all_ok_empty(self, session: Session):  # no data fixture injected
        assert BaseObj.get_all(session) == []

    def test_delete_ok(self, data: list[BaseObj], session: Session):
        assert _get_obj_count(session) == 3
        obj = BaseObj.get_by_id(1, session)
        assert type(obj) is BaseObj
        result = obj.delete(session)
        assert result is True
        assert _get_obj_count(session) == 2
        assert type(obj) is BaseObj  # Python object still exists in memory (weird)

    def test_delete_by_id_ok(self, data: list[BaseObj], session: Session):
        assert _get_obj_count(session) == 3
        result = BaseObj.delete_by_id(1, session)
        assert result is True
        assert _get_obj_count(session) == 2

    def test_delete_by_id_ok_no_object(self, data: list[BaseObj], session: Session):
        assert _get_obj_count(session) == 3
        result = BaseObj.delete_by_id(999, session)
        assert result is False
        assert _get_obj_count(session) == 3

    def test_count_ok_many(self, data: list[BaseObj], session: Session):
        assert BaseObj.count(session) == 3

    def test_count_ok_zero(self, session: Session):  # no data fixture injected
        assert BaseObj.count(session) == 0


##########################################################################################
# Mixins for models
##########################################################################################


class SecretIdObject(SecretIdModel, MyModel): ...


def test_secret_id_model(session: Session):
    obj = SecretIdObject().save(session)
    assert type(obj.id) is str


class SingletonObject(SingletonModel, MyModel): ...


def test_singleton_model(session: Session):
    # A singleton object can't be instanciated directly
    with pytest.raises(NotImplementedError):
        SingletonObject(id=1)

    # it creates and get the object when it does not exist
    obj = SingletonObject.load(session)
    assert type(obj) is SingletonObject
    assert obj.id == 1
    assert SingletonObject.count(session) == 1

    # it just gets the object when it's already created
    del obj
    obj = SingletonObject.load(session)
    assert type(obj) is SingletonObject
    assert obj.id == 1
    assert SingletonObject.count(session) == 1

    # the object can still be deleted
    obj.delete(session)
    assert SingletonObject.count(session) == 0


class TimeStampObject(SecretIdModel, TimeStampModel, MyModel): ...


def test_time_stamp_model(session: Session):
    obj = TimeStampObject().save(session)
    assert type(obj) is TimeStampObject
    assert obj.created_at is not None
    assert obj.modified_at is not None
    assert obj.created_at == obj.modified_at
    # A small delta between python date and server date ensure they have the same schedule
    assert abs(datetime.now() - obj.created_at) < timedelta(seconds=1)


class ExpireObject(SecretIdModel, ExpireModel, MyModel): ...


def test_expire_model(session: Session):
    obj_no_expiration = ExpireObject(expire_at=None).save(session)
    obj_expire_soon = ExpireObject(expire_at=datetime.now() + timedelta(days=30)).save(
        session
    )
    obj_expired = ExpireObject(expire_at=datetime.now() - timedelta(days=30)).save(
        session
    )

    # Test Python property
    assert obj_no_expiration.expired is False
    assert obj_expire_soon.expired is False
    assert obj_expired.expired is True

    # Test SQL property
    stmt_1 = select(ExpireObject).where(ExpireObject.expired)
    assert session.execute(stmt_1).scalars().all() == [obj_expired]

    stmt_2 = select(ExpireObject).where(~ExpireObject.expired)
    assert Counter(session.execute(stmt_2).scalars().all()) == Counter(
        [
            obj_expire_soon,
            obj_no_expiration,
        ]
    )


class DeactivateObject(SecretIdModel, DeactivateModel, MyModel): ...


def test_deactivate_model(session: Session):
    obj = DeactivateObject(is_active=True)

    assert obj.is_active is True
    obj.deactivate(session)
    assert obj.is_active is False
    obj.deactivate(session)  # no error if deactivated again
    assert obj.is_active is False
    obj.invert_activity(session)
    assert obj.is_active is True
