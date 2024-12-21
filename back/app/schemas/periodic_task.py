from datetime import datetime, timedelta
from typing import Any

from pydantic import Field

from app.schemas.base import DeactivateSchemaOptIn, MySchema


class PeriodicTaskIn(DeactivateSchemaOptIn, MySchema):
    name: str
    task: str
    interval: timedelta | None = Field(default=None)
    crontab_expression: str | None = Field(default=None)
    args: list[Any] = Field(default=[])
    kwargs: dict[str, Any] = Field(default={})
    start_at: datetime | None = Field(default=None)

    # NOTE: there is no interval VS crontab_expression integrity check since there is
    # a strong constraint DB that will be checked anyway.
