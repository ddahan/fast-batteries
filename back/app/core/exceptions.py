from typing import TypedDict

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError

from app.core.config import get_settings

settings = get_settings()

##########################################################################################
# Types and holders
##########################################################################################

Message = str  # could be a more complex Error(TypedDict) in the future


class ErrorPayload(TypedDict, total=False):
    general: list[Message]  # general error for toast notifications
    nonfield: list[Message]  # non-field errors for form-level messages
    field: dict[str, Message]  # field-specific errors for individual form fields


class ProjectAPIException(Exception):
    """
    Abstract Base Class for custom errors to be returned to the client
    - Custom project API exceptions have default attributes when defined, but these
    attributes can be overrided at instanciation.
    - Messages can be plain message of formatable messages.
    """

    status_code: int
    errors: ErrorPayload

    def __init__(
        self,
        status_code: int | None = None,
        errors: ErrorPayload | None = None,
        **message_kwargs: str,
    ):
        self.status_code = status_code or self.__class__.status_code
        self.errors = self.format_errors(
            errors or self.__class__.errors, **message_kwargs
        )

    def format_errors(self, errors: ErrorPayload, **message_kwargs: str) -> ErrorPayload:
        """
        Use Python string formatting to inject variables into the error messages.
        Limitation: won't work if a name is used twice in the payload.
        """

        def safe_format(message: str) -> str:
            """Provide a clean developer error message for missing keys"""
            try:
                return message.format(**message_kwargs)
            except KeyError as e:
                raise ValueError(
                    f"Error formatting message: missing key '{e.args[0]}' in message_kwargs"
                ) from e

        formatted_errors: ErrorPayload = {}
        if "general" in errors:
            # For general errors (a list of messages)
            formatted_errors["general"] = [safe_format(msg) for msg in errors["general"]]

        if "nonfield" in errors:
            # For non-field errors (a list of messages)
            formatted_errors["nonfield"] = [
                safe_format(msg) for msg in errors["nonfield"]
            ]

        if "field" in errors:
            # For field-specific errors (a dict of field names to messages)
            formatted_errors["field"] = {
                field: safe_format(msg) for field, msg in errors["field"].items()
            }

        return formatted_errors


##########################################################################################
# Pre-defined errors
##########################################################################################


class InvalidToken(ProjectAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    errors = {
        "general": ["Could not validate existing credentials. Please log in again."]
    }


class InsufficientPermission(ProjectAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    errors = {"general": ["The user doesn't have enough privileges."]}


class BadCredentials(ProjectAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    errors = {"nonfield": ["Incorrect email or password."]}


class EmailAlreadyExists(ProjectAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    errors = {"field": {"email": "This email address already exists."}}


class UserDoesNotExist(ProjectAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    errors = {"field": {"email": "This email does not exist in the system."}}


class BadgeOwnerDoesNotExist(ProjectAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    errors = {"field": {"owner_id": "This user does not exist in the system."}}


class UserCanNotResetPassword(ProjectAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    errors = {
        "field": {
            "email": "This account is linked to a social login and therefore its password cannot be reset."
        }
    }


class ItemNotFound(ProjectAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    errors = {"general": ["Item not found."]}


##########################################################################################
# Utils
##########################################################################################


def add_cors(request: Request, response: JSONResponse) -> JSONResponse:
    """
    CORS headers are not automatically added to error handlers with FastAPI
    cf. https://github.com/fastapi/fastapi/discussions/8027
    """
    cors_headers = {
        "Access-Control-Allow-Methods": ", ".join(settings.CORS_ALLOW_METHODS),
        "Access-Control-Allow-Headers": ", ".join(settings.CORS_ALLOW_HEADERS),
        "Access-Control-Allow-Credentials": str(settings.CORS_ALLOW_CREDENTIALS).lower(),
    }

    # If the origin is in the allowed list, add it to the CORS headers
    origin = request.headers.get("origin")
    if origin in settings.CORS_ALLOW_ORIGIN:
        cors_headers["Access-Control-Allow-Origin"] = origin

    response.headers.update(cors_headers)
    return response


##########################################################################################
# Exception handlers
# ('async' is necessary to keep the right function signature)
##########################################################################################


async def project_api_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Handle project API errors"""
    assert isinstance(exc, ProjectAPIException)  # help for type checking
    status_code = exc.__dict__.pop("status_code")
    return JSONResponse(status_code=status_code, content=exc.__dict__)


async def validation_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Handle invalid request with Pydantic providing more information"""

    assert isinstance(
        exc, (RequestValidationError | ValidationError)
    )  # help for type checking

    def format_pydantic_errors(
        exc: RequestValidationError | ValidationError,
    ) -> ErrorPayload:
        """
        Convert Pydantic validation errors into a format that matches our custom error
        structure.
        """
        errors: ErrorPayload = {}

        for error in exc.errors():
            # Specific case of malformated JSON
            if error.get("type") == "json_invalid":
                errors["general"] = ["The JSON payload is not formatted properly."]
            else:  # all other cases
                loc = error.get("loc", [])
                # TODO : maybe use str(error["ctx"]["error"]) to get clean message
                # because raw 'msg' contains "Value Error, ..."
                msg = error.get("msg", "Invalid input.")

                if len(loc) > 0:
                    field_name = str(loc[-1])
                    errors.setdefault("field", {})[field_name] = msg
                else:  # assuming it's not a field name, fallback to generic error
                    errors["general"] = [msg]

        return errors

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": format_pydantic_errors(exc)},
    )


async def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any other internal exceptions that are not caught, to raise a 500"""
    logger.exception(f"Internal error occurred: {exc}")
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "errors": {
                "general": [
                    "An unknown error has occurred. Please contact an administrator."
                ]
            }
        },
    )
    return add_cors(request, response)
