"""分页参数解析：limit 默认 20、范围 1-100；offset 最小 0。"""
from __future__ import annotations

from app import contract


def limit(query: dict[str, list[str]], default: int = 20, maximum: int = 100) -> int:
    raw = query.get("limit", [str(default)])[0]
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise contract.ApiError("bad_limit", "limit must be an integer") from None
    if value < 1 or value > maximum:
        raise contract.ApiError("bad_limit", f"limit must be between 1 and {maximum}")
    return value


def offset(query: dict[str, list[str]]) -> int:
    raw = query.get("offset", ["0"])[0]
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise contract.ApiError("bad_offset", "offset must be an integer") from None
    if value < 0:
        raise contract.ApiError("bad_offset", "offset must be >= 0")
    return value
