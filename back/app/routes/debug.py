from time import sleep
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile

from app.core.auth import get_current_superuser
from app.core.config import Settings, SettingsDep
from app.core.exceptions import ErrorPayload
from app.core.query_pagination import Page, Pagination
from app.models.db_parameters import DBParametersDep
from app.schemas.message import Message
from app.utils.orm import model_to_dict

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get(
    "/settings",
    summary="Read all settings",
    dependencies=[Depends(get_current_superuser)],
    response_model=Settings,
)
def read_settings(settings: SettingsDep):
    return settings


@router.get(
    "/db-parameters",
    summary="Read database parameters",
    response_model=dict[str, Any],
)
def read_db_parameters(db_parameters: DBParametersDep):
    return model_to_dict(db_parameters)


@router.post("/upload")
def create_upload_file(file: UploadFile):
    # TODO: POC with S3 Client on CloudFlare
    # https://stackoverflow.com/questions/70520522/how-to-upload-file-in-fastapi-then-to-amazon-s3-and-finally-process-it
    return {"filename": file.filename, "content_type": file.content_type}


@router.get("/bg-task")
async def some_method_including_a_background_task(
    seconds: int, bg_tasks: BackgroundTasks
) -> Message:  # must be aysnc
    """Demo of built-in BackGroundTasks from FastAPI (Starlette actually)"""

    def long_running_fn(s: int) -> None:  # could be defined outside
        return sleep(s)

    bg_tasks.add_task(long_running_fn, seconds)
    return Message(
        message=f"Did you wait {seconds} seconds before this message is displayed?"
    )


@router.get("/celery-task")
def some_method_with_celery_task_inside() -> str:  # no need to be async
    """Demo of Celery task execution"""

    from app.tasks.tasks import add

    result = add.delay(3, 4)  # type: ignore
    return result.status  # status will be probably be PENDING


@router.get("/schema-includer", response_model=Pagination | Page | ErrorPayload)
def schema_includer() -> None:
    """This is a fake endpoint to force some useful schemas to be included in openAPI"""
    return


@router.get("/div-by-zero")
def div_by_zero():
    """This is a fake endpoint to test uncaugth exception"""

    return {"result": 1 / 0}
