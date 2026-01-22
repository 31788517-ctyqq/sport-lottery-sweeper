#!/usr/bin/env python
"""
修复 SQLite 不支持 ARRAY 类型的问题
将 PostgreSQL ARRAY 类型替换为 SQLite 兼容的 JSON 存储方式
"""
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "backend" / "models"

# 需要修复的文件和对应的 ARRAY 字段
ARRAY_FIXES = {
    "venues.py": [
        ("image_urls = Column(ARRAY(String), default=list, nullable=False)", 
         "image_urls = Column(JSON, default=list, nullable=False)  # 图片URL数组，SQLite JSON存储"),
        ("facilities = Column(ARRAY(String), default=list, nullable=False)", 
         "facilities = Column(JSON, default=list, nullable=False)  # 设施列表，SQLite JSON存储")
    ],
    "user.py": [
        # user.py 中的 ARRAY 导入需要保留，但实际使用的地方需要替换
    ],
    "predictions.py": [
        # predictions.py 中的 ARRAY 导入需要保留，但实际使用的地方需要替换
    ],
    "odds.py": [
        ("supported_markets = Column(ARRAY(String), default=list, nullable=False)",
         "supported_markets = Column(JSON, default=list, nullable=False)  # 支持的市场，SQLite JSON存储"),
        ("supported_odds_types = Column(ARRAY(String), default=list, nullable=False)",
         "supported_odds_types = Column(JSON, default=list, nullable=False)  # 支持的赔率类型，SQLite JSON存储")
    ],
    "match.py": [
        # match.py 中的 ARRAY 导入需要保留，但实际使用的地方需要替换
    ],
    "intelligence.py": [
        ("keywords = Column(ARRAY(String\(50\)), default=\[\], nullable=False, index=True)",
         "keywords = Column(JSON, default=[], nullable=False, index=False)  # 关键词，SQLite JSON存储"),
        ("tags = Column(ARRAY(String\(50\)), default=\[\], nullable=False, index=True)",
         "tags = Column(JSON, default=[], nullable=False, index=False)  # 标签，SQLite JSON存储"),
        ("images = Column(ARRAY(String\(500\)), default=\[\], nullable=False)",
         "images = Column(JSON, default=[], nullable=False)  # 图片URL，SQLite JSON存储")
    ],
    "data_review.py": [
        # data_review.py 中的 ARRAY 导入需要保留，但实际使用的地方需要替换
    ],
    "admin_user.py": [
        ("login_allowed_ips = Column\(ARRAY\(String\), nullable=True\)",
         "login_allowed_ips = Column(JSON, nullable=True)  # 允许登录的IP白名单，SQLite JSON存储")
    ]
}

def fix_array_fields(file_path):
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()
    
    original_content = content
    filename = file_path.name
    
    if filename in ARRAY_FIXES:
        for old_pattern, new_text in ARRAY_FIXES[filename]:
            # 使用更灵活的正则匹配
            pattern = old_pattern.replace("(", "\\(").replace(")", "\\)")
            content = re.sub(pattern, new_text, content)
    
    # 特殊处理：移除 ARRAY 导入但保留其他 postgresql 导入
    if "from sqlalchemy.dialects.postgresql import" in content:
        # 将 "from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY" 
        # 替换为 "from sqlalchemy.dialects.postgresql import UUID, JSONB"
        content = re.sub(
            r"from sqlalchemy\.dialects\.postgresql import ([^\n]*), ARRAY([^\n]*)",
            r"from sqlalchemy.dialects.postgresql import \1\2",
            content
        )
        # 如果没有其他 postgresql 导入了，就删除整行
        content = re.sub(
            r"from sqlalchemy\.dialects\.postgresql import\s*\n",
            "",
            content
        )
    
    # 添加 JSON 导入（如果还没有的话）
    if "from sqlalchemy import" in content and "JSON" not in content:
        # 在 SQLAlchemy 导入中添加 JSON
        content = re.sub(
            r"(from sqlalchemy import \([^\)]*)([,\s]*)(\n?\))",
            lambda m: m.group(1) + ", JSON" + m.group(2) + m.group(3),
            content,
            flags=re.DOTALL
        )
    
    if content != original_content:
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ {filename} - Fixed ARRAY fields and imports")
        return True
    else:
        print(f"○ {filename} - No changes needed")
        return False

# 处理所有文件
for filename in ARRAY_FIXES.keys():
    fp = MODELS_DIR / filename
    if fp.exists():
        fix_array_fields(fp)
    else:
        print(f"✗ {filename} - File not found")

print("\nArray fixes completed!")
