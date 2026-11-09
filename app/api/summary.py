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
