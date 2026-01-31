#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断lottery API的500错误
"""
import sys
import os

# 设置路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=" * 70)
print("诊断lottery API 500错误")
print("=" * 70)
print(f"项目根目录: {project_root}")
print()

# 测试1: 直接导入并调用load_500_com_data
print("[测试1] 测试load_500_com_data函数...")
try:
    from api.v1.lottery import load_500_com_data
    print("✓ 导入成功")
    
    data = load_500_com_data()
    print(f"✓ 函数执行完成，返回 {len(data)} 条数据")
    
    if data:
        print(f"✓ 第一条数据: {data[0]}")
    else:
        print("⚠ 警告: 没有返回数据（可能是debug文件问题）")
        
except Exception as e:
    print(f"✗ 失败: {e}")
    import traceback
    traceback.print_exc()
    print("\n错误堆栈:")
    traceback.print_exc()

# 测试2: 检查debug文件
print("\n[测试2] 检查debug数据文件...")
try:
    from pathlib import Path
    import json
    
    debug_dir = Path(project_root) / "debug"
    print(f"Debug目录: {debug_dir}")
    print(f"Debug目录存在: {debug_dir.exists()}")
    
    if debug_dir.exists():
        files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
        print(f"找到 {len(files)} 个文件: {files}")
        
        if files:
            latest = sorted(files)[-1]
            file_path = debug_dir / latest
            print(f"读取文件: {file_path}")
            print(f"文件存在: {file_path.exists()}")
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"文件大小: {len(content)} 字节")
                
                # 尝试解析
                data = json.loads(content)
                print(f"✓ JSON解析成功，包含 {len(data)} 条数据")
                
                if data:
                    print(f"✓ 示例: {data[0]}")
            else:
                print("✗ 文件不存在")
        else:
            print("✗ 没有找到500_com_matches_*.json文件")
    else:
        print("✗ debug目录不存在")
        
except Exception as e:
    print(f"✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: 调用get_lottery_matches
print("\n[测试3] 测试get_lottery_matches函数...")
try:
    import asyncio
    from api.v1.lottery import get_lottery_matches
    
    async def test():
        result = await get_lottery_matches(page=1, size=10, source="500")
        return result
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(test())
    loop.close()
    
    print(f"✓ 异步函数执行成功")
    print(f"✓ 返回类型: {type(result)}")
    print(f"✓ 返回数据: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
    
except Exception as e:
    print(f"✗ 失败: {e}")
    print("\n完整错误堆栈:")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)
