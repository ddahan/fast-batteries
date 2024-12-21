from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def validate_single_field(field_name: str, value: Any, schema: type[T]) -> Any:
    """
    Validate a single field of a given model and return the model.
    https://github.com/pydantic/pydantic/discussions/7367
    NOTE: should be replaced by https://docs.pydantic.dev/latest/concepts/experimental/#partial-validation
    """
    return schema.__pydantic_validator__.validate_assignment(
        schema.model_construct(), field_name, value
    )
