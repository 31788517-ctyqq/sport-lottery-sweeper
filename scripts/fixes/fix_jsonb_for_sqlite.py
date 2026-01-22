#!/usr/bin/env python
"""
临时将 backend/models 下的 JSONB 列转换为 SQLite 兼容的 Text + MutableDict
用法: python fix_jsonb_for_sqlite.py
"""
import os
import re
from pathlib import Path

MODELS_DIR = Path("c:/Users/11581/Downloads/sport-lottery-sweeper/backend/models")

def fix_file(fp: Path):
    with fp.open("r", encoding="utf-8") as f:
        content = f.read()

    # 替换 import
    content = re.sub(
        r"from sqlalchemy\\.dialects\\.postgresql import ([^\n]*JSONB[^\n]*,? ?)",
        lambda m: "from sqlalchemy import Text\nfrom sqlalchemy.ext.mutable import MutableDict" + (", " + m.group(1).replace("JSONB", "").strip(", ") if m.group(1).strip(", ") else ""),
        content
    )
    # 去掉单独的 JSONB import 行
    content = re.sub(r"from sqlalchemy\\.dialects\\.postgresql import JSONB\n?", "", content)

    # 替换 Column(JSONB, ...) 为 Column(MutableDict.as_mutable(Text), ...)
    def replace_col(m):
        params = m.group(1).strip()
        # 默认值为 dict 的要转成 lambda: {}
        params = re.sub(r"default=dict", "default=lambda: {}", params)
        params = re.sub(r"default=list", "default=lambda: []", params)
        return f"Column(MutableDict.as_mutable(Text), {params})"

    content = re.sub(
        r"Column\(JSONB,\s*([^)]+)\)",
        replace_col,
        content
    )

    with fp.open("w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed: {fp}")

for pyfile in MODELS_DIR.rglob("*.py"):
    fix_file(pyfile)

print("All model files processed. JSONB replaced with Text for SQLite compatibility.")
