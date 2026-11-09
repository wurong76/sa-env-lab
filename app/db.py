"""SQLite 连接。数据库路径来自环境变量 APP_DB（见 .env.example）。"""
from __future__ import annotations

import os
import pathlib
import sqlite3


def db_path() -> str:
    return os.environ.get("APP_DB", "var/app.db")


def connect() -> sqlite3.Connection:
    path = db_path()
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
