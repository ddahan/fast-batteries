import random
import secrets
from string import ascii_letters, digits

SecretId = str  # type alias to make it clearer we're dealing with an id.


def get_secret_id() -> SecretId:
    """
    Wrapper to python built-in method to be used as a callable, while ensuring
    nbytes is defined to get the same string length in output.
    nbytes == 16 means a better entropy than uuid4
    """
    return secrets.token_urlsafe(nbytes=16)


def make_random_str(size: int, chars: str = digits + ascii_letters) -> str:
    """Build a random string of `size`, using `chars`."""
    return "".join(random.choice(chars) for _ in range(size))
