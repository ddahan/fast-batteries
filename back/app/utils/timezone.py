from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, NaiveDatetime

from app.core.config import get_settings


def now_utc() -> AwareDatetime:
    """Return an aware datetime.datetime in UTC Timezone"""
    return datetime.now(UTC)


def now(tz: ZoneInfo | None = None) -> AwareDatetime:
    """
    Return an aware datetime.datetime
    Timezone is defined by a setting, unless another time zone is specified.
    """
    return datetime.now(tz or get_settings().TIMEZONE)


def localtime(aware_dt: AwareDatetime, tz: ZoneInfo | None = None) -> AwareDatetime:
    """
    Convert an aware datetime.datetime to local time.
    Only aware datetimes are allowed.
    Timezone is defined by a setting, unless another time zone is specified.
    """

    if aware_dt.tzinfo is None:
        raise ValueError("localtime() cannot be applied to a naive datetime")
    return aware_dt.astimezone(tz or get_settings().TIMEZONE)


def make_aware(naive_dt: NaiveDatetime, tz: ZoneInfo | None = None) -> AwareDatetime:
    """Make a naive datetime.datetime aware, assuming it is in UTC,
    and convert to the provided timezone.
    Timezone is defined by a setting, unless another time zone is specified.
    """
    if naive_dt.tzinfo is not None:
        raise ValueError(f"make_aware expects a naive datetime, got {naive_dt}")

    utc_dt = naive_dt.replace(tzinfo=ZoneInfo("UTC"))
    return utc_dt.astimezone(tz or get_settings().TIMEZONE)
