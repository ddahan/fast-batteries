from sqlalchemy import select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.models.base import MyModel
from app.utils.orm import model_to_dict


class SomeGuy(MyModel):
    name: Mapped[str] = mapped_column(primary_key=True)
    age: Mapped[int]


def test_model_to_dict(session: Session):
    # Create an instance of SomeGuy
    instance = SomeGuy(name="John", age=23)
    session.add(instance)
    session.commit()

    # Query the instance from the database
    stmt = select(SomeGuy)
    obj = session.execute(stmt).scalars().one_or_none()
    assert obj

    # Convert the model to a dictionary
    result = model_to_dict(obj)

    # Assert the dictionary matches the model's attributes
    assert result == {
        "name": "John",
        "age": 23,
    }
