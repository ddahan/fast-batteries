import time

from app.confcelery import celery_app


@celery_app.task  # type: ignore
def add(a: int, b: int) -> int:
    time.sleep(1)
    return a + b
