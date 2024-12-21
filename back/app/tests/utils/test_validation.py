import pytest
from pydantic import BaseModel, ValidationError

from app.utils.validation import validate_single_field


# Define a sample Pydantic model for testing
class SampleModel(BaseModel):
    name: str
    age: int
    colors: list[str]


def test_validate_single_field():
    # Validate the 'name' field
    validate_single_field("name", "John", SampleModel)

    # Validate the 'age' field
    validate_single_field("age", 25, SampleModel)

    # Validate the 'colors' field
    validate_single_field("colors", ["red", "green"], SampleModel)

    # Validate with an invalid value for 'name'
    with pytest.raises(ValidationError):
        validate_single_field("name", 123, SampleModel)

    # Validate with an invalid value for 'age'
    with pytest.raises(ValidationError):
        validate_single_field("age", "not_a_number", SampleModel)

    # Validate with an invalid value for 'colors'
    with pytest.raises(ValidationError):
        validate_single_field("age", [12, "13"], SampleModel)
