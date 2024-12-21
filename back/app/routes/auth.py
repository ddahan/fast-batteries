from typing import Annotated
from urllib.parse import urljoin

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import CurrentUserDep, authenticate
from app.core.config import get_settings
from app.core.database import SessionDep
from app.core.emails import send_reset_password_email
from app.core.exceptions import (
    BadCredentials,
    InvalidToken,
    UserCanNotResetPassword,
    UserDoesNotExist,
)
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.message import Message
from app.schemas.token import AccessJWT, ResetPasswordJWT
from app.schemas.user import UserPublic, UserResetPassword, UserSendResetPassword

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/access-token", response_model=AccessJWT)
def access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> AccessJWT:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate(  # `username`is OAuth spec (even if it's actually an email)
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise BadCredentials()
    access_jwt = AccessJWT.create(user.id)
    return access_jwt


@router.get("/me", response_model=UserPublic)
def me(current_user: CurrentUserDep):
    return current_user


@router.post("/send-reset-password-link", response_model=Message)
def send_reset_password_link(payload: UserSendResetPassword, session: SessionDep):
    email = payload.email
    user = User.get_by("email", email, session=session)
    if not user:
        raise UserDoesNotExist()
    if not user.hashed_password:
        raise UserCanNotResetPassword()
    password_reset_token = ResetPasswordJWT.create(email=email)
    front_reset_password_url = urljoin(
        settings.FRONT_URL, f"auth/reset-password?tokenKey={password_reset_token.key}"
    )
    send_reset_password_email(
        email_to=email, front_reset_password_url=front_reset_password_url
    )

    return Message(message="Reset password email sent.")


@router.post("/reset-password", response_model=Message)
def reset_password(session: SessionDep, payload: UserResetPassword):
    email = ResetPasswordJWT.verify(payload.token_key)
    if not email:
        raise InvalidToken()
    user = User.get_by("email", email, session=session)
    if not user:
        raise UserDoesNotExist()
    user.hashed_password = get_password_hash(payload.new_password.get_secret_value())
    user.save(session)

    return Message(message="Password updated successfully.")
