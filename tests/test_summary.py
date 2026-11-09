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
