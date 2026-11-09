#!/usr/bin/env python3
"""从 schema/models.def 生成 app/generated/models.py。不要手改生成结果。"""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema" / "models.def"
OUT = ROOT / "app" / "generated" / "models.py"

HEADER = '''"""GENERATED FILE — 由 scripts/gen.py 从 schema/models.def 生成，请勿手改。

下次执行 `make gen`（或 `make prepare`）会覆盖本文件。
"""
from dataclasses import dataclass
from typing import Optional

'''


def parse() -> dict[str, list[tuple[str, str, str]]]:
    tables: dict[str, list[tuple[str, str, str]]] = {}
    for raw in SCHEMA.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 4:
            raise SystemExit(f"schema 行格式错误: {raw}")
        table, column, sqltype, pytype = parts
        tables.setdefault(table, []).append((column, sqltype, pytype))
    return tables


def class_name(table: str) -> str:
    base = table[:-1] if table.endswith("s") else table
    return "".join(part.capitalize() for part in base.split("_"))


def render(tables: dict[str, list[tuple[str, str, str]]]) -> str:
    chunks = [HEADER]
    for table, columns in tables.items():
        chunks.append("@dataclass\n")
        chunks.append(f"class {class_name(table)}:\n")
        for column, sqltype, pytype in columns:
            if column != "id" and "NOT NULL" not in sqltype:
                chunks.append(f"    {column}: Optional[{pytype}]\n")
            else:
                chunks.append(f"    {column}: {pytype}\n")
        chunks.append("\n\n")
    chunks.append("TABLES = {\n")
    for table, columns in tables.items():
        chunks.append(f"    {table!r}: [\n")
        for column, sqltype, _ in columns:
            chunks.append(f"        ({column!r}, {sqltype!r}),\n")
        chunks.append("    ],\n")
    chunks.append("}\n")
    return "".join(chunks)


def main() -> None:
    tables = parse()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(tables), encoding="utf-8")
    print(f"generated {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
