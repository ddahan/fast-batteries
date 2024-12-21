from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import DeactivateModel, MyModel, SecretIdModel, TimeStampModel


class ScheduleType(StrEnum):
    INTERVAL = "INTERVAL"
    CRONTAB = "CRONTAB"


class PeriodicTask(SecretIdModel, TimeStampModel, DeactivateModel, MyModel):
    __table_args__ = (
        CheckConstraint(
            "(interval IS NOT NULL AND crontab_expression IS NULL) OR "
            "(interval IS NULL AND crontab_expression IS NOT NULL)",
            name="check_interval_or_crontab_expression",
        ),
    )

    name: Mapped[str] = mapped_column(
        unique=True, index=True, doc="The name of the Celery task to be run."
    )

    task: Mapped[str] = mapped_column(
        doc="The import path of the task to be executed, e.g., 'proj.tasks.import_contacts'."
    )

    interval: Mapped[timedelta | None] = mapped_column(
        doc="The time interval between task executions (optional)."
    )

    crontab_expression: Mapped[str | None] = mapped_column(
        doc="The crontab expression for scheduling tasks, e.g., '0 12 * * *' (optional).",
    )

    @property
    def schedule_type(self) -> ScheduleType:
        if self.interval is not None:
            return ScheduleType.INTERVAL
        if self.crontab_expression is not None:
            return ScheduleType.CRONTAB
        raise ValueError("Invalid schedule type")

    args: Mapped[list[Any]] = mapped_column(
        JSON,
        doc="JSON-encoded positional arguments for the task, e.g., ['arg1', 'arg2'].",
    )

    kwargs: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        doc="JSON-encoded keyword arguments for the task, e.g., {'argument': 'value'}.",
    )

    start_at: Mapped[datetime | None] = mapped_column(
        doc="The datetime when the schedule should begin triggering the task (optional).",
    )
