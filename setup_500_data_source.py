#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置500万彩票数据源并执行抓取
"""
import sqlite3
import json
import os
import sys

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

def setup_data_source():
    """创建500万彩票数据源"""
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data_sources'")
        if not cursor.fetchone():
            print("❌ data_sources 表不存在")
            return None
        
        # 检查是否已存在
        cursor.execute("SELECT id, name FROM data_sources WHERE name = ?", ('500万彩票',))
        existing = cursor.fetchone()
        
        if existing:
            print(f"✓ 数据源已存在: ID={existing[0]}, 名称={existing[1]}")
            return existing[0]
        
        # 创建数据源
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
        
        cursor.execute("""
            INSERT INTO data_sources (name, type, status, url, config, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            '500万彩票',
            'web',
            1,  # 启用
            'https://trade.500.com/jczq/',
            json.dumps(config, ensure_ascii=False),
            1   # 创建人ID
        ))
        
        conn.commit()
        source_id = cursor.lastrowid
        print(f"✓ 数据源创建成功: ID={source_id}")
        return source_id
        
    except Exception as e:
        print(f"❌ 创建数据源失败: {e}")
        return None
    finally:
        conn.close()

def verify_data():
    """验证数据是否正确"""
    print("\n=== 验证数据 ===")
    
    # 检查debug文件
    debug_dir = os.path.join(project_root, 'debug')
    if os.path.exists(debug_dir):
        files = [f for f in os.listdir(debug_dir) if f.startswith('500_com_matches_') and f.endswith('.json')]
        if files:
            latest = sorted(files)[-1]
            print(f"✓ 找到数据文件: {latest}")
            
            # 读取并显示几条数据
            with open(os.path.join(debug_dir, latest), 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ 数据条数: {len(data)}")
            if data:
                print(f"✓ 示例数据: {data[0].get('match_id')} - {data[0].get('home_team')} vs {data[0].get('away_team')}")
        else:
            print("⚠ 没有找到500彩票网数据文件")
    
    # 测试API
    print("\n=== 测试API ===")
    try:
        import requests
        response = requests.get('http://localhost:8000/api/v1/lottery/matches?source=500&page=1&size=10')
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                matches = result.get('data', [])
                print(f"✓ API返回数据: {len(matches)} 条比赛")
                if matches:
                    print(f"✓ 第一条: ID={matches[0].get('id')}, {matches[0].get('match_id')}")
            else:
                print(f"❌ API返回错误: {result.get('message')}")
        else:
            print(f"❌ API请求失败: {response.status_code}")
    except Exception as e:
        print(f"⚠ 无法测试API (可能后端未启动): {e}")

if __name__ == '__main__':
    print("=" * 50)
    print("设置500万彩票数据源")
    print("=" * 50)
    
    source_id = setup_data_source()
    
    if source_id:
        print(f"\n✓ 数据源设置完成: {source_id}")
        verify_data()
    else:
        print("\n❌ 数据源设置失败")
    
    print("\n" + "=" * 50)
    print("请在前端页面查看效果:")
    print("- 数据源管理: 查看500万彩票数据源")
    print("- 竞彩赛程页面: 查看抓取的比赛数据")
    print("=" * 50)
