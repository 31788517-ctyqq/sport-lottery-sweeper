#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API诊断工具 - 在后端目录中运行
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=" * 70)
print("API诊断工具")
print("=" * 70)
print(f"项目根目录: {project_root}")
print(f"当前目录: {os.getcwd()}")
print()

# 测试导入
print("[测试1] 导入lottery模块...")
try:
    from api.v1.lottery import load_500_com_data, get_lottery_matches
    print("✓ 导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试数据加载
print("\n[测试2] 测试load_500_com_data函数...")
try:
    data = load_500_com_data()
    print(f"✓ 加载了 {len(data)} 条数据")
    if data:
        print(f"✓ 第一条: ID={data[0]['id']}, {data[0]['match_id']}")
except Exception as e:
    print(f"✗ 失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试异步函数
print("\n[测试3] 测试get_lottery_matches函数...")
try:
    import asyncio
    
    async def test():
        result = await get_lottery_matches(page=1, size=10, source="500")
        return result
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(test())
    loop.close()
    
    print(f"✓ 函数执行成功")
    print(f"✓ 返回类型: {type(result)}")
    print(f"✓ 包含键: {list(result.keys())}")
    print(f"✓ success: {result.get('success')}")
    print(f"✓ 数据条数: {len(result.get('data', []))}")
    
except Exception as e:
    print(f"✗ 失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ 所有测试通过！")
print("=" * 70)
