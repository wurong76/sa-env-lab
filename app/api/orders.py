"""订单接口。注意：软删除的退款不出现在订单详情里。"""
from __future__ import annotations

import sqlite3

from app import contract
from app.money import cents_to_yuan


def get_order(conn: sqlite3.Connection, order_id: int) -> dict:
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        raise contract.ApiError("not_found", f"order {order_id} not found", 404)
    refunds = conn.execute(
        "SELECT * FROM refunds WHERE order_id = ? AND deleted_at IS NULL ORDER BY id",
        (order_id,),
    ).fetchall()
    return {
        "id": row["id"],
        "userId": row["user_id"],
        "total": cents_to_yuan(row["total_cents"]),
        "currency": row["currency"],
        "status": row["status"],
        "createdAt": row["created_at"],
        "refunds": [
            {
                "id": refund["id"],
                "amount": cents_to_yuan(refund["amount_cents"]),
                "status": refund["status"],
                "createdAt": refund["created_at"],
            }
            for refund in refunds
        ],
    }
