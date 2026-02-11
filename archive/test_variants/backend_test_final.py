#!/usr/bin/env python3
"""最终测试脚本"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.getcwd())

print("=== 开始测试 ===")
print(f"当前目录: {os.getcwd()}")

try:
    from utils.datetime_compat import patch_datetime
    print("✅ 函数导入成功")
    
    patch_datetime()
    print("✅ patch_datetime执行成功")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("=== 测试结束 ===")