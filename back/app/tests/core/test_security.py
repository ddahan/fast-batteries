from app.core.security import get_password_hash, verify_password


class TestGetPasswordHash:
    def test_hash_is_different_from_plain_text(self):
        password = "securePassword123"
        hashed_password = get_password_hash(password)
        assert hashed_password != password

    def test_hash_starts_with_bcrypt_identifier(self):
        password = "securePassword123"
        hashed_password = get_password_hash(password)
        assert hashed_password.startswith("$2b$")

    def test_consistent_hash_behavior_with_salting(self):
        password = "securePassword123"
        hashed_password_1 = get_password_hash(password)
        hashed_password_2 = get_password_hash(password)
        # Ensure that hashes are different due to bcrypt salting
        assert hashed_password_1 != hashed_password_2


class TestVerifyPassword:
    def test_correct_password_verifies(self):
        password = "securePassword123"
        hashed_password = get_password_hash(password)
        assert verify_password(password, hashed_password)

    def test_incorrect_password_fails_verification(self):
        password = "securePassword123"
        hashed_password = get_password_hash(password)
        assert not verify_password("wrongPassword123", hashed_password)

    def test_hash_verifies_for_multiple_attempts(self):
        password = "securePassword123"
        hashed_password = get_password_hash(password)
        # Test multiple calls to ensure consistency
        assert verify_password(password, hashed_password)
        assert verify_password(password, hashed_password)
