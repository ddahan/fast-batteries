from datetime import datetime
from typing import Any
from unittest.mock import patch
from zoneinfo import ZoneInfo

from app.utils.timezone import localtime, make_aware, now

ZONE_INFO_PARIS = ZoneInfo("Europe/Paris")
ZONE_INFO_SYDNEY = ZoneInfo("Australia/Sydney")


@patch("app.core.config.get_settings")
def test_now_ok(mock: Any):
    mock.return_value.TIMEZONE = ZONE_INFO_PARIS
    now_test = now()
    assert isinstance(now_test, datetime)
    assert now_test.tzinfo == ZONE_INFO_PARIS


def test_now_with_specific_timezone_ok():
    now_test = now(ZONE_INFO_SYDNEY)
    assert isinstance(now_test, datetime)
    assert now_test.tzinfo == ZONE_INFO_SYDNEY


@patch("app.core.config.get_settings")
def test_localtime_ok(mock: Any):
    mock.return_value.TIMEZONE = ZONE_INFO_PARIS
    dt = datetime(2024, 12, 25, 18, 00, tzinfo=ZONE_INFO_SYDNEY)
    local_dt = localtime(dt)
    assert local_dt.tzinfo == ZONE_INFO_PARIS
    assert local_dt.hour != dt.hour


@patch("app.core.config.get_settings")
def test_make_aware_ok(mock: Any):
    mock.return_value.TIMEZONE = ZONE_INFO_PARIS
    naive_dt = datetime(2024, 12, 25, 18, 00)
    assert naive_dt.tzinfo is None
    aware_dt = make_aware(naive_dt)
    assert aware_dt.tzinfo == ZONE_INFO_PARIS
