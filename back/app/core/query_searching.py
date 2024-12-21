from typing import Any, TypeVar

from pydantic import Field
from sqlalchemy import Select, String, cast, or_
from sqlalchemy.orm import InstrumentedAttribute, aliased
from sqlalchemy.sql.elements import BinaryExpression

from app.models.base import MyModel
from app.schemas.base import MySchema

T = TypeVar("T", bound=MyModel)


class Searcher(MySchema):
    model: type[MyModel]
    search: str | None = Field(
        default=None,
        description="Search term (case insensitive)",
    )
    search_model_fields: list[str] = Field(
        description="Model fields in which the search will be run with a `OR` logic"
    )

    def build_search_filter(
        self, attr: InstrumentedAttribute[Any]
    ) -> BinaryExpression[Any]:
        """Insensitive to case search, with explicit casting for non-string columns."""
        return cast(attr, String).ilike(f"%{self.search}%")

    def make_search(self, query: Select[tuple[T]]) -> Select[tuple[T]]:
        """
        Filter the given query using user-provided 'search' field on 'search_model_fields'
        exec() is not called and must be called outside to get actual results
        """
        if self.search == "":
            raise ValueError("Please provide a value if providing search parameter.")

        if self.search and self.search_model_fields:
            search_filters: list[BinaryExpression[Any]] = []
            for raw_model_field in self.search_model_fields:
                nb_double_underscores = raw_model_field.count("__")
                if nb_double_underscores == 0:
                    # Direct field search
                    model_field = raw_model_field
                    new_search_filter = self.build_search_filter(
                        getattr(self.model, model_field)
                    )
                    search_filters.append(new_search_filter)
                elif nb_double_underscores == 1:
                    # Handle relationship fields (e.g., "owner__first_name")
                    model_field, child_model_field = raw_model_field.split("__")

                    # Get the parent model class from its name
                    # e.g. getattr(Badge, "owner") -> <class 'app.models.user.User'>
                    parent_model = getattr(self.model, model_field).property.mapper.class_

                    # Create an alias for the parent model to handle the join
                    # -> <class 'sqlalchemy.orm.util.AliasedClass'>
                    parent_alias = aliased(parent_model)

                    # Get the child field from the parent model
                    # -> <sqlalchemy.orm.attributes.InstrumentedAttribute>
                    child = getattr(parent_alias, child_model_field)

                    # Join the parent model and apply the filter on the child field
                    query = query.join(parent_alias, getattr(self.model, model_field))

                    new_search_filter = self.build_search_filter(child)
                    search_filters.append(new_search_filter)
                else:
                    raise ValueError("Multiple relationships are not supported.")

            # Process the query
            query = query.filter(or_(*search_filters))

        return query


def get_searcher_dep(model: type[MyModel], search_model_fields: list[str]):
    def dependency(search: str | None = None) -> Searcher:
        return Searcher(
            model=model, search=search, search_model_fields=search_model_fields
        )

    return dependency
