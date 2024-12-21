from datetime import timedelta

import pytest
import sqlalchemy
from sqlalchemy.orm import Session

from app.models.periodic_task import PeriodicTask, ScheduleType


class TestPeriodicTask:
    def test_periodic_task_can_not_have_same_name(self, session: Session):
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            for _ in range(2):
                PeriodicTask(
                    name="add",
                    task="proj.tasks.add",
                    interval=None,
                    crontab_expression="0 12 * * *",
                    args=[1, 4],
                    kwargs={},
                    start_at=None,
                    is_active=True,
                ).save(session)

    def test_periodic_task_can_not_have_crontab_and_interval_set(self, session: Session):
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            PeriodicTask(
                name="add",
                task="proj.tasks.add",
                interval=timedelta(days=1),
                crontab_expression="0 12 * * *",
                args=[1, 4],
                kwargs={},
                start_at=None,
                is_active=True,
            ).save(session)

    def test_schedule_type(self, session: Session):
        crontab_task = PeriodicTask(
            name="add",
            task="proj.tasks.add",
            interval=None,
            crontab_expression="0 12 * * *",
            args=[1, 4],
            kwargs={},
            start_at=None,
            is_active=True,
        ).save(session)
        assert crontab_task.schedule_type == ScheduleType.CRONTAB

        interval_task = PeriodicTask(
            name="mult",
            task="proj.tasks.mult",
            interval=timedelta(days=1),
            crontab_expression=None,
            args=[],
            kwargs={"left_op": 2, "right_op": 3},
            start_at=None,
            is_active=True,
        ).save(session)
        assert interval_task.schedule_type == ScheduleType.INTERVAL
