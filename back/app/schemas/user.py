from decimal import Decimal

from pydantic import EmailStr, Field, computed_field, field_validator

from app.schemas.base import MySchema, PhoneNumberSchemaIn, PhoneNumberSchemaOut
from app.utils.fields import Password, Price
from app.utils.strings import SecretId


class UserBaseIn(PhoneNumberSchemaIn):
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=128)
    last_name: str = Field(min_length=1, max_length=128)
    balance: Price = Decimal(0)

    @field_validator("email", mode="before")
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("first_name", mode="after")
    def normalize_first_name(cls, value: str) -> str:
        return value.strip().capitalize()

    @field_validator("last_name", mode="after")
    def normalize_last_name(cls, value: str) -> str:
        return value.strip().upper()


class UserClassicIn(UserBaseIn, MySchema):
    password: Password


class UserLinkedinIn(UserBaseIn, MySchema):
    linkedin_id: str


class UserSendResetPassword(MySchema):
    email: EmailStr


class UserResetPassword(MySchema):
    token_key: str
    new_password: Password


# Properties to return via API
class UserPublic(PhoneNumberSchemaOut, MySchema):
    id: SecretId
    email: EmailStr
    first_name: str
    last_name: str
    is_superuser: bool


class BadgeOwner(MySchema):
    id: SecretId
    first_name: str = Field()  # only used to compute label
    last_name: str = Field()  # only used to compute label

    @computed_field(alias="label")  # useful for Nuxt UI
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
