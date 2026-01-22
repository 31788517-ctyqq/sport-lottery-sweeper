#!/usr/bin/env python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# 创建测试目录结构
base_path = BASE_DIR / "frontend" / "src" / "tests"

# 高优先级测试目录
unit_dirs = [
    "unit/components",
    "unit/composables", 
    "unit/utils",
    "unit/store",
    "unit/api"
]

# 创建目录
for dir_path in unit_dirs:
    full_path = base_path / dir_path
    full_path.mkdir(parents=True, exist_ok=True)
    print(f"Created: {full_path}")

# 创建 __init__.py 文件使目录成为 Python 包
for dir_path in unit_dirs:
    init_file = base_path / dir_path / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Test module\n")
        print(f"Created: {init_file}")

print("✅ 测试目录结构创建完成")