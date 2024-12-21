# type:ignore
import logfire
from celery import Celery
from celery.signals import beat_init, worker_init

from app.core.config import get_settings

settings = get_settings()

# Logfire documentation: https://logfire.pydantic.dev/docs/integrations/celery/


# https://docs.celeryq.dev/en/latest/userguide/signals.html#worker-init
@worker_init.connect()
def init_worker(*args, **kwargs):  # noqa: ARG001
    logfire.configure(service_name="worker", token=settings.LOGFIRE_TOKEN)
    logfire.instrument_celery()


@beat_init.connect()
def init_beat(*args, **kwargs):  # noqa: ARG001
    logfire.configure(service_name="beat", token=settings.LOGFIRE_TOKEN)
    logfire.instrument_celery()


# Creates a Celery instance
celery_app = Celery(__name__)

# Find config from the settings, using a namespace to limit used settings
# Note that celery expect settings in lowercase
celery_app.config_from_object(obj=settings.model_dump(), namespace="celery")

# Load tasks automatically, in 'tasks' folder.
# Files must be named 'tasks.py' to be imported (note that we could also use
# autodiscover_tasks(..., related_name=None) and import tasks manually in __init__.py)
celery_app.autodiscover_tasks(packages=["app.tasks"])
