#!/usr/bin/env python3
"""建表。DDL 来自 app/generated/models.py（由 make gen 生成）。幂等。"""
from __future__ import annotations

import os
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.generated.models import TABLES  # noqa: E402

INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_refunds_order ON refunds(order_id)",
)


def main() -> None:
    path = os.environ.get("APP_DB", "var/app.db")
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    for table, columns in TABLES.items():
        ddl = ", ".join(f"{name} {sqltype}" for name, sqltype in columns)
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({ddl})")
    for statement in INDEXES:
        conn.execute(statement)
    conn.commit()
    conn.close()
    print(f"migrated {path}")


if __name__ == "__main__":
    main()
