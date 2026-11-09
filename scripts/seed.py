#!/usr/bin/env python3
"""写入种子数据。幂等：先清空再插入，id 固定。"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.db import connect  # noqa: E402

USERS = [
    (1, "alice@example.com", "Alice", "2024-01-05T02:00:00Z"),
    (2, "bob@example.com", "Bob", "2024-02-11T09:30:00Z"),
    (3, "carol@example.com", "Carol", "2024-03-20T16:45:00Z"),
]

# id, user_id, total_cents, currency, status, created_at
ORDERS = [
    (1, 1, 12000, "CNY", "paid", "2024-06-01T01:00:00Z"),
    (2, 1, 4500, "CNY", "paid", "2024-06-03T07:20:00Z"),
    (3, 1, 9900, "CNY", "refunded", "2024-06-05T12:00:00Z"),
    (4, 2, 20000, "CNY", "paid", "2024-06-08T03:10:00Z"),
    (5, 2, 1000, "CNY", "cancelled", "2024-06-09T11:00:00Z"),
    (6, 3, 7777, "CNY", "paid", "2024-06-12T15:30:00Z"),
]

# id, order_id, amount_cents, status, reason, deleted_at, created_at
REFUNDS = [
    (1, 1, 3000, "settled", "商品破损", None, "2024-06-02T02:00:00Z"),
    (2, 1, 1500, "rejected", "超出售后期", None, "2024-06-02T04:00:00Z"),
    (3, 3, 9900, "settled", "整单退款", None, "2024-06-06T01:00:00Z"),
    (4, 3, 100, "settled", "运费差额", "2024-06-07T00:00:00Z", "2024-06-06T02:00:00Z"),
    (5, 4, 5000, "pending", "部分退款申请", None, "2024-06-09T05:00:00Z"),
    (6, 4, 2500, "settled", "少发一件", None, "2024-06-10T06:00:00Z"),
    (7, 6, 777, "settled", "包装破损", None, "2024-06-13T08:00:00Z"),
]


def main() -> None:
    conn = connect()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("DELETE FROM refunds")
    conn.execute("DELETE FROM orders")
    conn.execute("DELETE FROM users")
    conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", USERS)
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", ORDERS)
    conn.executemany("INSERT INTO refunds VALUES (?, ?, ?, ?, ?, ?, ?)", REFUNDS)
    conn.commit()
    counts = {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in ("users", "orders", "refunds")}
    conn.close()
    print(f"seeded {counts}")


if __name__ == "__main__":
    main()
