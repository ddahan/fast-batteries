from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.database import SessionDep
from app.core.exceptions import InsufficientPermission, InvalidToken, ItemNotFound
from app.core.security import verify_password
from app.models.user import User
from app.schemas.token import AccessJWT

# The string is not a route, just a helper for openAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/access-token", auto_error=False)

TokenDep = Annotated[str, Depends(oauth2_scheme)]


def authenticate(session: SessionDep, email: str, password: str) -> User | None:
    user = User.get_by("email", email, session=session)
    if not user:
        return None
    if not user.hashed_password:  # user registered by social login
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(session: SessionDep, token_key: TokenDep) -> User:
    user_id = AccessJWT.verify(token_key)
    if not user_id:
        raise InvalidToken()
    user = User.get_by_id(user_id, session)
    if not user:
        raise ItemNotFound(errors={"general": ["User not found."]})
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_current_superuser(current_user: CurrentUserDep) -> User:
    if not current_user.is_superuser:
        raise InsufficientPermission()
    return current_user


CurrentSuperUserDep = Annotated[User, Depends(get_current_superuser)]
