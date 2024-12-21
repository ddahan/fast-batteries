from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Self, TypedDict

import jwt
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.utils.strings import SecretId
from app.utils.timezone import now_utc

settings = get_settings()


class JWTPayload(TypedDict):
    """Represents the content (payload) of a **decoded** JWT key"""

    sub: str  # main subject (user id, user email, ...)
    exp: int  # unix timestamp
    scope: str  # limit the usage scope of the token (via JWT parent class name)


class JWT(BaseModel, ABC):  # Do not use MySchema here
    """Base class used to represent an **encoded** Json Web Token (JWT)"""

    key: str

    @classmethod
    @abstractmethod
    def create(cls, *args: Any, **kwargs: Any) -> Self:
        raise NotImplementedError

    @classmethod
    def _create(cls, subject: str | Any, delta: timedelta) -> Self:
        """
        Helper method to create a token with a specific action and subject.
        Use in children classes.
        """
        to_encode = JWTPayload(
            sub=str(subject), exp=int((now_utc() + delta).timestamp()), scope=cls.__name__
        )

        # Encode the JWT
        encoded_jwt = jwt.encode(
            dict(to_encode), settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return cls(key=encoded_jwt)

    @classmethod
    def verify(cls, key: str) -> str | None:
        """Check the validity of a key and return its subject."""
        try:
            decoded_jwt_payload: JWTPayload = jwt.decode(
                key, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except jwt.InvalidTokenError:
            return None

        if decoded_jwt_payload["scope"] != cls.__name__:
            return None  # wrong token usage

        return decoded_jwt_payload["sub"]


class AccessJWT(JWT):
    # the alias provides the expected format for OAuth2, as 'key' would not work!
    key: str = Field(..., serialization_alias="access_token")
    token_type: str = "bearer"  # mandatory for OAuth2 standard

    @classmethod
    def create(cls, user_id: SecretId) -> Self:
        return cls._create(subject=user_id, delta=settings.ACCESS_TOKEN_EXPIRE)


class ResetPasswordJWT(JWT):
    @classmethod
    def create(cls, email: str) -> Self:
        return cls._create(
            subject=email,
            delta=settings.EMAIL_RESET_TOKEN_EXPIRE,
        )
