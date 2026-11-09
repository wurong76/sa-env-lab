import app
import app.server


def test_health(client):
    status, body = client.request("GET", "/api/health")
    assert status == 200
    assert body["data"] == {"status": "ok", "version": app.__version__}


def test_health_does_not_touch_database(client, monkeypatch):
    def fail_connect():
        raise AssertionError("health endpoint must not open the database")

    monkeypatch.setattr(app.server, "connect", fail_connect)
    status, body = client.request("GET", "/api/health")
    assert status == 200
    assert body["data"]["status"] == "ok"


def test_health_rejects_other_methods(client):
    status, body = client.request("POST", "/api/health")
    assert status == 405
    assert body["error"]["code"] == "method_not_allowed"
