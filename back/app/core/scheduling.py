from celery import beat  # type: ignore
from celery.schedules import crontab, schedule  # type: ignore
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import engine
from app.models.periodic_task import PeriodicTask, ScheduleType


class MyDatabaseScheduler(beat.Scheduler):
    def setup_schedule(self) -> None:
        """Load periodic tasks from the database and populate Celery's schedule."""

        with Session(engine) as session:
            stmt = select(PeriodicTask).where(PeriodicTask.is_active)
            tasks = session.execute(stmt).scalars().all()
            for task in tasks:
                self.schedule[task.name] = self.create_schedule_entry(task)  # type: ignore

    def create_schedule_entry(self, task: PeriodicTask) -> beat.ScheduleEntry:
        """Convert a `PeriodicTask` instance into a Celery schedule entry."""

        if task.schedule_type == ScheduleType.INTERVAL:
            celery_schedule = schedule(run_every=task.interval)
        elif task.schedule_type == ScheduleType.CRONTAB:
            parts = task.crontab_expression.split()  # type: ignore
            celery_schedule = crontab(
                minute=parts[0],
                hour=parts[1],
                day_of_month=parts[2],
                month_of_year=parts[3],
                day_of_week=parts[4],
            )
        else:
            raise ValueError(f"Invalid schedule type for task: {task.name}")

        return beat.ScheduleEntry(
            name=task.name,
            task=task.task,
            schedule=celery_schedule,
            args=task.args,
            kwargs=task.kwargs,
            options={"expires": task.start_at},
        )
