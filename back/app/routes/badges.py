from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.core.database import SessionDep
from app.core.exceptions import BadgeOwnerDoesNotExist, ItemNotFound
from app.core.query_ordering import Orderer, get_orderer_dep
from app.core.query_pagination import Page, PaginationDep
from app.core.query_searching import Searcher, get_searcher_dep
from app.models.badge import Badge
from app.models.user import User
from app.schemas.badge import BadgeCreate, BadgeFullUpdate, BadgeOut, BadgePartialUpdate
from app.utils.strings import SecretId

router = APIRouter(prefix="/badges", tags=["Badges"])


@router.get("", summary="Read all badges", response_model=Page[BadgeOut])
def read_badges(
    session: SessionDep,
    paginator: PaginationDep,
    searcher: Annotated[
        Searcher,
        Depends(get_searcher_dep(Badge, ["id", "owner__first_name", "owner__last_name"])),
    ],
    orderer: Annotated[Orderer, Depends(get_orderer_dep(Badge))],
):
    query = orderer.sort(select(Badge))  # separation of concerns?
    query = searcher.make_search(query)
    return paginator.paginate(query, BadgeOut, session)


@router.get("/{badge_id}", summary="Read a given badge", response_model=BadgeOut)
def read_badge(badge_id: SecretId, session: SessionDep):
    badge = Badge.get_by_id(badge_id, session, exc=ItemNotFound())
    return badge


@router.put(
    "/{badge_id}",
    summary="Update a badge entirely",
    response_model=BadgeOut,
)
def update_badge_entirely(
    badge_id: SecretId, payload: BadgeFullUpdate, session: SessionDep
):
    # Check if the owner exists in the database
    owner = session.get(User, payload.owner_id)
    if not owner:
        raise BadgeOwnerDoesNotExist()

    badge = Badge.get_by_id(badge_id, session, exc=ItemNotFound())

    if badge:
        return badge.update(payload, partial=False, session=session)


@router.patch(
    "/{badge_id}",
    summary="Update a badge partially",
    response_model=BadgeOut,
)
def update_badge_partially(
    badge_id: SecretId, payload: BadgePartialUpdate, session: SessionDep
):
    """note: not used in the app for now. Here as an example.
    Could be absolutely used instead of 'update_badge_entirely' method in our case.
    """
    badge = Badge.get_by_id(badge_id, session, exc=ItemNotFound())
    if badge:
        return badge.update(payload, partial=True, session=session)


@router.patch(
    "/{badge_id}/activity",
    summary="Invert activation state",
    response_model=BadgeOut,
    response_description="The updated badge",
)
def invert_activation_state(badge_id: SecretId, session: SessionDep):
    badge = Badge.get_by_id(badge_id, session, exc=ItemNotFound())
    if badge:
        return badge.invert_activity(session)


@router.post("", summary="Create a new badge", response_model=BadgeOut)
def create_badge(payload: BadgeCreate, session: SessionDep):
    return Badge.create(payload, session)


@router.delete("/{badge_id}", summary="Delete the given badge", response_model=bool)
def destroy_badge(badge_id: SecretId, session: SessionDep):
    return Badge.delete_by_id(badge_id, session, exc=ItemNotFound())
