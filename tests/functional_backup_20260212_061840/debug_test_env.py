#!/usr/bin/env python3
"""
调试测试环境
"""
import sys
import os

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {current_dir}")

# 检查数据库文件是否存在
db_path = os.path.join(current_dir, "sport_lottery.db")
print(f"Database file exists: {os.path.exists(db_path)}")

# 导入配置查看数据库URL
from backend.config import settings
print(f"Config DATABASE_URL: {settings.DATABASE_URL}")

# 从main导入app并检查
from backend.main import app
print("App imported successfully")

# 检查实际使用的数据库引擎
from backend.database import engine
print(f"Engine URL: {engine.url}")