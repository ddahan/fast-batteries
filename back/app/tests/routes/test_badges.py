import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.factories.badge import BadgeFactory
from app.models.badge import Badge
from app.utils.testing import patch_bcrypt_hashpw


@pytest.fixture()
def badges_data() -> list[Badge]:
    with patch_bcrypt_hashpw():
        return [BadgeFactory() for _ in range(12)]


route = "/badges"


def test_read_badges(client: TestClient, badges_data: list[Badge]):
    response = client.get(route)
    page_of_badges = response.json()
    assert len(page_of_badges["items"]) == 10


def test_read_badge_ok(client: TestClient, badges_data: list[Badge], session: Session):
    badge = badges_data[3]
    response = client.get(route + f"/{badge.id}")
    assert response.json()["id"] == badge.id
    assert response.json()["owner"]["id"] == badge.owner_id


def test_read_badge_ko_does_not_exist(client: TestClient):
    response = client.get(route + "/fake-id-that-does-not-exist")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["errors"]["general"] == ["Item not found."]


def test_update_badge_entirely_ok(client: TestClient, badges_data: list[Badge]):
    badge = badges_data[3]
    other_owner = badges_data[4].owner
    payload = dict(
        owner_id=other_owner.id, is_active=False, expire_at="2028-12-12T16:30:00+01:00"
    )
    response = client.put(route + f"/{badge.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["owner"]["id"] == other_owner.id
    assert response.json()["isActive"] is False
    assert response.json()["expireAt"] == "2028-12-12T16:30:00+01:00"


def test_update_badge_entirely_ko_payload_not_full(
    client: TestClient, badges_data: list[Badge]
):
    badge = badges_data[3]
    other_owner = badges_data[4].owner
    payload = dict(owner_id=other_owner.id, is_active=False)
    response = client.put(route + f"/{badge.id}", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["errors"]["field"]["expireAt"] == "Field required"


def test_update_badge_entirely_ko_owner_does_not_exist(
    client: TestClient, badges_data: list[Badge]
):
    badge = badges_data[3]
    payload = dict(
        owner_id="unexisting_id", is_active=False, expire_at="2028-12-12T16:30:00+01:00"
    )
    response = client.put(route + f"/{badge.id}", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_badge_partially_ok(client: TestClient, badges_data: list[Badge]):
    badge = badges_data[3]
    assert badge.is_active is True
    payload = dict(is_active=False)
    response = client.patch(route + f"/{badge.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["isActive"] is False


def test_invert_activation_state_ok(client: TestClient, badges_data: list[Badge]):
    badge = badges_data[3]
    assert badge.is_active is True
    response = client.patch(route + f"/{badge.id}/activity")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["isActive"] is False


def test_create_badge(client: TestClient, badges_data: list[Badge], session: Session):
    old_badge_count = Badge.count(session)
    payload = dict(
        owner_id=badges_data[1].owner_id,
        is_active=True,
        expire_at="2028-12-12T16:30:00+01:00",
    )

    response = client.post(route, json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert old_badge_count == Badge.count(session) - 1


def test_destroy_badge_ok(client: TestClient, badges_data: list[Badge], session: Session):
    old_badge_count = Badge.count(session)
    badge = badges_data[3]
    response = client.delete(route + f"/{badge.id}")
    assert response.status_code == status.HTTP_200_OK
    assert old_badge_count == Badge.count(session) + 1
