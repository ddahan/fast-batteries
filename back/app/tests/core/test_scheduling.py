from datetime import timedelta

import pytest
from celery import Celery  # type: ignore
from celery.schedules import crontab, schedule  # type: ignore
from sqlalchemy.orm import Session

from app.core.scheduling import MyDatabaseScheduler
from app.models.periodic_task import PeriodicTask
from app.schemas.periodic_task import PeriodicTaskIn


@pytest.fixture
def celery_app() -> Celery:
    """
    Provides a minimal Celery app instance for testing.
    """
    app = Celery("test_app")
    return app


def test_my_database_scheduler(celery_app: Celery, session: Session):
    """
    Test the `setup_schedule` method to ensure periodic tasks are loaded into Celery's schedule.
    """
    # Create some test periodic tasks in the database
    task1_in = PeriodicTaskIn(
        name="task1",
        task="app.tasks.example_task1",
        interval=timedelta(days=1),
    )
    task2_in = PeriodicTaskIn(
        name="task2",
        task="app.tasks.example_task2",
        crontab_expression="0 12 * * *",
        args=["arg1"],
        kwargs={"age": 13},
    )
    task1 = PeriodicTask(**task1_in.model_dump())
    task2 = PeriodicTask(**task2_in.model_dump())
    session.add_all([task1, task2])
    session.commit()

    scheduler = MyDatabaseScheduler(app=celery_app)

    # Call the setup_schedule method
    scheduler.setup_schedule()
    assert (
        scheduler.schedule and len(scheduler.schedule) == 2
    ), "Scheduler should contain 2 tasks."

    # Verify task1 schedule
    entry1 = scheduler.schedule["task1"]
    assert isinstance(entry1.schedule, schedule)
    assert entry1.schedule.run_every == timedelta(days=1)

    # Verify task2 schedule
    entry2 = scheduler.schedule["task2"]
    assert isinstance(entry2.schedule, crontab)
    assert entry2.args == ["arg1"]
    assert entry2.kwargs == {"age": 13}
    assert entry2.schedule.minute == {0}
    assert entry2.schedule.hour == {12}
