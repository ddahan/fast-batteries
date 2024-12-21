from typing import Annotated, Generic, TypeVar

from fastapi import Depends
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.sql import Select, func

from app.core.config import get_settings
from app.core.database import SessionDep
from app.models.base import MyModel
from app.schemas.base import MySchema

T = TypeVar("T", bound=MyModel)
U = TypeVar("U", bound=MySchema)


class Pagination(MySchema):
    total_items: int = Field(ge=0, description="Number of total items")
    start_index: int = Field(ge=0, description="Starting item index")
    end_index: int = Field(ge=0, description="Ending item index")
    total_pages: int = Field(ge=0, description="Total number of pages")
    requested_page: int = Field(ge=1, description="Requested page number")
    requested_page_size: int = Field(
        ge=1, description="Requested number of items per page"
    )
    current_page: int = Field(ge=0, description="Page number (could differ from request)")
    current_page_size: int = Field(
        ge=0, description="Number of items per page (could differ from request)"
    )


class Page(Pagination, Generic[U]):
    """Model to represent a page of results along with pagination metadata."""

    items: list[U] = Field(description="List of items on this Page")


class Paginator(MySchema):
    page: int = Field(default=1, ge=1, description="Requested page number")
    page_size: int = Field(
        default=get_settings().DEFAULT_ITEMS_PER_PAGE,
        ge=1,
        le=get_settings().MAX_ITEMS_PER_PAGE,
        description="Requested number of items per page",
    )

    def paginate(
        self,
        query: Select[tuple[T]],
        schema: type[U],
        session: SessionDep,
    ) -> Page[U]:
        """Paginate the given query based on the pagination input.
        NOTE: execute() is called and doesn't need to be called.
        """

        # Get the total number of items
        total_items = session.scalar(select(func.count()).select_from(query.subquery()))
        assert isinstance(
            total_items, int
        ), "A database error occurred when getting `total_items`"

        # Handle out-of-bounds page requests by redirecting to the last page instead of
        # displaying empty data.
        total_pages = (total_items + self.page_size - 1) // self.page_size
        # we don't want to have 0 page even if there is no item.
        total_pages = max(total_pages, 1)
        current_page = min(self.page, total_pages)

        # Calculate the offset for pagination
        offset = (current_page - 1) * self.page_size

        # Apply limit and offset to the query
        result = session.execute(query.offset(offset).limit(self.page_size))

        # Fetch the paginated items
        db_items = list(result.scalars().all())

        # Transform database items to schemas
        items = [schema.model_validate(db_item) for db_item in db_items]

        # Calculate the rest of pagination metadata
        start_index = offset + 1 if total_items > 0 else 0
        end_index = min(offset + self.page_size, total_items)

        # Return the paginated response using the Page model
        return Page[U](
            items=items,
            total_items=total_items,
            start_index=start_index,
            end_index=end_index,
            total_pages=total_pages,
            requested_page=self.page,
            requested_page_size=self.page_size,
            current_page_size=len(items),  # can differ from the requested page_size
            current_page=current_page,  # can differ from the requested page
        )


PaginationDep = Annotated[Paginator, Depends()]
