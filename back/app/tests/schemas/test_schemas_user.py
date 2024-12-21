import pytest

from app.schemas.user import BadgeOwner, UserBaseIn


class TestUserBaseIn:
    @pytest.fixture()
    @staticmethod
    def user() -> UserBaseIn:
        return UserBaseIn(
            email="  KÉVIN@LOU.com", first_name="  Kévin-Lou", last_name="Garou"
        )

    def test_normalize_email(self, user: UserBaseIn):
        assert user.email == "kévin@lou.com"

    def test_normalize_first_name(self, user: UserBaseIn):
        assert user.first_name == "Kévin-lou"

    def test_normalize_last_name(self, user: UserBaseIn):
        assert user.last_name == "GAROU"


class TestBadgeOwner:
    @pytest.fixture()
    @staticmethod
    def badge_owner() -> BadgeOwner:
        return BadgeOwner(id="abc", first_name="Jean-Lou", last_name="Garou")

    def test_full_name(self, badge_owner: BadgeOwner):
        assert badge_owner.full_name == "Jean-Lou Garou"

    def test_full_name_alias(self, badge_owner: BadgeOwner):
        serialized = badge_owner.model_dump(by_alias=True)
        assert serialized["label"] == "Jean-Lou Garou"
