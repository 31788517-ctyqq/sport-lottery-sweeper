#!/usr/bin/env python
"""
在 backend/models 下所有使用 MutableDict 的文件中添加 MutableDict 导入
"""
import os
import re
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / "backend" / "models"

# 需要添加导入的文件列表
FILES_TO_FIX = [
    "venues.py",
    "user.py", 
    "predictions.py",
    "odds.py",
    "match.py",
    "intelligence.py",
    "data_review.py",
    "data.py",
    "admin_user.py"
]

def add_mutable_dict_import(fp: Path):
    with fp.open("r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查是否已经导入了 MutableDict
    if "from sqlalchemy.ext.mutable import MutableDict" in content:
        print(f"✓ {fp.name} - MutableDict already imported")
        return
    
    # 检查是否需要导入（是否有 MutableDict.as_mutable）
    if "MutableDict.as_mutable" not in content:
        return
    
    # 查找合适的导入位置（在最后一个 sqlalchemy 导入之后）
    import_pattern = r"(from sqlalchemy(?!\.ext\.mutable)[^\n]+(?:\n\s+)?(?:[\w\s,]+)?\n)"
    matches = list(re.finditer(import_pattern, content))
    
    if matches:
        last_sqlalchemy_import = matches[-1]
        insert_pos = last_sqlalchemy_import.end()
        # 在最后一个 sqlalchemy 导入后添加 MutableDict 导入
        content = content[:insert_pos] + "from sqlalchemy.ext.mutable import MutableDict\n" + content[insert_pos:]
        print(f"✓ {fp.name} - Added MutableDict import after sqlalchemy imports")
    else:
        # 如果找不到 sqlalchemy 导入，直接在文件开头添加
        lines = content.split('\n')
        # 跳过文档字符串
        insert_line = 0
        for i, line in enumerate(lines):
            if line.startswith('"""') or line.startswith("'''"):
                continue
            if not line.strip():
                insert_line = i + 1
                break
            if line.startswith('from ') or line.startswith('import '):
                insert_line = i + 1
                break
        
        lines.insert(insert_line, "from sqlalchemy.ext.mutable import MutableDict")
        content = '\n'.join(lines)
        print(f"✓ {fp.name} - Added MutableDict import at line {insert_line + 1}")
    
    with fp.open("w", encoding="utf-8") as f:
        f.write(content)

# 处理所有文件
for filename in FILES_TO_FIX:
    fp = MODELS_DIR / filename
    if fp.exists():
        add_mutable_dict_import(fp)
    else:
        print(f"✗ {fp.name} - File not found")

print("\nAll files processed!")
