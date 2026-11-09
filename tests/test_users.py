def test_get_user(client):
    status, body = client.request("GET", "/api/users/1")
    assert status == 200
    assert body["data"] == {
        "id": 1,
        "email": "alice@example.com",
        "name": "Alice",
        "createdAt": "2024-01-05T02:00:00Z",
    }


def test_unknown_user_is_404(client):
    status, body = client.request("GET", "/api/users/999")
    assert status == 404
    assert body["error"]["code"] == "not_found"


def test_list_orders_default_pagination(client):
    status, body = client.request("GET", "/api/users/1/orders")
    assert status == 200
    assert body["data"]["limit"] == 20
    assert body["data"]["offset"] == 0
    assert body["data"]["total"] == 3
    assert [item["id"] for item in body["data"]["items"]] == [1, 2, 3]


def test_list_orders_limit_and_offset(client):
    status, body = client.request("GET", "/api/users/1/orders", "limit=1&offset=1")
    assert status == 200
    assert [item["id"] for item in body["data"]["items"]] == [2]


def test_list_orders_rejects_bad_limit(client):
    status, body = client.request("GET", "/api/users/1/orders", "limit=101")
    assert status == 400
    assert body["error"]["code"] == "bad_limit"


def test_list_orders_rejects_negative_offset(client):
    status, body = client.request("GET", "/api/users/1/orders", "offset=-1")
    assert status == 400
    assert body["error"]["code"] == "bad_offset"
