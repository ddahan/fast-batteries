# Test paginator
import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.query_pagination import Page, Paginator
from app.models.base import MyModel, SecretIdModel
from app.schemas.base import MySchema

settings = get_settings()


class PaginationObj(SecretIdModel, MyModel):
    """Simple object used for these tests only, to avoid coupling with real objects."""


class PaginationSch(MySchema):
    """Corresponding schema"""

    id: str


query = select(PaginationObj)  # will be the same for all the tests


def test_paginator_wrong_input_values():
    # Page 0 or negative can't exist
    with pytest.raises(ValidationError):
        Paginator(page=0)
    with pytest.raises(ValidationError):
        Paginator(page=-1)

    # Page size can't be lower than 1
    with pytest.raises(ValidationError):
        Paginator(page_size=0)
    with pytest.raises(ValidationError):
        Paginator(page_size=-1)

    # Page size can't be higher than the max defined in the settings
    with pytest.raises(ValidationError):
        Paginator(page_size=settings.MAX_ITEMS_PER_PAGE + 1)


def test_paginator_with_zero_objects(session: Session):
    def _test(page: int, page_size: int):
        """Helper to avoid repeat same tests"""
        paginator = Paginator(page=page, page_size=page_size)
        p: Page[PaginationSch] = paginator.paginate(query, PaginationSch, session)
        assert len(p.items) == 0
        assert p.total_items == 0
        assert p.start_index == 0
        assert p.end_index == 0
        assert p.total_pages == 1
        assert p.requested_page == page
        assert p.requested_page_size == page_size
        assert p.current_page_size == 0
        assert p.current_page == 1

    _test(page=1, page_size=10)
    _test(page=9999, page_size=10)
    _test(page=1, page_size=1)
    _test(page=9999, page_size=1)


def test_paginator_with_single_object(session: Session):
    PaginationObj().save(session)  # create a single object

    def _test(page: int, page_size: int):
        paginator = Paginator(page=page, page_size=page_size)
        p: Page[PaginationSch] = paginator.paginate(query, PaginationSch, session)
        assert len(p.items) == 1
        assert p.total_items == 1
        assert p.start_index == 1
        assert p.end_index == 1
        assert p.total_pages == 1
        assert p.requested_page == page
        assert p.requested_page_size == page_size
        assert p.current_page_size == 1
        assert p.current_page == 1

    _test(page=1, page_size=10)
    _test(page=9999, page_size=10)
    _test(page=1, page_size=1)
    _test(page=9999, page_size=1)


def test_paginator_with_multiple_objects(session: Session):
    [PaginationObj().save(session) for _ in range(24)]  # create 24 objects (arbitrary)

    def _test(page: int, page_size: int) -> Page[PaginationSch]:
        paginator = Paginator(page=page, page_size=page_size)
        p: Page[PaginationSch] = paginator.paginate(query, PaginationSch, session)
        assert p.requested_page == page
        assert p.requested_page_size == page_size
        return p

    p = _test(page=1, page_size=10)
    assert len(p.items) == 10
    assert p.total_items == 24
    assert p.start_index == 1
    assert p.end_index == 10
    assert p.total_pages == 3
    assert p.current_page_size == 10
    assert p.current_page == 1

    p = _test(page=2, page_size=10)
    assert len(p.items) == 10
    assert p.total_items == 24
    assert p.start_index == 11
    assert p.end_index == 20
    assert p.total_pages == 3
    assert p.current_page_size == 10
    assert p.current_page == 2

    p = _test(page=9999, page_size=10)  # should go to the last page (3rd)
    assert len(p.items) == 4
    assert p.total_items == 24
    assert p.start_index == 21
    assert p.end_index == 24
    assert p.total_pages == 3
    assert p.current_page_size == 4
    assert p.current_page == 3

    p = _test(page=1, page_size=1)  # weird test as we would not do this
    assert len(p.items) == 1
    assert p.total_items == 24
    assert p.start_index == 1
    assert p.end_index == 1
    assert p.total_pages == 24
    assert p.current_page_size == 1
    assert p.current_page == 1

    p = _test(page=2, page_size=12)  # page size is a multiple of nb_objects (2*12 == 24)
    assert len(p.items) == 12
    assert p.total_items == 24
    assert p.start_index == 13
    assert p.end_index == 24
    assert p.total_pages == 2
    assert p.current_page_size == 12
    assert p.current_page == 2
