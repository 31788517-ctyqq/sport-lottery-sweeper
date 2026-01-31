#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置数据源并加载数据到前端
"""
import sqlite3
import json
import os
import sys

# 设置项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

# 设置数据库路径
db_path = os.path.join(project_root, 'backend', 'sport_lottery.db')

def create_data_source():
    """创建500万彩票数据源"""
    print("正在创建数据源...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查是否已存在
    cursor.execute("SELECT id FROM data_sources WHERE name = ?", ('500万彩票',))
    existing = cursor.fetchone()
    
    if existing:
        print(f"✓ 数据源已存在 (ID: {existing[0]})")
        conn.close()
        return existing[0]
    
    # 配置信息
    config = {
        "source_type": "web_scraper",
        "data_type": "lottery_schedule",
        "parser_type": "html_parser",
        "update_frequency": "daily",
        "timeout": 30,
        "retry_count": 3,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "url_pattern": "https://trade.500.com/jczq/",
        "data_fields": ["match_id", "league", "home_team", "away_team", "match_time", "odds"]
    }
    
    # 插入数据
    cursor.execute("""
        INSERT INTO data_sources (name, type, status, url, config, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        '500万彩票',
        'web',
        1,
        'https://trade.500.com/jczq/',
        json.dumps(config, ensure_ascii=False),
        1
    ))
    
    source_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✓ 数据源创建成功 (ID: {source_id})")
    return source_id

def check_debug_data():
    """检查debug目录中的数据"""
    print("\n=== 检查数据文件 ===")
    
    debug_dir = os.path.join(project_root, 'debug')
    if not os.path.exists(debug_dir):
        print("❌ debug 目录不存在")
        return None
    
    files = [f for f in os.listdir(debug_dir) if f.startswith('500_com_matches_') and f.endswith('.json')]
    if not files:
        print("❌ 没有找到500彩票网数据文件")
        return None
    
    # 获取最新文件
    latest_file = sorted(files)[-1]
    file_path = os.path.join(debug_dir, latest_file)
    
    print(f"✓ 找到数据文件: {latest_file}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ 数据条数: {len(data)}")
    
    if data:
        match = data[0]
        print(f"✓ 示例数据: {match.get('match_id')} - {match.get('home_team')} vs {match.get('away_team')}")
    
    return data

def test_api():
    """测试API是否能返回数据"""
    print("\n=== 测试API ===")
    
    # 检查后端是否运行
    import urllib.request
    import urllib.error
    
    try:
        with urllib.request.urlopen('http://localhost:8000/api/v1/lottery/matches?source=500&page=1&size=10', timeout=5) as response:
            data = json.loads(response.read().decode())
            
        if data.get('success'):
            matches = data.get('data', [])
            print(f"✓ API返回数据: {len(matches)} 条比赛")
            if matches:
                print(f"✓ 第一条: ID={matches[0].get('id')}, match_id={matches[0].get('match_id')}")
                return True
        else:
            print(f"❌ API返回错误: {data.get('message')}")
    except urllib.error.URLError as e:
        print(f"⚠ 无法连接后端API: {e}")
        print("  请确保后端服务已启动: python backend/main.py")
    except Exception as e:
        print(f"⚠ 测试失败: {e}")
    
    return False

if __name__ == '__main__':
    print("=" * 60)
    print("设置500万彩票数据源并验证数据")
    print("=" * 60)
    print(f"数据库: {db_path}")
    print(f"项目根目录: {project_root}")
    print()
    
    # 1. 创建数据源
    source_id = create_data_source()
    
    # 2. 检查数据
    data = check_debug_data()
    
    # 3. 测试API
    api_ok = test_api()
    
    print("\n" + "=" * 60)
    print("操作完成！")
    print("=" * 60)
    
    if source_id and data:
        print("✓ 数据源已创建")
        print("✓ 数据文件已存在")
        if api_ok:
            print("✓ API可正常访问")
        print("\n现在可以访问前端页面查看效果:")
        print("- 数据源管理: 查看500万彩票数据源")
        print("- 竞彩赛程页面: 查看比赛数据")
    else:
        print("❌ 存在问题，请检查:")
        if not source_id:
            print("  - 数据源创建失败")
        if not data:
            print("  - 数据文件不存在（需要运行爬虫）")
        if not api_ok:
            print("  - API无法访问（需要启动后端）")
    
    print("\n如果数据未显示，请:")
    print("1. 确保后端已启动: python backend/main.py")
    print("2. 访问API测试: http://localhost:8000/api/v1/lottery/matches?source=500")
    print("3. 刷新前端页面")
