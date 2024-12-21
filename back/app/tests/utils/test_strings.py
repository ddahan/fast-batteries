from string import ascii_letters, digits

from app.utils.strings import get_secret_id, make_random_str


def test_get_secret_id():
    secret_id = get_secret_id()
    assert isinstance(secret_id, str)
    assert len(secret_id) == 22


def test_make_random_str():
    desired_chars = digits + ascii_letters
    str1 = make_random_str(size=10, chars=desired_chars)
    assert all(c in desired_chars for c in str1)
    assert len(str1) == 10
    str2 = make_random_str(size=10, chars=desired_chars)
    assert str1 != str2
