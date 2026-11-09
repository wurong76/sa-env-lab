"""退款列表接口。"""
from __future__ import annotations

import sqlite3

from app import contract
from app.money import cents_to_yuan


def list_refunds(conn: sqlite3.Connection, query: dict[str, list[str]]) -> dict:
    raw = query.get("order_id", [None])[0]
    params: tuple = ()
    where = "WHERE deleted_at IS NULL"
    if raw is not None:
        try:
            order_id = int(raw)
        except ValueError:
            raise contract.ApiError("bad_order_id", "order_id must be an integer") from None
        where += " AND order_id = ?"
        params = (order_id,)
    rows = conn.execute(f"SELECT * FROM refunds {where} ORDER BY id", params).fetchall()
    return {
        "items": [
            {
                "id": row["id"],
                "orderId": row["order_id"],
                "amount": cents_to_yuan(row["amount_cents"]),
                "status": row["status"],
                "reason": row["reason"],
                "createdAt": row["created_at"],
            }
            for row in rows
        ]
    }
