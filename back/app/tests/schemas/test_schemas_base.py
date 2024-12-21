import json
from datetime import datetime

import pytest
from pydantic import ValidationError
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.models.base import Base
from app.schemas.base import (
    MySchema,
    PhoneNumberSchemaIn,
    PhoneNumberSchemaOut,
    TimeStampSchemaOut,
)


class MySchemaBase(MySchema):
    first_name: str
    age: int


class MySchemaObjIn(MySchemaBase): ...


class MySchemaObjOut(MySchemaBase):
    id: int


class MyModelObj(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str]
    age: Mapped[int]


class TestMySchema:
    def test_alias_generator_camel(self):
        obj = MySchemaObjIn(first_name="Rob", age=20)
        assert "first_name" in obj.model_dump().keys()
        assert "firstName" in obj.model_dump(by_alias=True).keys()

    def test_from_attributes_true(self, session: Session):
        model_obj = MyModelObj(first_name="Rob", age=20)
        session.add(model_obj)
        session.commit()

        schema_obj = MySchemaObjOut.model_validate(model_obj)
        assert schema_obj.first_name == "Rob"
        assert schema_obj.age == 20

    def test_extra_forbid(self):
        with pytest.raises(ValidationError):
            payload = dict(first_name="Rob", age=20, other="other")
            MySchemaObjIn(**payload)  # type: ignore


class TestPhoneNumberSchemaIn:
    def test_configure_default_region(self):
        obj_in = PhoneNumberSchemaIn(phone_number=PhoneNumber("06 10 20 30 40"))
        # Change the code below if you use a different region
        assert PhoneNumber.default_region_code == "FR"
        assert obj_in.phone_number
        assert obj_in.phone_number.startswith("tel:+33")

    def test_wrong_phone_number_ko(self):
        with pytest.raises(ValidationError):
            PhoneNumberSchemaIn(phone_number=PhoneNumber("1234"))


class TestPhoneNumberSchemaOut:
    def test_pretty_phone_number(self):
        obj_out = PhoneNumberSchemaOut(phone_number=PhoneNumber("+33-6-10-20-30-40"))
        assert obj_out.model_dump()["phone_number"] == "06 10 20 30 40"


class TestTimeStampSchemaOut:
    def test_timestampable_tz_aware_datefield(self):
        dt = datetime(2024, 12, 12, 10)  # 10h 00min 00sec
        obj = TimeStampSchemaOut(created_at=dt, modified_at=dt)

        # assert nothing changes if simple model_dump() (without JSON)
        dump = obj.model_dump()
        assert dump["created_at"] == obj.created_at

        # assert conversion is done with model_dump_json()
        json_dump = obj.model_dump_json()
        dump = json.loads(json_dump)  # easier to reconvert in dict for assertions
        assert dump["created_at"] == "2024-12-12T11:00:00+01:00"
