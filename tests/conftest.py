import io
import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.server import application  # noqa: E402


class Client:
    """直接调用 WSGI app，不起网络端口。"""

    def request(self, method: str, path: str, query: str = ""):
        captured = {}

        def start_response(status, headers):
            captured["status"] = int(status.split()[0])
            captured["headers"] = dict(headers)

        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "QUERY_STRING": query,
            "SERVER_NAME": "test",
            "SERVER_PORT": "80",
            "wsgi.url_scheme": "http",
            "wsgi.input": io.BytesIO(b""),
            "CONTENT_LENGTH": "0",
        }
        body = b"".join(application(environ, start_response))
        return captured["status"], json.loads(body.decode("utf-8") or "{}")


@pytest.fixture(scope="session", autouse=True)
def require_prepared_env():
    path = os.environ.get("APP_DB", "var/app.db")
    if not os.path.exists(path):
        pytest.exit(
            f"数据库 {path} 不存在：请先执行 make prepare（创建 venv、.env、建表、种子数据）",
            returncode=2,
        )
    conn = sqlite3.connect(path)
    existing = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    missing = {"users", "orders", "refunds"} - existing
    if missing:
        pytest.exit(f"缺少表 {sorted(missing)}：请先执行 make migrate && make seed", returncode=2)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def conn():
    from app.db import connect

    connection = connect()
    yield connection
    connection.close()
