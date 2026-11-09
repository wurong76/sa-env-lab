# sa-env-lab

一个最小的订单/退款服务，刻意保留了真实项目里的环境依赖与业务约定，用来验证
"智能体能否自己把环境拉起来并跑通回归"。

## 快速开始

```bash
make prepare   # 建 venv、装依赖、生成 .env、建表、写种子数据
make test      # 跑回归
make serve     # 起服务，默认 http://127.0.0.1:18080
```

## 目录

```
schema/models.def        数据模型定义（生成器的输入）
scripts/gen.py           生成 app/generated/models.py
scripts/migrate.py       建表
scripts/seed.py          种子数据
app/api/*.py             接口实现
app/generated/models.py  生成物，禁止手改
docs/                    架构与 API 约定（统计口径在这里）
tests/                   回归用例
```

## 已有数据

3 个用户、6 张订单、7 条退款（其中 1 条 `rejected`、1 条软删除），
具体见 `scripts/seed.py`。
