def _delete_user_with_data(conn, user_id: int) -> None:
    conn.execute("DELETE FROM refunds WHERE order_id IN (SELECT id FROM orders WHERE user_id = ?)", (user_id,))
    conn.execute("DELETE FROM orders WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))


def test_order_summary_total_and_count(client):
    status, body = client.request("GET", "/api/users/1/order-summary")
    assert status == 200
    data = body["data"]
    assert data["count"] == 3
    assert data["total"] == "264.00"
    assert data["byStatus"] == {"paid": 2, "refunded": 1}


def test_order_summary_of_user_without_orders(client):
    from app.db import connect

    conn = connect()
    conn.execute("DELETE FROM users WHERE id = 99")
    conn.execute("INSERT INTO users VALUES (99, 'new@example.com', 'New', '2024-07-01T00:00:00Z')")
    conn.commit()
    conn.close()
    status, body = client.request("GET", "/api/users/99/order-summary")
    assert status == 200
    assert body["data"] == {"total": "0.00", "count": 0, "byStatus": {}}


def test_order_summary_unknown_user(client):
    status, body = client.request("GET", "/api/users/12345/order-summary")
    assert status == 404


def test_refund_summary_excludes_rejected_and_soft_deleted(client):
    # user 1: refunds 1(settled 30.00), 2(rejected), 3(settled 99.00), 4(settled 1.00, 软删除)
    status, body = client.request("GET", "/api/users/1/refund-summary")
    assert status == 200
    assert body["data"] == {
        "total": "129.00",
        "count": 2,
        "refundedOrderCount": 2,
        "byStatus": {"settled": 2},
    }


def test_refund_summary_groups_by_status(client):
    # user 2: 订单 4 同时有 refund 5(pending 50.00) 与 6(settled 25.00)，订单数按去重计
    status, body = client.request("GET", "/api/users/2/refund-summary")
    assert status == 200
    assert body["data"] == {
        "total": "75.00",
        "count": 2,
        "refundedOrderCount": 1,
        "byStatus": {"pending": 1, "settled": 1},
    }


def test_refund_summary_ignores_rejected_only_orders(client):
    from app.db import connect

    conn = connect()
    _delete_user_with_data(conn, 97)
    conn.execute("INSERT INTO users VALUES (97, 'rejected@example.com', 'Rejected', '2024-07-01T00:00:00Z')")
    conn.execute(
        "INSERT INTO orders VALUES (97, 97, 5000, 'CNY', 'paid', '2024-07-02T00:00:00Z')"
    )
    conn.execute(
        "INSERT INTO refunds VALUES (97, 97, 5000, 'rejected', '超出售后期', NULL, '2024-07-03T00:00:00Z')"
    )
    conn.commit()
    conn.close()
    try:
        status, body = client.request("GET", "/api/users/97/refund-summary")
        assert status == 200
        assert body["data"] == {
            "total": "0.00",
            "count": 0,
            "refundedOrderCount": 0,
            "byStatus": {},
        }
    finally:
        conn = connect()
        _delete_user_with_data(conn, 97)
        conn.commit()
        conn.close()


def test_refund_summary_of_user_without_refunds(client):
    from app.db import connect

    conn = connect()
    _delete_user_with_data(conn, 98)
    conn.execute("INSERT INTO users VALUES (98, 'norefund@example.com', 'NoRefund', '2024-07-01T00:00:00Z')")
    conn.execute(
        "INSERT INTO orders VALUES (98, 98, 5000, 'CNY', 'paid', '2024-07-02T00:00:00Z')"
    )
    conn.commit()
    conn.close()
    try:
        status, body = client.request("GET", "/api/users/98/refund-summary")
        assert status == 200
        assert body["data"] == {
            "total": "0.00",
            "count": 0,
            "refundedOrderCount": 0,
            "byStatus": {},
        }
    finally:
        conn = connect()
        _delete_user_with_data(conn, 98)
        conn.commit()
        conn.close()


def test_refund_summary_unknown_user(client):
    status, body = client.request("GET", "/api/users/12345/refund-summary")
    assert status == 404
    assert body["error"]["code"] == "not_found"
