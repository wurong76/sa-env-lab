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
    assert body["data"] == {"total": "129.00", "count": 2, "byStatus": {"settled": 2}}


def test_refund_summary_groups_by_status(client):
    # user 2: refund 5(pending 50.00), 6(settled 25.00)
    status, body = client.request("GET", "/api/users/2/refund-summary")
    assert status == 200
    assert body["data"] == {
        "total": "75.00",
        "count": 2,
        "byStatus": {"pending": 1, "settled": 1},
    }


def test_refund_summary_of_user_without_refunds(client):
    from app.db import connect

    conn = connect()
    conn.execute("DELETE FROM refunds WHERE order_id IN (SELECT id FROM orders WHERE user_id = 98)")
    conn.execute("DELETE FROM orders WHERE user_id = 98")
    conn.execute("DELETE FROM users WHERE id = 98")
    conn.execute("INSERT INTO users VALUES (98, 'norefund@example.com', 'NoRefund', '2024-07-01T00:00:00Z')")
    conn.execute(
        "INSERT INTO orders VALUES (98, 98, 5000, 'CNY', 'paid', '2024-07-02T00:00:00Z')"
    )
    conn.commit()
    conn.close()
    status, body = client.request("GET", "/api/users/98/refund-summary")
    assert status == 200
    assert body["data"] == {"total": "0.00", "count": 0, "byStatus": {}}


def test_refund_summary_unknown_user(client):
    status, body = client.request("GET", "/api/users/12345/refund-summary")
    assert status == 404
    assert body["error"]["code"] == "not_found"
