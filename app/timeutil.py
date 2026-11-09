"""业务时间：库里存 UTC，业务日期按 APP_TZ（东八区）计算。"""
from __future__ import annotations

import os
from datetime import datetime
from zoneinfo import ZoneInfo


def app_tz() -> ZoneInfo:
    return ZoneInfo(os.environ.get("APP_TZ", "UTC"))


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def business_date(value: str) -> str:
    """把 UTC 时间戳转成业务时区下的日期。"""
    return parse_utc(value).astimezone(app_tz()).date().isoformat()
