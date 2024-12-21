from app.schemas.base import (
    DeactivateSchemaIn,
    DeactivateSchemaOptIn,
    DeactivateSchemaOut,
    ExpireSchemaIn,
    ExpireSchemaOptIn,
    ExpireSchemaOut,
    MySchema,
    TimeStampSchemaOut,
)
from app.schemas.user import BadgeOwner
from app.utils.strings import SecretId


class BadgeOut(ExpireSchemaOut, DeactivateSchemaOut, TimeStampSchemaOut, MySchema):
    owner: BadgeOwner
    id: str


class BadgeCreate(ExpireSchemaOptIn, DeactivateSchemaOptIn, MySchema):
    owner_id: SecretId


class BadgeFullUpdate(ExpireSchemaIn, DeactivateSchemaIn, MySchema):
    owner_id: SecretId


class BadgePartialUpdate(ExpireSchemaOptIn, DeactivateSchemaOptIn, MySchema):
    owner_id: SecretId | None = None
