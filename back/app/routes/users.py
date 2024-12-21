from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.core.database import SessionDep
from app.core.exceptions import EmailAlreadyExists
from app.core.query_pagination import Page, PaginationDep
from app.core.query_searching import Searcher, get_searcher_dep
from app.models.user import User
from app.schemas.message import Message
from app.schemas.user import BadgeOwner, UserClassicIn

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    summary="Read all users with pagination",
    response_model=Page[BadgeOwner],
)
def read_users(
    session: SessionDep,
    paginator: PaginationDep,
    searcher: Annotated[
        Searcher,
        Depends(get_searcher_dep(User, ["first_name", "last_name"])),
    ],
):
    query = searcher.make_search(select(User))  # separation of concerns?
    return paginator.paginate(query, BadgeOwner, session)


@router.post(
    "/signup",
    summary="Register a new user (the classic way)",
    response_model=Message,
)
def register_user(session: SessionDep, payload: UserClassicIn):
    user = User.get_by("email", payload.email, session)
    if user:
        raise EmailAlreadyExists()

    User.register_user(payload, session)
    return Message(message="Account created succesfully.")
