from typing import Any

import pytest
import sqlalchemy
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.factories.user import (
    ClassicUserFactory,
    LinkedInProfileDictFactory,
    LinkedInUserFactory,
)
from app.models.user import User
from app.schemas.token import AccessJWT
from app.schemas.user import UserClassicIn, UserLinkedinIn


@pytest.fixture
def user_data() -> dict[str, Any]:
    # Return a dictionary that can be safely modified in each test
    return {
        "email": "Robert@ledoux.com",
        "first_name": "robert ",  # trailing space is on purpose to test normalization
        "last_name": "Ledoux",
        "password": "azerty123",
    }


def test_classic_register_user_ok(user_data: dict[str, Any], session: Session):
    user = User.register_user(UserClassicIn(**user_data), session)
    assert user.email == "robert@ledoux.com"
    assert user.first_name == "Robert"
    assert user.last_name == "LEDOUX"
    assert user.is_superuser is False
    assert user.phone_number is None
    assert not hasattr(user, "password")
    assert hasattr(user, "hashed_password")
    assert len(user.badges) == 0
    assert user.linkedin_id is None


def test_classic_register_user_ko_wrong_field(
    user_data: dict[str, Any], session: Session
):
    user_data["email"] = "wrong email"
    with pytest.raises(ValidationError):
        User.register_user(UserClassicIn(**user_data), session)


def test_classic_register_user_ko_email_already_exists(
    user_data: dict[str, Any], session: Session
):
    User.register_user(UserClassicIn(**user_data), session)  # first user
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        # try to create second user with same email
        User.register_user(UserClassicIn(**user_data), session)


def test_classic_register_superuser_ok(user_data: dict[str, Any], session: Session):
    user = User.register_super_user(UserClassicIn(**user_data), session)
    assert user.email == "robert@ledoux.com"
    assert user.first_name == "Robert"
    assert user.last_name == "LEDOUX"
    assert user.is_superuser is True
    assert user.phone_number is None
    assert not hasattr(user, "password")
    assert hasattr(user, "hashed_password")
    assert len(user.badges) == 0
    assert user.linkedin_id is None


def test_handle_linkedin_profile_for_login(session: Session):
    ClassicUserFactory(email="sophie@lol.com")
    LinkedInUserFactory(email="tom@cook.com")

    # Case 1: User exists with `linkedin_id` -> Login
    old_nb_users = User.count(session)
    access_token = User.handle_linkedin_profile(
        profile=LinkedInProfileDictFactory(email="tom@cook.com"),
        session=session,
    )
    assert type(access_token) is AccessJWT
    assert old_nb_users == User.count(session)

    # Case 2: User exists with same email but no linkedin_id -> Deny Access
    old_nb_users = User.count(session)
    access_token = User.handle_linkedin_profile(
        profile=LinkedInProfileDictFactory(email="sophie@lol.com"),
        session=session,
    )
    assert old_nb_users == User.count(session)
    assert access_token is None

    # Case 3: User does not exist -> Signup
    old_nb_users = User.count(session)
    access_token = User.handle_linkedin_profile(
        profile=LinkedInProfileDictFactory(email="john@hamon.com"),
        session=session,
    )
    assert old_nb_users + 1 == User.count(session)
    assert type(access_token) is AccessJWT


def test_linkedin_register_user_ok(session: Session):
    payload = UserLinkedinIn(
        email="Lay@chips.com", first_name="Lay", last_name="Chips", linkedin_id="abcdef"
    )
    user = User.register_linkedin_user(payload, session)
    assert user.email == "lay@chips.com"
    assert user.first_name == "Lay"
    assert user.last_name == "CHIPS"
    assert user.is_superuser is False
    assert user.phone_number is None
    assert not hasattr(user, "password")
    assert user.hashed_password is None
    assert len(user.badges) == 0
    assert user.linkedin_id == "abcdef"
