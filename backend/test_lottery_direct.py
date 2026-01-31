#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接测试lottery API错误
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=" * 70)
print("直接测试lottery API")
print("=" * 70)

# 测试导入
try:
    from api.v1.lottery import load_500_com_data
    print("✓ 成功导入 load_500_com_data")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试函数
try:
    print("\n调用 load_500_com_data()...")
    result = load_500_com_data()
    print(f"✓ 函数返回 {len(result)} 条数据")
    
    if result:
        print(f"✓ 第一条: {result[0]}")
except Exception as e:
    print(f"\n✗ 函数执行失败!")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print("\n完整堆栈跟踪:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("测试完成 - 没有错误!")
print("=" * 70)
