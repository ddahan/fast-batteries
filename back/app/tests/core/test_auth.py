from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.core.auth import authenticate, get_current_superuser, get_current_user
from app.core.exceptions import InsufficientPermission, InvalidToken, ItemNotFound
from app.factories.user import LinkedInUserFactory, UserFactory
from app.models.user import User
from app.schemas.token import AccessJWT


@pytest.fixture()
def test_user() -> User:
    return UserFactory(email="jean@lou.com", password="azerty123")


@pytest.fixture()
def linkedin_user() -> User:
    return LinkedInUserFactory(email="john@dep.com")


@pytest.fixture
def mock_access_jwt() -> Generator[MagicMock]:
    with patch.object(AccessJWT, "verify", return_value=1) as mock:
        yield mock


class TestAuthenticate:
    def test_valid_user(self, test_user: User, session: Session):
        user = authenticate(session, "jean@lou.com", "azerty123")
        assert user == test_user

    def test_invalid_user(self, test_user: User, session: Session):
        user = authenticate(session, "nonexistent@example.com", "azerty123")
        assert user is None

    def test_user_without_hashed_password(self, linkedin_user: User, session: Session):
        user = authenticate(session, "john@dep.com", "azerty123")
        assert user is None

    def test_wrong_password(self, test_user: User, session: Session):
        with patch("app.core.security.verify_password", return_value=False):
            user = authenticate(session, "jean@lou.com", "wrongpassword")
            assert user is None


class TestGetCurrentUser:
    def test_valid_token(
        self,
        session: Session,
        test_user: User,
        mock_access_jwt: Generator[MagicMock],
    ):
        with patch.object(AccessJWT, "verify", return_value=test_user.id):
            user = get_current_user(session, "valid_token")
            assert user == test_user

    def test_invalid_token(self, session: Session):
        with patch.object(AccessJWT, "verify", return_value=None):
            with pytest.raises(InvalidToken):
                get_current_user(session, "invalid_token")

    def test_user_not_found(
        self, session: Session, mock_access_jwt: Generator[MagicMock]
    ):
        with patch.object(AccessJWT, "verify", return_value=999):  # Non-existent user ID
            with pytest.raises(ItemNotFound):
                get_current_user(session, "valid_token")


class TestGetCurrentSuperuser:
    def test_valid_superuser(self, session: Session, test_user: User):
        # Mark the test user as a superuser
        test_user.is_superuser = True
        session.commit()

        # Call the function with the superuser
        superuser = get_current_superuser(test_user)
        assert superuser == test_user
        assert superuser.is_superuser

    def test_non_superuser(self, session: Session, test_user: User):
        # Ensure the user is not a superuser
        assert test_user.is_superuser is False

        # Call the function with a non-superuser and expect an exception
        with pytest.raises(InsufficientPermission):
            get_current_superuser(test_user)
