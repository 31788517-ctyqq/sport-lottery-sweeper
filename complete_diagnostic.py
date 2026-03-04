#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
竞彩赛程API完整诊断工具
"""
import os
import sys
import json

# 设置项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'backend'))

print("=" * 70)
print("竞彩赛程API完整诊断工具")
print("=" * 70)
print(f"项目根目录: {project_root}")
print()

# 步骤1: 检查必需文件是否存在
print("[步骤1] 检查必需文件...")
required_files = [
    "backend/api/v1/lottery.py",
    "backend/api/v1/admin_matches.py",
    "backend/api/v1/__init__.py",
]

all_exist = True
for file_path in required_files:
    full_path = os.path.join(project_root, file_path)
    exists = os.path.exists(full_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {file_path}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n✗ 部分文件不存在，请检查！")
    sys.exit(1)

# 步骤2: 检查数据文件
print("\n[步骤2] 检查数据文件...")
debug_dir = os.path.join(project_root, "debug")
if os.path.exists(debug_dir):
    print(f"  ✓ debug目录存在: {debug_dir}")
    
    json_files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_") and f.endswith(".json")]
    if json_files:
        print(f"  ✓ 找到 {len(json_files)} 个数据文件")
        latest = sorted(json_files)[-1]
        print(f"  ✓ 最新文件: {latest}")
        
        # 检查文件内容
        file_path = os.path.join(debug_dir, latest)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  ✓ 文件有效，包含 {len(data)} 条比赛数据")
        except Exception as e:
            print(f"  ✗ 文件格式错误: {e}")
            sys.exit(1)
    else:
        print("  ✗ 没有找到500_com_matches_*.json文件")
        sys.exit(1)
else:
    print("  ✗ debug目录不存在")
    sys.exit(1)

# 步骤3: 测试导入lottery模块
print("\n[步骤3] 测试导入lottery模块...")
try:
    from api.v1.lottery import load_500_com_data, get_lottery_matches
    print("  ✓ 成功导入lottery模块")
except Exception as e:
    print(f"  ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤4: 测试load_500_com_data函数
print("\n[步骤4] 测试load_500_com_data函数...")
try:
    result = load_500_com_data()
    print(f"  ✓ 函数执行成功，返回 {len(result)} 条数据")
    
    if result:
        # 检查数据结构
        first = result[0]
        required_fields = ['id', 'match_id', 'league', 'home_team', 'away_team', 'match_time', 'match_date']
        missing_fields = [f for f in required_fields if f not in first]
        
        if missing_fields:
            print(f"  ✗ 缺少字段: {missing_fields}")
            sys.exit(1)
        
        print(f"  ✓ 数据结构正确")
        print(f"  ✓ 第一条: ID={first['id']}, {first['match_id']}, {first['home_team']} vs {first['away_team']}")
except Exception as e:
    print(f"  ✗ 函数执行失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤5: 测试admin_matches模块
print("\n[步骤5] 测试admin_matches模块...")
try:
    # 检查文件内容
    admin_matches_path = os.path.join(project_root, "backend/api/v1/admin_matches.py")
    with open(admin_matches_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "from .lottery import get_lottery_matches" in content:
        print("  ✓ admin_matches.py正确导入了lottery模块")
    else:
        print("  ✗ admin_matches.py导入语句不正确")
        sys.exit(1)
    
    if "router = APIRouter(prefix=\"/admin/matches\"" in content:
        print("  ✓ admin_matches.py路由前缀正确")
    else:
        print("  ✗ admin_matches.py路由前缀不正确")
        sys.exit(1)
        
except Exception as e:
    print(f"  ✗ 检查失败: {e}")
    sys.exit(1)

# 步骤6: 检查路由注册
print("\n[步骤6] 检查路由注册...")
try:
    init_path = os.path.join(project_root, "backend/api/v1/__init__.py")
    with open(init_path, 'r', encoding='utf-8') as f:
        init_content = f.read()
    
    # 检查lottery路由
    if "from .lottery import router as lottery_router" in init_content:
        print("  ✓ lottery路由已注册")
    else:
        print("  ✗ lottery路由未注册")
        sys.exit(1)
    
    # 检查admin_matches路由
    if "from .admin_matches import router as admin_matches_router" in init_content:
        print("  ✓ admin_matches路由已注册")
    else:
        print("  ✗ admin_matches路由未注册")
        sys.exit(1)
        
    # 检查match_admin是否被禁用
    if "# try:\n#     from .match_admin import router as match_admin_router" in init_content:
        print("  ✓ match_admin路由已禁用（避免冲突）")
    else:
        print("  ⚠ match_admin路由可能未被禁用，可能有冲突")
        
except Exception as e:
    print(f"  ✗ 检查失败: {e}")
    sys.exit(1)

# 步骤7: 检查后端服务
print("\n[步骤7] 检查后端服务...")
import urllib.request
try:
    with urllib.request.urlopen('http://localhost:8000/docs', timeout=5) as response:
        if response.status == 200:
            print("  ✓ 后端服务正在运行")
        else:
            print(f"  ✗ 后端返回状态码: {response.status}")
            print("  请重启后端服务: cd backend && python main.py")
            sys.exit(1)
except Exception as e:
    print(f"  ✗ 无法连接后端: {e}")
    print("  请确保后端已启动: cd backend && python main.py")
    sys.exit(1)

# 步骤8: 测试API端点
print("\n[步骤8] 测试API端点...")
try:
    # 测试lottery API
    print("  测试 /api/v1/lottery/matches...")
    with urllib.request.urlopen('http://localhost:8000/api/v1/lottery/matches?source=500&page=1&size=10', timeout=10) as response:
        data = response.read().decode('utf-8')
        if response.status == 200:
            print(f"    ✓ 返回200，响应长度: {len(data)} 字节")
            result = json.loads(data)
            if result.get('success'):
                matches = result.get('data', [])
                print(f"    ✓ 成功获取 {len(matches)} 条数据")
            else:
                print(f"    ✗ API返回错误: {result.get('message')}")
                sys.exit(1)
        else:
            print(f"    ✗ 返回状态码: {response.status}")
            print(f"    响应: {data[:300]}")
            sys.exit(1)
    
    # 测试admin API
    print("  测试 /api/v1/admin/matches...")
    with urllib.request.urlopen('http://localhost:8000/api/v1/admin/matches?source=500&page=1&size=10', timeout=10) as response:
        data = response.read().decode('utf-8')
        if response.status == 200:
            print(f"    ✓ 返回200，响应长度: {len(data)} 字节")
            result = json.loads(data)
            if result.get('code') == 200:
                matches = result.get('data', [])
                print(f"    ✓ 成功获取 {len(matches)} 条数据")
            else:
                print(f"    ✗ API返回错误: {result.get('message')}")
                sys.exit(1)
        else:
            print(f"    ✗ 返回状态码: {response.status}")
            print(f"    响应: {data[:300]}")
            sys.exit(1)
            
except Exception as e:
    print(f"  ✗ API测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 完成
print("\n" + "=" * 70)
print("✅ 所有测试通过！API工作正常")
print("=" * 70)
print("\n现在可以:")
print("1. 启动前端: npm run dev 或 pnpm dev")
print("2. 访问: http://localhost:3000")
print("3. 进入: 竞彩赛程管理页面")
print("4. 查看500彩票网的10条比赛数据")
print("\n数据源信息:")
print("- 名称: 500万彩票")
print("- URL: https://trade.500.com/jczq/")
print("- 数据条数: 10条")
print("- 示例: 周二01 - 日职联 - 大阪钢巴 vs 浦和红钻")
