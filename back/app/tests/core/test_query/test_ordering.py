import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.query_ordering import Orderer
from app.models.base import MyModel


class OrderingObj(MyModel):
    """Simple object used for these tests only, to avoid coupling with real objects."""

    id: Mapped[str] = mapped_column(primary_key=True)
    col_b: Mapped[int]


@pytest.fixture
def data(session: Session) -> None:
    OrderingObj(id="b", col_b=3).save(session)
    OrderingObj(id="a", col_b=1).save(session)
    OrderingObj(id="c", col_b=2).save(session)
    OrderingObj(id="d", col_b=-1).save(session)


@pytest.fixture
def items(
    data: None, request: pytest.FixtureRequest, session: Session
) -> list[OrderingObj]:
    """Get ordered items using parameters"""
    orderer = Orderer(model=OrderingObj, ordering=request.param)
    query = orderer.sort(select(OrderingObj))
    result = session.execute(query)
    return list(result.scalars().all())


@pytest.mark.parametrize("items", ["id"], indirect=True)
def test_orderer_ok(items: list[OrderingObj]):
    assert [item.id for item in items] == ["a", "b", "c", "d"]


@pytest.mark.parametrize("items", ["+id"], indirect=True)
def test_orderer_ok_id_plus_sign(items: list[OrderingObj]):
    assert [item.id for item in items] == ["a", "b", "c", "d"]


@pytest.mark.parametrize("items", ["-id"], indirect=True)
def test_orderer_ok_id_minus_sign(items: list[OrderingObj]):
    assert [item.id for item in items] == ["d", "c", "b", "a"]


@pytest.mark.parametrize("items", ["col_b"], indirect=True)
def test_orderer_ok_col_b(items: list[OrderingObj]):
    assert [item.id for item in items] == ["d", "a", "c", "b"]


@pytest.mark.parametrize("items", ["-col_b"], indirect=True)
def test_orderer_ok_col_b_minus_sign(items: list[OrderingObj]):
    assert [item.id for item in items] == ["b", "c", "a", "d"]


@pytest.mark.parametrize("items", ["colB"], indirect=True)
def test_orderer_ok_colB(items: list[OrderingObj]):
    assert [item.id for item in items] == ["d", "a", "c", "b"]


@pytest.mark.parametrize("items", ["-colB"], indirect=True)
def test_orderer_ok_colB_minus_sign(items: list[OrderingObj]):
    assert [item.id for item in items] == ["b", "c", "a", "d"]


def test_orderer_invalid_field():
    with pytest.raises(ValidationError):
        Orderer(model=OrderingObj, ordering="unexisting_field")
        # no need to go further in the logic


def test_orderer_empty_field():
    with pytest.raises(ValidationError):
        Orderer(model=OrderingObj, ordering="")
        # no need to go further in the logic
