from pathlib import Path

import logfire
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.core.config import get_settings
from app.core.exceptions import (
    ProjectAPIException,
    internal_exception_handler,
    project_api_exception_handler,
    validation_exception_handler,
)
from app.utils.introspection import import_package_modules

settings = get_settings()

app = FastAPI(
    title=f"{settings.APP_TITLE} API ({settings.ENVIRONMENT})",
    version=settings.APP_VERSION,
    docs_url=settings.DOCS_URL,
    redirect_slashes=settings.REDIRECT_SLASHES,
    debug=settings.DEBUG,
    # - Order matters when adding handlers.
    # - Native FastAPI handlers (like http_exception_handler) will still be called,
    #  as these custom handlers are added in addition to, not in place of, the default handlers.
    exception_handlers={
        # Errors raised manually in routes
        ProjectAPIException: project_api_exception_handler,
        # Errors raised because of a Pydantic error
        RequestValidationError: validation_exception_handler,
        # Uncaught errors
        Exception: internal_exception_handler,
    },
)

if settings.USE_LOGFIRE:
    logfire.configure(token=settings.LOGFIRE_TOKEN)
    logger.configure(handlers=[logfire.loguru_handler()])
    logfire.instrument_fastapi(app)


# https://github.com/fastapi/fastapi/discussions/8027
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGIN,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Detect and include all routers dynamically from the given module
for module in import_package_modules("app.routes"):
    app.include_router(module.router)


app.mount(
    "/public/",
    StaticFiles(directory=Path(__file__).resolve().parent.parent / "public"),
    name="public",
)
