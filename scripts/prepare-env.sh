#!/usr/bin/env bash
# 环境准备：新克隆的仓库跑这一个脚本即可。幂等，可重复执行。
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/5] 创建虚拟环境"
python3 -m venv .venv

echo "[2/5] 安装依赖"
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -r requirements.txt

echo "[3/5] 准备 .env"
if [ -f .env ]; then
  echo "      已存在 .env，保留不动"
else
  cp .env.example .env
  echo "      已从 .env.example 复制"
fi

echo "[4/5] 生成代码 + 建表"
set -a; . ./.env; set +a
.venv/bin/python scripts/gen.py
.venv/bin/python scripts/migrate.py

echo "[5/5] 写入种子数据"
.venv/bin/python scripts/seed.py

echo "prepare ok"
