from collections.abc import Callable
from typing import Any, TypeVar, get_args

from pydantic import SecretStr, ValidationError
from pydantic_extra_types.phone_numbers import PhoneNumber
from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.models.base import MyModel
from app.schemas.base import MySchema
from app.utils.orm import model_to_dict
from app.utils.validation import validate_single_field


def CustomTable(title: str) -> Table:
    """Rich table with shared UI"""

    return Table(
        title=title,
        title_justify="left",
        title_style="bold green underline",
        show_header=False,
        box=box.SIMPLE,
        row_styles=["cyan"],
    )


T = TypeVar("T", bound=MyModel)
U = TypeVar("U", bound=MySchema)


def create_object_from_cli(
    schema_in: type[U],
    create_method: Callable[[U, Session], T],
    friendly_name: str,
):
    """
    Base Function for creating an object by prompting the user field by field
    Use it as a base to create dedicated functions (like 'create_superuser')

    Args:
        * schema_in: The Pydantic schema used to parse and validate the CLI input.
        * create_method: A callable that handles the creation logic.
        It will be fed with an instance of the schema and a database session as arguments
        * friendly_name: A displayable name of the object being created.
    """
    input_data: dict[str, Any] = {}
    console = Console()

    # Prompt the user to enter data
    console.print(f"Please fill the following fields to create a {friendly_name} object:")
    for field_name, field_info in schema_in.model_fields.items():
        while "the entered input is not valid":
            value = Prompt.ask(
                f"{field_name}", password=(field_info.annotation == SecretStr)
            )
            # Special cases
            if PhoneNumber in [field_info.annotation, get_args(field_info.annotation)]:
                value = PhoneNumber(value)
            if value in ["", "null", "None"]:
                value = None
            # Main logic
            try:
                # Use Pydantic's model field validation to validate the field
                validated_value: Any = validate_single_field(
                    field_name=field_name, value=value, schema=schema_in
                )
            except ValidationError as e:
                console.print(f"{e.errors()[0]['msg']}. Please try again.", style="red")
            else:
                input_data[field_name] = getattr(validated_value, field_name)
                break

    # Convert schema to database model
    session: Session = next(get_session())
    new_object: T = create_method(schema_in(**input_data), session)
    session.refresh(new_object)

    if new_object:
        table = CustomTable(f"\n{friendly_name} created successfully.")
        object_as_dict = model_to_dict(new_object)
        for k, v in object_as_dict.items():
            table.add_row(k, str(v))

        console.print(table)
