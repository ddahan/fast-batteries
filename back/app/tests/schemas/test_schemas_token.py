from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import pytest
from freezegun import freeze_time

from app.core.config import get_settings
from app.schemas.token import AccessJWT, JWTPayload, ResetPasswordJWT

settings = get_settings()

# NOTE: we could avoid some repetitions here by using parametrization but the code would
# be harder to understand.


@pytest.fixture()
def access_jwt() -> AccessJWT:
    return AccessJWT.create(user_id="123")


class TestAccessJWT:
    def test_token_creation(self, access_jwt: AccessJWT):
        assert type(access_jwt) is AccessJWT
        assert type(access_jwt.key) is str

        decoded_access_jwt: JWTPayload = jwt.decode(
            access_jwt.key, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Check decoded content (without using verify() method directly)
        assert decoded_access_jwt["sub"] == "123"
        assert decoded_access_jwt["scope"] == "AccessJWT"

    def test_token_verify_ok(self, access_jwt: AccessJWT):
        assert AccessJWT.verify(access_jwt.key) == "123"  # sub

    def test_token_verify_ko_invalid_token(self):
        assert AccessJWT.verify("wrong_key") is None

    def test_token_verify_ko_expired(self, access_jwt: AccessJWT):
        def _one_hour_too_late():
            return datetime.now(UTC) + settings.ACCESS_TOKEN_EXPIRE + timedelta(hours=1)

        with freeze_time(_one_hour_too_late):
            assert AccessJWT.verify(access_jwt.key) is None

    def test_token_verify_ko_wrong_scope_token(self):
        # Manually create a token with a wrong scope
        wrong_scope_payload: dict[str, Any] = {
            "sub": "123",
            "exp": int((datetime.now(UTC) + settings.ACCESS_TOKEN_EXPIRE).timestamp()),
            "scope": "WrongScopeJWT",
        }

        wrong_scope_token = jwt.encode(
            wrong_scope_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        # Verify the token
        assert AccessJWT.verify(wrong_scope_token) is None

    def test_token_verify_ko_empty_token(self):
        assert AccessJWT.verify("") is None
        assert AccessJWT.verify(None) is None  # type: ignore


@pytest.fixture()
def reset_password_jwt() -> ResetPasswordJWT:
    return ResetPasswordJWT.create(email="user@example.com")


class TestResetPasswordJWT:
    def test_token_creation(self, reset_password_jwt: ResetPasswordJWT):
        assert type(reset_password_jwt) is ResetPasswordJWT
        assert type(reset_password_jwt.key) is str

        decoded_reset_jwt: JWTPayload = jwt.decode(
            reset_password_jwt.key, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Check decoded content (without using verify() method directly)
        assert decoded_reset_jwt["sub"] == "user@example.com"
        assert decoded_reset_jwt["scope"] == "ResetPasswordJWT"

    def test_token_verify_ok(self, reset_password_jwt: ResetPasswordJWT):
        assert (
            ResetPasswordJWT.verify(reset_password_jwt.key) == "user@example.com"
        )  # sub

    def test_token_verify_ko_invalid_token(self):
        assert ResetPasswordJWT.verify("wrong_key") is None

    def test_token_verify_ko_expired(self, reset_password_jwt: ResetPasswordJWT):
        def _one_hour_too_late():
            return (
                datetime.now(UTC) + settings.EMAIL_RESET_TOKEN_EXPIRE + timedelta(hours=1)
            )

        with freeze_time(_one_hour_too_late):
            assert ResetPasswordJWT.verify(reset_password_jwt.key) is None

    def test_token_verify_ko_wrong_scope_token(self):
        # Manually create a token with a wrong scope
        wrong_scope_payload: dict[str, Any] = {
            "sub": "user@example.com",
            "exp": int(
                (datetime.now(UTC) + settings.EMAIL_RESET_TOKEN_EXPIRE).timestamp()
            ),
            "scope": "WrongScopeJWT",
        }

        wrong_scope_token = jwt.encode(
            wrong_scope_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        # Verify the token
        assert ResetPasswordJWT.verify(wrong_scope_token) is None

    def test_token_verify_ko_empty_token(self):
        assert ResetPasswordJWT.verify("") is None
        assert ResetPasswordJWT.verify(None) is None  # type: ignore
