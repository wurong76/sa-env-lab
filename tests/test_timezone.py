import os

from app.timeutil import business_date


def test_app_tz_is_shanghai():
    assert os.environ.get("APP_TZ") == "Asia/Shanghai", (
        "APP_TZ 必须是 Asia/Shanghai（见 .env.example / AGENTS.md）；"
        "缺 .env 时业务日期会按 UTC 算，统计结果整体偏移一天"
    )


def test_business_date_crosses_midnight_in_shanghai():
    # 2024-06-01T15:30:00Z = 东八区 2024-06-01 23:30（仍是当天）
    assert business_date("2024-06-01T15:30:00Z") == "2024-06-01"


def test_business_date_after_midnight_shanghai():
    # 2024-06-01T16:30:00Z = 东八区 2024-06-02 00:30（跨天）
    assert business_date("2024-06-01T16:30:00Z") == "2024-06-02"


def test_business_date_early_morning_utc():
    # 2024-06-01T01:00:00Z = 东八区 2024-06-01 09:00
    assert business_date("2024-06-01T01:00:00Z") == "2024-06-01"


def test_business_date_late_evening_shanghai():
    # 2024-06-01T16:30:00Z = 东八区 2024-06-02 00:30
    assert business_date("2024-06-01T16:30:00Z") == "2024-06-02"
