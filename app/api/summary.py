"""统计接口。新增统计端点请对齐这里的响应结构：

    {"total": "<两位小数金额字符串>", "count": <整数>, "byStatus": {"<status>": <整数>}}
"""
from __future__ import annotations

import sqlite3

from app.api.users import require_user
from app.money import cents_to_yuan


def order_summary(conn: sqlite3.Connection, user_id: int) -> dict:
    """用户订单汇总：笔数、总金额、按状态分组。"""
    require_user(conn, user_id)
    rows = conn.execute(
        "SELECT status, count(*) AS amount_count, coalesce(sum(total_cents), 0) AS amount_sum "
        "FROM orders WHERE user_id = ? GROUP BY status",
        (user_id,),
    ).fetchall()
    return {
        "total": cents_to_yuan(sum(row["amount_sum"] for row in rows)),
        "count": sum(row["amount_count"] for row in rows),
        "byStatus": {row["status"]: row["amount_count"] for row in rows},
    }


def refund_summary(conn: sqlite3.Connection, user_id: int) -> dict:
    """用户退款汇总：笔数、累计退款金额、按退款状态分组。

    口径：只计入 pending / settled 且未软删除的退款，
    rejected 与软删除的退款不参与金额和笔数统计。
    """
    require_user(conn, user_id)
    rows = conn.execute(
        "SELECT r.status AS status, count(*) AS amount_count, "
        "coalesce(sum(r.amount_cents), 0) AS amount_sum "
        "FROM refunds r JOIN orders o ON o.id = r.order_id "
        "WHERE o.user_id = ? AND r.deleted_at IS NULL AND r.status IN ('pending', 'settled') "
        "GROUP BY r.status",
        (user_id,),
    ).fetchall()
    return {
        "total": cents_to_yuan(sum(row["amount_sum"] for row in rows)),
        "count": sum(row["amount_count"] for row in rows),
        "byStatus": {row["status"]: row["amount_count"] for row in rows},
    }
