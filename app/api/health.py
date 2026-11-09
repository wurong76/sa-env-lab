"""健康检查接口：只读，不依赖数据库与鉴权。"""
from __future__ import annotations

from app import __version__


def health() -> dict:
    return {"status": "ok", "version": __version__}
