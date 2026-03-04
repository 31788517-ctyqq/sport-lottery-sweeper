#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接测试 load_500_com_data 函数
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=" * 70)
print("直接测试 load_500_com_data 函数")
print("=" * 70)
print(f"项目根目录: {project_root}")
print()

# 测试导入
try:
    from pathlib import Path
    print("✓ 导入 pathlib 成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 手动执行函数逻辑
print("\n[步骤1] 计算debug目录路径...")
from pathlib import Path

# 模拟 lottery.py 中的路径计算
api_file = Path(__file__).parent / "api" / "v1" / "lottery.py"
project_root_calc = api_file.parent.parent.parent.parent
debug_dir_calc = project_root_calc / "debug"

print(f"  lottery.py 路径: {api_file}")
print(f"  lottery.py 存在: {api_file.exists()}")
print(f"  计算的项目根目录: {project_root_calc}")
print(f"  计算的debug目录: {debug_dir_calc}")
print(f"  debug目录存在: {debug_dir_calc.exists()}")

# 检查debug目录
if debug_dir_calc.exists():
    print("\n[步骤2] 列出debug目录内容...")
    files = [f for f in os.listdir(debug_dir_calc) if f.startswith("500_com_matches_")]
    print(f"  找到 {len(files)} 个匹配文件: {files}")
    
    if files:
        latest = sorted(files)[-1]
        file_path = debug_dir_calc / latest
        print(f"\n[步骤3] 检查最新文件...")
        print(f"  文件: {file_path}")
        print(f"  文件存在: {file_path.exists()}")
        
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"  文件大小: {file_size} 字节")
            
            # 读取文件
            print(f"\n[步骤4] 读取文件内容...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"  读取成功，内容长度: {len(content)}")
                
                # 解析JSON
                print(f"\n[步骤5] 解析JSON...")
                import json
                data = json.loads(content)
                print(f"  解析成功，包含 {len(data)} 条数据")
                
                if data:
                    print(f"\n[步骤6] 显示第一条数据...")
                    first = data[0]
                    for key, value in first.items():
                        print(f"    {key}: {value}")
                
            except Exception as e:
                print(f"  ✗ 失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  ✗ 文件不存在")
    else:
        print(f"  ✗ 没有找到500_com_matches_*.json文件")
else:
    print(f"  ✗ debug目录不存在")

# 对比项目根目录
print(f"\n[步骤7] 对比项目根目录...")
print(f"  当前计算的根目录: {project_root_calc}")
print(f"  实际的project_root: {project_root}")
print(f"  是否相同: {str(project_root_calc) == str(project_root)}")

# 测试绝对路径
debug_dir_abs = Path(project_root) / "debug"
print(f"  使用绝对路径: {debug_dir_abs}")
print(f"  绝对路径存在: {debug_dir_abs.exists()}")

if debug_dir_abs.exists():
    files_abs = [f for f in os.listdir(debug_dir_abs) if f.startswith("500_com_matches_")]
    print(f"  绝对路径找到 {len(files_abs)} 个文件")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
