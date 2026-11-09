"""响应约定：成功 {"data": ...}，失败 {"error": {code, message, traceId}}。"""
from __future__ import annotations

import uuid
from typing import Any


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


def trace_id() -> str:
    return uuid.uuid4().hex[:16]


def ok(data: Any) -> dict[str, Any]:
    return {"data": data}


def fail(code: str, message: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "traceId": trace_id()}}
