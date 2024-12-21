from datetime import datetime

import phonenumbers
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)
from pydantic.alias_generators import to_camel
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.core.config import get_settings
from app.utils.timezone import make_aware

settings = get_settings()


class MySchema(BaseModel):
    """Allow to add a custom global config for all schemas."""

    model_config = ConfigDict(
        # python to Javascript case to use fields in a natural way with front-end
        alias_generator=to_camel,
        # TODO: add relevant comment here
        populate_by_name=True,
        # enables Pydantic to map ORM attributes to the schema fields
        from_attributes=True,
        # extra attributes during schema instanciation will raise a ValidationError
        extra="forbid",
    )


##########################################################################################
# Mixins for schemas
##########################################################################################


class PhoneNumberSchemaIn(MySchema):
    phone_number: PhoneNumber | None = Field(default=None)

    @field_validator("phone_number", mode="before")
    def configure_default_region(cls, value: PhoneNumber | None):
        PhoneNumber.default_region_code = settings.PHONE_REGION_CODE
        return value


class PhoneNumberSchemaOut(MySchema):  # TODO: add "Opt" in name or make mandatory
    phone_number: PhoneNumber | None

    @field_serializer("phone_number")
    def pretty_phone_number(self, value: PhoneNumber | None) -> str | None:
        """
        Instead of returning raw DB field like `tel:+33-6-11-22-33-44` it returns
        `06 11 22 33 44`.
        This configuration assumes that a single nationality is used for all phone numbers
        and that all recorded phone numbers used the same input and output regions.
        """
        if value:
            region_code = settings.PHONE_REGION_CODE
            parsed_number = phonenumbers.parse(value, region_code)
            return phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL
            )


class TimeStampSchemaOut(MySchema):
    created_at: datetime
    modified_at: datetime

    @field_serializer("created_at", "modified_at", when_used="json")
    def timestampable_tz_aware_datefield(self, value: datetime) -> datetime:
        return make_aware(value)


class ExpireSchemaOptIn(MySchema):
    expire_at: datetime | None = Field(default=None)


class ExpireSchemaIn(MySchema):
    expire_at: datetime


class ExpireSchemaOut(MySchema):
    expire_at: datetime | None
    expired: bool  # uses hybrid property from SQLAlchemy

    @field_serializer("expire_at", when_used="json")
    def expirable_tz_aware_datefield(self, value: datetime | None) -> datetime | None:
        if value:
            return make_aware(value)
        return None


class DeactivateSchemaOptIn(MySchema):
    is_active: bool | None = Field(default=True)


class DeactivateSchemaIn(MySchema):
    is_active: bool


class DeactivateSchemaOut(MySchema):
    is_active: bool
