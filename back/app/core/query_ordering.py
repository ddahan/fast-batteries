from typing import Self, TypeVar

from pydantic import Field, field_validator, model_validator
from pydantic.alias_generators import to_snake
from sqlalchemy import Select

from app.models.base import MyModel
from app.schemas.base import MySchema

T = TypeVar("T", bound=MyModel)


class Orderer(MySchema):
    model: type[MyModel]
    ordering: str | None = Field(default=None, description="Field to use to sort item.")

    @field_validator("ordering", mode="before")
    def camel_to_snake(cls, value: str | None):
        """This way, a given ordering value can be both in camel or snake case."""
        if value is not None:
            if value.startswith("-"):  # converted to '_' by default!
                return "-" + to_snake(value[1:])
            else:
                return to_snake(value)

    @property
    def unsigned_ordering(self) -> str | None:
        if self.ordering is not None:
            return self.ordering.replace("-", "").replace("+", "")

    @model_validator(mode="after")
    def check_existing_ordering_field(self) -> Self:
        if self.unsigned_ordering is not None:
            if self.unsigned_ordering == "":
                raise ValueError("Empty ordering passed.")
            if not hasattr(self.model, self.unsigned_ordering):
                raise ValueError(
                    f"Invalid ordering field: '{self.unsigned_ordering}' does not exist on the model '{self.model.__name__}'."
                )
        return self

    def sort(self, query: Select[tuple[T]]) -> Select[tuple[T]]:
        """Order the given query based on the ordering input
        exec() is not called and must be called outside to get actual results
        """

        if self.ordering and self.unsigned_ordering:
            direction = "desc" if self.ordering.startswith("-") else "asc"
            column_attr = getattr(self.model, self.unsigned_ordering)

            if direction == "desc":
                query = query.order_by(column_attr.desc())
            else:
                query = query.order_by(column_attr)

        return query


def get_orderer_dep(model: type[T]):
    def dependency(ordering: str | None = None) -> Orderer:
        return Orderer(ordering=ordering, model=model)

    return dependency
