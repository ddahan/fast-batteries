import string
from collections.abc import Callable
from decimal import DivisionByZero

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.exceptions import EmailAlreadyExists, ProjectAPIException
from app.main import app
from app.utils.strings import make_random_str
from app.utils.testing import FixtureResponse

##########################################################################################
# Setup: Client, types and fixtures
##########################################################################################


ExcRunnerFn = Callable[[Exception | None], FixtureResponse]


@pytest.fixture
def exc_runner_response() -> ExcRunnerFn:
    """
    This fixture allow to setup a response that raises the passed exception.
    It returns the response and the errors in a tuple.
    """
    # no need to have a real name here, just a unique one
    route = "/" + make_random_str(32, chars=string.ascii_letters)

    def _exc_runner_response(exc: Exception | None) -> FixtureResponse:
        @app.get(route)
        def _():
            if exc:
                raise exc

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(route)
        errors = response.json().get("errors", None)
        return (response, errors)

    return _exc_runner_response


##########################################################################################
# Actual tests
##########################################################################################


def test_project_exception(exc_runner_response: ExcRunnerFn):
    response, errors = exc_runner_response(EmailAlreadyExists())

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert errors == {"field": {"email": "This email address already exists."}}


def test_project_exception_overriding(exc_runner_response: ExcRunnerFn):
    response, errors = exc_runner_response(
        EmailAlreadyExists(errors={"field": {"email": "Please use another address."}})
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert errors == {"field": {"email": "Please use another address."}}


def test_project_exception_with_multiple_errors(exc_runner_response: ExcRunnerFn):
    class MultipleProblems(ProjectAPIException):
        status_code = status.HTTP_400_BAD_REQUEST
        errors = {
            "general": ["There is something wrong.", "I'll tell you what."],
            "nonfield": ["But not now..."],
            "field": {
                "email": "This email does not exist in the system.",
                "password": "I don't like it.",
            },
        }

    _, errors = exc_runner_response(MultipleProblems())
    assert len(errors["general"]) == 2
    assert len(errors["nonfield"]) == 1
    assert len(errors["field"]) == 2


def test_project_exception_string_formatting_ok(exc_runner_response: ExcRunnerFn):
    class FormatableEmailAlreadyExists(ProjectAPIException):
        status_code = status.HTTP_400_BAD_REQUEST
        errors = {"field": {"email": "{address} already exists."}}

    _, errors = exc_runner_response(FormatableEmailAlreadyExists(address="tim@mail.com"))
    assert errors["field"]["email"] == "tim@mail.com already exists."


def test_project_exception_string_formatting_ko_when_key_is_missing(
    exc_runner_response: ExcRunnerFn,
):
    class FormatableEmailAlreadyExists(ProjectAPIException):
        status_code = status.HTTP_400_BAD_REQUEST
        errors = {"field": {"email": "{address} already exists."}}

    with pytest.raises(ValueError) as exc_info:
        exc_runner_response(FormatableEmailAlreadyExists())

    assert (
        str(exc_info.value)
        == "Error formatting message: missing key 'address' in message_kwargs"
    )


def test_uncaught_exception(
    exc_runner_response: ExcRunnerFn,
):
    response, errors = exc_runner_response(DivisionByZero())
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert errors["general"] == [
        "An unknown error has occurred. Please contact an administrator."
    ]
