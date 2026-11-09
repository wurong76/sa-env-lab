SHELL := /bin/bash
ENV_FILE := .env
PY := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
LOAD_ENV := set -a; [ -f $(ENV_FILE) ] && . ./$(ENV_FILE) || true; set +a;

.PHONY: help prepare gen migrate seed test lint reset serve

help:
	@echo "make prepare   创建 venv、装依赖、生成 .env、建表、写种子数据"
	@echo "make test      跑回归（需要先 make prepare）"
	@echo "make lint      语法检查"
	@echo "make serve     本地起服务（默认端口见 .env 的 APP_PORT）"
	@echo "make reset     删库重建（var/ 整个删除）"

prepare:
	@bash scripts/prepare-env.sh

gen:
	@$(PY) scripts/gen.py

migrate:
	@$(LOAD_ENV) $(PY) scripts/migrate.py

seed:
	@$(LOAD_ENV) $(PY) scripts/seed.py

test:
	@$(LOAD_ENV) $(PY) -m pytest -q

lint:
	@$(PY) -m compileall -q app scripts tests && echo "compile ok"

serve:
	@$(LOAD_ENV) $(PY) -m app.server

reset:
	@rm -rf var
	@$(MAKE) migrate seed
