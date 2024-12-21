import pytest
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.query_searching import Searcher
from app.models.base import MyModel
from app.utils.strings import SecretId


class SearchingObj(MyModel):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sub: Mapped["SearchingSubObj"] = relationship(back_populates="searching_objs")
    sub_id: Mapped[SecretId | None] = mapped_column(
        ForeignKey("tb_searching_sub_obj.id"), nullable=True
    )
    col_a: Mapped[str]
    col_b: Mapped[int] = mapped_column(default=1)
    col__c: Mapped[str | None] = mapped_column(nullable=True)


class SearchingSubObj(MyModel):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    searching_objs: Mapped[list["SearchingObj"]] = relationship(back_populates="sub")
    col_d: Mapped[int]


@pytest.fixture
def items(
    search: str,
    search_model_fields: list[str],
    items_to_create: list[SearchingObj],
    session: Session,
) -> list[SearchingObj]:
    """Get ordered items using parameters"""
    searcher = Searcher(
        model=SearchingObj, search=search, search_model_fields=search_model_fields
    )

    # create items in database
    for item in items_to_create:
        item.save(session)

    # make the query and returns the items
    query = searcher.make_search(select(SearchingObj))
    result = session.execute(query)
    return list(result.scalars().all())


@pytest.mark.parametrize(
    "search,search_model_fields,items_to_create",
    [
        (
            "dav",  # search
            ["col_a", "col_b"],  # search_model_fields
            [SearchingObj(col_a="david", col_b=36)],  # items_to_create
        )
    ],
)
def test_search_ok_found_with_string(items: list[SearchingObj]):
    assert len(items) == 1
    assert items[0].col_a == "david"


@pytest.mark.parametrize(
    "search,search_model_fields,items_to_create",
    [
        (
            "dav",  # search
            ["col_a", "col_b"],  # search_model_fields
            [
                SearchingObj(col_a="david"),  # yes
                SearchingObj(col_a="david"),  # yes
                SearchingObj(col_a="davy"),  # yes
                SearchingObj(col_a="robert"),  # no
            ],
        )
    ],
)
def test_search_ok_found_with_multiple_results(items: list[SearchingObj]):
    assert len(items) == 3


@pytest.mark.parametrize(
    "search,search_model_fields,items_to_create",
    [
        (
            "rob",
            ["col_a", "col_b"],
            [SearchingObj(col_a="david", col_b=36)],
        )
    ],
)
def test_search_ok_not_found_with_string(items: list[SearchingObj]):
    assert items == []


@pytest.mark.parametrize(
    "search,search_model_fields,items_to_create",
    [
        (
            "3",
            ["col_a", "col_b"],
            [SearchingObj(col_a="david", col_b=36)],
        )
    ],
)
def test_search_ok_with_integer(items: list[SearchingObj]):
    assert len(items) == 1
    assert items[0].col_a == "david"


@pytest.mark.parametrize(
    "search,search_model_fields,items_to_create",
    [
        (
            "4",
            ["col_a", "col_b"],
            [SearchingObj(col_a="david", col_b=36)],
        )
    ],
)
def test_search_ok_not_found_with_integer(items: list[SearchingObj]):
    assert items == []


def test_search_ko_empty_field():
    searcher = Searcher(model=SearchingObj, search="", search_model_fields=["col_a"])
    with pytest.raises(ValueError):
        searcher.make_search(select(SearchingObj))


def test_search_ko_with_multiple_relationships():
    searcher = Searcher(
        model=SearchingObj, search="foo", search_model_fields=["col_a__col_b__col_c"]
    )
    with pytest.raises(ValueError):
        searcher.make_search(select(SearchingObj))


@pytest.mark.parametrize(
    "search,search_model_fields,items_to_create",
    [
        (
            "36",
            ["col_a", "col_b"],
            [SearchingObj(col_a="david360", col_b=36)],
        )
    ],
)
def test_search_ok_not_duplicated_if_in_two_different_fields(items: list[SearchingObj]):
    assert len(items) == 1


@pytest.mark.parametrize(
    "search,search_model_fields,items_to_create",
    [
        (
            "dAV",
            ["col_a", "col_b"],
            [SearchingObj(col_a="David")],
        )
    ],
)
def test_search_case_insensitivity(items: list[SearchingObj]):
    assert len(items) == 1


@pytest.mark.parametrize(
    "search,search_model_fields,items_to_create",
    [
        (
            "42",
            ["sub__col_d"],
            [
                SearchingSubObj(id=777, col_d=42),
                SearchingObj(col_a="david", sub_id=777),
            ],
        )
    ],
)
def test_search_ok_with_relationship(items: list[SearchingObj], session: Session):
    assert len(items) == 1
    assert items[0].sub and items[0].sub.id == 777
