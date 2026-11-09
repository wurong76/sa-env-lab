# API 约定

## 响应结构

成功：

```json
{"data": {...}}
```

失败（所有非 2xx）：

```json
{"error": {"code": "not_found", "message": "user 999 not found", "traceId": "a1b2c3d4e5f60718"}}
```

`traceId` 由 `app/contract.py` 生成，测试会校验它存在且是 16 位十六进制。

## 错误码

| code | HTTP | 场景 |
|---|---|---|
| `not_found` | 404 | 资源不存在 |
| `bad_limit` | 400 | limit 非整数或超出 1–100 |
| `bad_offset` | 400 | offset 非整数或为负 |
| `bad_order_id` | 400 | order_id 非整数 |
| `method_not_allowed` | 405 | 方法不匹配 |

## 字段命名

- JSON 用 camelCase（`userId`、`createdAt`、`orderId`）
- 金额字段用 `total` / `amount`，值是**字符串**，两位小数
- 数据库列用 snake_case（`user_id`、`created_at`）

## 分页

`?limit=&offset=`，`limit` 默认 20、上限 100。列表返回里带 `limit` / `offset` / `total`。

## 统计端点

形如 `/api/users/{id}/xxx-summary`，返回：

```json
{"data": {"total": "129.00", "count": 2, "byStatus": {"settled": 2}}}
```

- `total`：金额字符串
- `currency`：币种，仅退款汇总端点返回，取自环境变量 `APP_CURRENCY`（默认 `CNY`）
- `count`：参与统计的条数
- `byStatus`：status → 条数，**必须满足 `sum(byStatus.values()) == count`**
- `refundedOrderCount`：仅退款汇总端点返回，发生过退款的订单数（按订单去重，统计口径与 `total` / `count` 一致）

## 现有端点

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/users/{id}` | 用户详情 |
| GET | `/api/users/{id}/orders` | 用户订单列表（分页） |
| GET | `/api/users/{id}/order-summary` | 用户订单汇总 |
| GET | `/api/users/{id}/refund-summary` | 用户退款汇总（口径见 `docs/architecture.md`） |
| GET | `/api/orders/{id}` | 订单详情（含退款，已过滤软删除） |
| GET | `/api/refunds?order_id=` | 退款列表 |
