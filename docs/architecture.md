# 架构说明

## 数据模型

三张表，全部由 `schema/models.def` 定义、`make gen` 生成、`make migrate` 建表。

```
users ──< orders ──< refunds
        (1:N)      (1:N)
```

| 表 | 关键字段 | 说明 |
|---|---|---|
| `users` | `id`, `email`, `name` | 一个用户多张订单 |
| `orders` | `user_id`, `total_cents`, `currency`, `status` | `status ∈ {paid, refunded, cancelled}` |
| `refunds` | `order_id`, `amount_cents`, `status`, `deleted_at` | `status ∈ {pending, settled, rejected}` |

## 两条贯穿全项目的约定

### 金额

数据库里一律是**整数分**（`total_cents` / `amount_cents`），任何对外输出都通过
`app/money.py::cents_to_yuan()` 转换成两位小数字符串。原因是浮点金额在 SQL 聚合里
会累积误差，历史上已经出过一次 0.01 的对不平。

### 软删除

退款不做物理删除，只写 `deleted_at`。所有查询退款的 SQL 都必须带 `deleted_at IS NULL`。
订单详情（`app/api/orders.py`）和退款列表（`app/api/refunds.py`）都是这么写的，
新增查询请照做。

## 统计口径（业务规则，必须遵守）

这是财务对过账的口径，不是随手写的：

| 场景 | 是否计入金额 |
|---|---|
| 退款 `status = 'settled'` | ✅ 计入 |
| 退款 `status = 'pending'` | ✅ 计入（已在途，占用额度） |
| 退款 `status = 'rejected'` | ❌ 不计入（申请被驳回，钱没出去） |
| 退款 `deleted_at IS NOT NULL` | ❌ 不计入（软删除，误录） |

统计接口的金额 = `sum(amount_cents)`，笔数 = `count(*)`，分组用 `byStatus`。

现有 `GET /api/users/{id}/order-summary` 就是标准实现，新增统计端点对齐它的返回结构：

```json
{"data": {"total": "264.00", "count": 3, "byStatus": {"paid": 2, "refunded": 1}}}
```

## 时间

库里存 UTC ISO8601（`2024-06-01T01:00:00Z`）。业务日期（对账日、报表日）按
`APP_TZ`（东八区）计算，见 `app/timeutil.py`。跨零点的时间戳在东八区会落到**下一天**，
写统计逻辑时不要直接用 `strftime('%Y-%m-%d')` 切 UTC 字符串。

## 请求链路

```
WSGI application (app/server.py)
  → 路由表匹配
  → 处理函数 (app/api/*.py)
  → app.db.connect() 每次请求一条 SQLite 连接
  → app/contract.ok() / fail() 统一 envelope
```

没有框架、没有 ORM、没有迁移版本表——`make migrate` 用的是 `CREATE TABLE IF NOT EXISTS`，
所以它**不会**修改已存在的表结构。加字段要改 schema 后重建库（`make reset`）。
