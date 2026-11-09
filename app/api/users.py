"""用户相关接口。"""
from __future__ import annotations

import sqlite3

from app import contract, paging
from app.money import cents_to_yuan


def require_user(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise contract.ApiError("not_found", f"user {user_id} not found", 404)
    return row


def get_user(conn: sqlite3.Connection, user_id: int) -> dict:
    row = require_user(conn, user_id)
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"],
        "createdAt": row["created_at"],
    }


def list_orders(conn: sqlite3.Connection, user_id: int, query: dict[str, list[str]]) -> dict:
    require_user(conn, user_id)
    limit = paging.limit(query)
    offset = paging.offset(query)
    rows = conn.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id LIMIT ? OFFSET ?",
        (user_id, limit, offset),
    ).fetchall()
    total = conn.execute("SELECT count(*) FROM orders WHERE user_id = ?", (user_id,)).fetchone()[0]
    return {
        "items": [
            {
                "id": row["id"],
                "total": cents_to_yuan(row["total_cents"]),
                "currency": row["currency"],
                "status": row["status"],
                "createdAt": row["created_at"],
            }
            for row in rows
        ],
        "limit": limit,
        "offset": offset,
        "total": total,
    }
