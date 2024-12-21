import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.factories.user import ClassicUserDictFactory, ClassicUserFactory, UserFactory
from app.models.user import User
from app.schemas.user import BadgeOwner
from app.utils.testing import patch_bcrypt_hashpw

settings = get_settings()


@pytest.fixture()
def users_data() -> list[User]:
    with patch_bcrypt_hashpw():
        known_user: User = UserFactory(first_name="Abdelkrim", last_name="OUAMARA")
        other_users: list[User] = [
            UserFactory() for _ in range(settings.MAX_ITEMS_PER_PAGE - 1)
        ]  # create_batch() would create a warning and not sure it calls custom create method

    return [known_user] + other_users


route = "/users"


def test_read_users_with_paginator(client: TestClient, users_data: list[User]):
    response = client.get(route)
    page_of_users = response.json()
    assert len(page_of_users["items"]) == settings.DEFAULT_ITEMS_PER_PAGE
    # remove `label` as computed value don't pass input validation
    page_of_users["items"][0].pop("label")
    BadgeOwner.model_validate(page_of_users["items"][0])


def test_read_users_with_searcher(client: TestClient, users_data: list[User]):
    search = "abdelk"
    response = client.get(f"{route}?page=1&pageSize=10&search={search}")
    data = response.json()["items"]
    assert len(data) == 1
    item = data[0]
    assert item["label"] == "Abdelkrim OUAMARA"


def test_register_new_user_ok(client: TestClient, session: Session):
    old_nb_users = User.count(session)
    response = client.post("/users/signup", json=ClassicUserDictFactory())
    assert response.status_code == status.HTTP_200_OK
    assert User.count(session) == old_nb_users + 1


def test_register_new_user_ko_already_exists(client: TestClient, session: Session):
    ClassicUserFactory(email="jean@levis.com")
    old_nb_users = User.count(session)
    response = client.post(
        "/users/signup", json=ClassicUserDictFactory(email="Jean@levis.com")
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["errors"]["field"]["email"]
        == "This email address already exists."
    )
    assert User.count(session) == old_nb_users
