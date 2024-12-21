import string
from collections.abc import Callable
from typing import Any, Literal

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.main import app
from app.utils.strings import make_random_str
from app.utils.testing import FixtureResponse

##########################################################################################
# Setup: Client, types and fixtures
##########################################################################################


class PydanticTestModel(BaseModel):
    """All-in-one Pydantic Model allowing to test validation"""

    name: str
    age: int = Field(gt=0)


PydanticValidationResponseFn = Callable[[Any, Literal["json", "data"]], FixtureResponse]


@pytest.fixture
def validation_response() -> PydanticValidationResponseFn:
    """
    This fixture allow to setup a response that require a json payload (to test Pydantic)
    """
    route = "/" + make_random_str(32, chars=string.ascii_letters)

    def _validation_response(
        payload: Any, post_method: Literal["json", "data"]
    ) -> FixtureResponse:
        @app.post(route)
        def _(_: PydanticTestModel): ...  # will trigger Pydantic validation

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(route, **{post_method: payload})

        if response.json():
            errors = response.json().get("errors")
        else:
            errors: dict[str, Any] = dict()
        return (response, errors)

    return _validation_response


##########################################################################################
# Actual tests
##########################################################################################


def test_pydantic_no_exception(
    validation_response: PydanticValidationResponseFn,
):
    response, errors = validation_response({"name": "David", "age": 35}, "json")
    assert response.status_code == status.HTTP_200_OK
    assert errors == {}


def test_pydantic_exception_missing_field(
    validation_response: PydanticValidationResponseFn,
):
    response, errors = validation_response({"name": "David"}, "json")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert errors["field"]["age"] == "Field required"


def test_pydantic_exception_wrong_fielf_value(
    validation_response: PydanticValidationResponseFn,
):
    response, errors = validation_response({"name": "David", "age": -1}, "json")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert errors["field"]["age"] == "Input should be greater than 0"


def test_pydantic_exception_wrong_field_type(
    validation_response: PydanticValidationResponseFn,
):
    response, errors = validation_response({"name": 35, "age": 35}, "json")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert errors["field"]["name"] == "Input should be a valid string"


def test_pydantic_exception_multiple_errors(
    validation_response: PydanticValidationResponseFn,
):
    response, errors = validation_response({"name": 35}, "json")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert errors["field"]["age"] == "Field required"
    assert errors["field"]["name"] == "Input should be a valid string"


def test_pydantic_json_wrong_format(
    validation_response: PydanticValidationResponseFn,
):
    raw_payload = '{"name": "Tom", "age": 35}_'  # note the trailing underscore
    # using 'data' instead of 'json' passes the raw data as a JSON string
    with pytest.warns(DeprecationWarning):
        response, errors = validation_response(raw_payload, "data")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "The JSON payload is not formatted properly." in errors["general"]
