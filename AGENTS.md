# AGENTS.md — 给编码智能体的项目须知

本项目是一个**有状态的服务**：它依赖一个已经建好表、填好种子数据的 SQLite 数据库。
代码本身跑不起来，必须先完成环境准备。

## 环境准备（每次新克隆的仓库第一条命令）

```bash
make prepare
```

它会依次做五件事：

1. 创建 `.venv/` 并安装 `requirements.txt` 里的依赖
2. 从 `.env.example` 复制出 `.env`（**不会覆盖已存在的 .env**）
3. 运行 `make gen` 生成 `app/generated/models.py`
4. 建表（`scripts/migrate.py`）
5. 写入种子数据（`scripts/seed.py`）

跳过这一步，`make test` 会直接报错退出，而不是"部分失败"。

## 跑回归

```bash
make test     # pytest，约 30 个用例
make lint     # 语法编译检查
```

`make test` 用的是 `.venv/bin/python`。系统自带的 `python3` 没有 pytest，
直接用 `python3 -m pytest` 会失败。

## 必须遵守的约定

### 1. `app/generated/` 是生成物，禁止手改

`app/generated/models.py` 由 `scripts/gen.py` 从 `schema/models.def` 生成，
`make gen` / `make prepare` 都会覆盖它。要加字段就改 `schema/models.def` 再 `make gen`。

### 2. 金额一律用整数"分"

- 数据库存储：`*_cents INTEGER`
- 对外输出：两位小数的**字符串**，如 `"129.00"`，由 `app/money.py` 的 `cents_to_yuan()` 转换
- 禁止在 JSON 里输出浮点数金额

### 3. 统计口径（最容易写错的地方）

退款金额统计**只计入 `status IN ('pending','settled')` 且 `deleted_at IS NULL`** 的退款。
`rejected` 的退款和软删除的退款都不计入。

现有 `GET /api/users/{id}/order-summary` 就是照这个套路写的，新增统计端点请对齐它的响应结构：
`{"total": "<金额字符串>", "count": <整数>, "byStatus": {"<status>": <整数>}}`

### 4. `APP_TZ` 必须是 `Asia/Shanghai`

业务日期按东八区计算，不是 UTC。`.env` 缺失或 `APP_TZ` 被改成 `UTC`，
`tests/test_timezone.py` 会失败。不要把测试改成迁就 UTC。

### 5. 错误响应必须带 traceId

所有非 2xx 响应统一是：

```json
{"error": {"code": "not_found", "message": "...", "traceId": "<16位十六进制>"}}
```

用 `app/contract.py` 的 `fail()` / `ApiError` 构造，不要手拼 dict。

### 6. 分页

`limit` 默认 20，范围 1–100，越界返回 `400 bad_limit`；`offset` 最小 0。

## 交付要求

- 改动控制在 `app/`、`tests/`、`docs/`、`schema/` 内；不要动 `scripts/` 里的迁移与种子逻辑（除非任务明确要求）
- PR 描述里写清楚：改了哪些文件、`make test` 的实际输出（通过/失败数量）
- 没有跑过回归就不要声称"测试通过"
