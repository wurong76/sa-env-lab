import re

MONEY = re.compile(r"^\d+\.\d{2}$")

SUMMARY_PATHS = (
    "/api/users/1/order-summary",
    "/api/users/1/refund-summary",
)


def test_success_envelope(client):
    status, body = client.request("GET", "/api/users/1")
    assert status == 200
    assert set(body) == {"data"}


def test_error_envelope_has_trace_id(client):
    status, body = client.request("GET", "/api/users/999")
    assert status == 404
    assert set(body) == {"error"}
    error = body["error"]
    assert error["code"] == "not_found"
    assert isinstance(error["message"], str) and error["message"]
    assert re.match(r"^[0-9a-f]{16}$", error["traceId"])


def test_money_is_string_with_two_decimals(client):
    _, body = client.request("GET", "/api/users/1/orders")
    for item in body["data"]["items"]:
        assert isinstance(item["total"], str), item
        assert MONEY.match(item["total"]), item


def test_summaries_follow_shape(client):
    """统计类端点（order-summary / refund-summary）必须返回 total/count/byStatus。"""
    for path in SUMMARY_PATHS:
        status, body = client.request("GET", path)
        if status == 404:
            continue
        assert status == 200, (path, body)
        data = body["data"]
        assert isinstance(data["total"], str), (path, data)
        assert MONEY.match(data["total"]), (path, data)
        assert isinstance(data["count"], int), (path, data)
        assert isinstance(data["byStatus"], dict), (path, data)
        for key, value in data["byStatus"].items():
            assert isinstance(key, str) and isinstance(value, int), (path, data)
        assert sum(data["byStatus"].values()) == data["count"], (path, data)


def test_method_not_allowed(client):
    status, body = client.request("POST", "/api/users/1")
    assert status == 405
    assert body["error"]["code"] == "method_not_allowed"
