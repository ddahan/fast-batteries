from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.security import get_password_hash
from app.models.base import MyModel, SecretIdModel
from app.schemas.token import AccessJWT
from app.schemas.user import UserClassicIn, UserLinkedinIn

if TYPE_CHECKING:
    from app.models.badge import Badge


class User(SecretIdModel, MyModel):
    __table_args__ = (
        CheckConstraint(
            "(hashed_password IS NOT NULL AND linkedin_id IS NULL) OR "
            "(hashed_password IS NULL AND linkedin_id IS NOT NULL)",
            name="check_auth_method_consistency",
        ),
    )
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    phone_number: Mapped[str | None]
    badges: Mapped[list[Badge]] = relationship(back_populates="owner")
    hashed_password: Mapped[str | None] = mapped_column(default=None)
    linkedin_id: Mapped[str | None] = mapped_column(index=True, unique=True, default=None)
    is_superuser: Mapped[bool]

    def __repr__(self) -> str:
        return f"< {self.__class__.__name__} {self.id} >"

    @classmethod
    def register_user(cls, user_payload: UserClassicIn, session: Session) -> User:
        """
        Classic Registration with user/password
        This supposes the user does not already exist in database
        """
        # If UserClassicRegister and User share the same fields (or overlapping ones),
        # Pydantic validation can successfully transform or validate payload into a
        # UserClassicRegister instance.
        UserClassicIn.model_validate(user_payload)
        new_user = cls(
            **user_payload.model_dump(exclude={"password"}),
            hashed_password=get_password_hash(user_payload.password.get_secret_value()),
            is_superuser=False,
        )
        return new_user.save(session)

    @classmethod
    def register_super_user(cls, user_payload: UserClassicIn, session: Session) -> User:
        UserClassicIn.model_validate(user_payload)
        new_user = cls(
            **user_payload.model_dump(exclude={"password"}),
            hashed_password=get_password_hash(user_payload.password.get_secret_value()),
            is_superuser=True,
        )
        return new_user.save(session)

    @classmethod
    def register_linkedin_user(
        cls, user_payload: UserLinkedinIn, session: Session
    ) -> User:
        new_user = User(
            **user_payload.model_dump(),
            is_superuser=False,
        )
        return new_user.save(session)

    @classmethod
    def handle_linkedin_profile(
        cls, profile: dict[str, str], session: Session
    ) -> AccessJWT | None:
        """
        After a user authenticates successfuly using Linked In, we define the right action
        to do (signup, login, or deny access).
        As we need to login the user (even after a sign up), we return the access token.
        """

        linkedin_user_model = UserLinkedinIn(
            linkedin_id=profile["sub"],
            first_name=profile["given_name"],
            last_name=profile["family_name"],
            email=profile["email"],  # handles normalization
        )

        user = User.get_by("email", linkedin_user_model.email, session)
        if user:
            # Case 1: User exists with `linkedin_id` -> Login
            if user.linkedin_id:
                return AccessJWT.create(user.id)
            # Case 2: User exists with same email but no linkedin_id -> Deny Access
            return None

        # Case 3: User does not exist -> Signup
        new_user = cls.register_linkedin_user(linkedin_user_model, session)
        return AccessJWT.create(new_user.id)
