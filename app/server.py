"""极简 WSGI 服务：路由表 + 统一 envelope。"""
from __future__ import annotations

import json
import os
import re
from typing import Callable
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from app import contract
from app.api import orders, refunds, summary, users
from app.db import connect

Handler = Callable[[object, "re.Match[str]", dict[str, list[str]]], dict]

ROUTES: list[tuple[str, re.Pattern[str], Handler]] = [
    ("GET", re.compile(r"^/api/users/(\d+)$"), lambda conn, m, q: users.get_user(conn, int(m.group(1)))),
    (
        "GET",
        re.compile(r"^/api/users/(\d+)/orders$"),
        lambda conn, m, q: users.list_orders(conn, int(m.group(1)), q),
    ),
    (
        "GET",
        re.compile(r"^/api/users/(\d+)/order-summary$"),
        lambda conn, m, q: summary.order_summary(conn, int(m.group(1))),
    ),
    ("GET", re.compile(r"^/api/orders/(\d+)$"), lambda conn, m, q: orders.get_order(conn, int(m.group(1)))),
    ("GET", re.compile(r"^/api/refunds$"), lambda conn, m, q: refunds.list_refunds(conn, q)),
]

REASONS = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}


def _json(start_response, status: int, payload: dict):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    start_response(
        f"{status} {REASONS.get(status, 'Unknown')}",
        [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(body)))],
    )
    return [body]


def application(environ, start_response):
    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "GET")
    query = parse_qs(environ.get("QUERY_STRING", ""))
    try:
        for route_method, pattern, handler in ROUTES:
            match = pattern.match(path)
            if not match:
                continue
            if route_method != method:
                raise contract.ApiError("method_not_allowed", f"{method} not allowed on {path}", 405)
            conn = connect()
            try:
                payload = contract.ok(handler(conn, match, query))
            finally:
                conn.close()
            return _json(start_response, 200, payload)
        raise contract.ApiError("not_found", f"no route for {path}", 404)
    except contract.ApiError as error:
        return _json(start_response, error.status, contract.fail(error.code, error.message))
    except Exception as error:  # noqa: BLE001
        return _json(start_response, 500, contract.fail("internal_error", str(error)))


app = application


def main() -> None:
    port = int(os.environ.get("APP_PORT", "18080"))
    with make_server("0.0.0.0", port, application) as httpd:
        print(f"serving on http://0.0.0.0:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
