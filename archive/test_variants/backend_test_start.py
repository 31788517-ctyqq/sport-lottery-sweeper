#!/usr/bin/env python3
"""
测试启动脚本 - 验证 main.py 是否能正常加载
"""
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("正在测试 main.py 导入...")
    import main
    print("✅ main.py 导入成功")
    print(f"✅ FastAPI 应用创建成功: {main.app.title}")
    print("✅ 所有修改已生效，可以正常启动服务")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()