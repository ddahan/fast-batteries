from typing import Any
from unittest import mock

from httpx import Response

# When testing validation, we want a fixture to return the http Response
# + the error payload for easier testing
# Using dict[Any, Any] instead of ErrorPayload removes all warning due to total=False
FixtureResponse = tuple[Response, dict[str, Any]]


# mocks


def patch_bcrypt_hashpw():
    """Utility function to patch bcrypt.hashpw with fake_password_hash."""

    def fake_password_hash(_salt: str, _password: str) -> bytes:
        """Mock function to speed up password hash generation."""
        return b"fake_hashed_password"

    return mock.patch("bcrypt.hashpw", side_effect=fake_password_hash)
