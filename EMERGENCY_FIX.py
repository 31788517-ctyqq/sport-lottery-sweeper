#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
紧急修复 - 检查并修复所有问题
"""
import os
import sys

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

print("=" * 70)
print("EMERGENCY FIX - 紧急修复工具")
print("=" * 70)

# 步骤1: 检查后段是否在运行
print("\n[步骤1] 检查后段服务状态...")
import urllib.request
try:
    with urllib.request.urlopen('http://localhost:8000/docs', timeout=3) as response:
        if response.status == 200:
            print("✓ 后端服务正在运行")
        else:
            print(f"⚠ 后端返回状态码: {response.status}")
except:
    print("✗ 后端服务未启动或无法访问")
    print("  请先启动后端: cd backend && python main.py")
    sys.exit(1)

# 步骤2: 测试lottery API
print("\n[步骤2] 测试 /api/v1/lottery/matches API...")
try:
    with urllib.request.urlopen('http://localhost:8000/api/v1/lottery/matches?source=500&page=1&size=10', timeout=5) as response:
        data = response.read().decode('utf-8')
        print(f"状态码: {response.status}")
        if response.status == 200:
            print("✓ API返回200")
            import json
            result = json.loads(data)
            print(f"✓ 成功标志: {result.get('success')}")
            print(f"✓ 数据条数: {len(result.get('data', []))}")
            if result.get('data'):
                print(f"✓ 第一条: {result['data'][0].get('match_id')}")
        else:
            print(f"✗ API错误: {data[:300]}
")
except Exception as e:
    print(f"✗ API测试失败: {e}")

# 步骤3: 检查文件
print("\n[步骤3] 检查数据文件...")
from pathlib import Path
debug_dir = Path("debug")
if debug_dir.exists():
    print(f"✓ debug目录存在: {debug_dir.absolute()}")
    files = list(debug_dir.glob("500_com_matches_*.json"))
    print(f"✓ 找到 {len(files)} 个数据文件")
    if files:
        latest = sorted(files)[-1]
        print(f"✓ 最新文件: {latest.name}")
        print(f"✓ 文件大小: {latest.stat().st_size} 字节")
        
        import json
        with open(latest, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ 包含 {len(data)} 条比赛数据")
else:
    print("✗ debug目录不存在")

# 步骤4: 检查路由注册
print("\n[步骤4] 检查路由注册...")
import subprocess
import time

# 重启后端服务
print("正在重启后端服务...")
print("请在新的终端窗口中运行:")
print("  cd backend")
print("  python main.py")
print("\n然后按Enter继续...")
input()

time.sleep(3)

# 再次测试
print("\n[步骤5] 重新测试API...")
try:
    with urllib.request.urlopen('http://localhost:8000/api/v1/lottery/matches?source=500&page=1&size=10', timeout=10) as response:
        data = response.read().decode('utf-8')
        print(f"状态码: {response.status}")
        if response.status == 200:
            print("✅ SUCCESS! API工作正常！")
            import json
            result = json.loads(data)
            matches = result.get('data', [])
            print(f"获取到 {len(matches)} 条比赛数据")
            
            print("\n数据预览:")
            for i, match in enumerate(matches[:3], 1):
                print(f"  {i}. {match.get('match_id')} - {match.get('home_team')} vs {match.get('away_team')}")
        else:
            print(f"❌ 仍然失败: {data[:300]}")
except Exception as e:
    print(f"❌ 测试失败: {e}")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)
print("\n如果仍然有问题，请:")
print("1. 检查backend/main.py的控制台输出")
print("2. 查看是否有错误堆栈信息")
print("3. 确保所有文件使用UTF-8编码保存")
