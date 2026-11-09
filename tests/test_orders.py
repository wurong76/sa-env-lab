def test_order_detail(client):
    status, body = client.request("GET", "/api/orders/1")
    assert status == 200
    data = body["data"]
    assert data["id"] == 1
    assert data["total"] == "120.00"
    assert data["status"] == "paid"
    assert [refund["amount"] for refund in data["refunds"]] == ["30.00", "15.00"]


def test_order_detail_hides_soft_deleted_refunds(client):
    """订单 3 有 2 条退款，其中 1 条被软删除，详情里只能看到 1 条。"""
    status, body = client.request("GET", "/api/orders/3")
    assert status == 200
    assert len(body["data"]["refunds"]) == 1
    assert body["data"]["refunds"][0]["amount"] == "99.00"


def test_order_not_found(client):
    status, body = client.request("GET", "/api/orders/404")
    assert status == 404
    assert body["error"]["code"] == "not_found"


def test_refund_list_filters_by_order(client):
    status, body = client.request("GET", "/api/refunds", "order_id=4")
    assert status == 200
    assert [item["amount"] for item in body["data"]["items"]] == ["50.00", "25.00"]


def test_refund_list_excludes_soft_deleted(client):
    status, body = client.request("GET", "/api/refunds")
    assert status == 200
    amounts = [item["amount"] for item in body["data"]["items"]]
    assert "1.00" not in amounts
    assert len(amounts) == 6
