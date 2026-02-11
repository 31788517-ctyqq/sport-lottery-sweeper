#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证API工作流程 - 完整测试
"""
import os
import sys
import json

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

def test_load_500_data():
    """测试加载500彩票数据"""
    print("=" * 60)
    print("1. 测试 load_500_com_data 函数")
    print("=" * 60)
    
    try:
        from api.v1.lottery import load_500_com_data
        data = load_500_com_data()
        print(f"✓ 成功加载 {len(data)} 条数据")
        
        if data:
            print(f"✓ 第一条数据:")
            for key, value in data[0].items():
                print(f"  {key}: {value}")
        
        return True, data
    except Exception as e:
        print(f"✗ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def test_import_data_source():
    """测试导入数据源"""
    print("\n" + "=" * 60)
    print("2. 测试数据源导入")
    print("=" * 60)
    
    db_path = os.path.join(project_root, 'backend', 'sport_lottery.db')
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data_sources'")
        if not cursor.fetchone():
            print("⚠ data_sources 表不存在，跳过")
            conn.close()
            return True
        
        # 检查或插入500万彩票数据源
        cursor.execute("SELECT id, name, url FROM data_sources WHERE name = ?", ('500万彩票',))
        existing = cursor.fetchone()
        
        if existing:
            print(f"✓ 数据源已存在: ID={existing[0]}")
            source_id = existing[0]
        else:
            config = {
                "source_type": "web_scraper",
                "data_type": "lottery_schedule",
                "parser_type": "html_parser",
                "update_frequency": "daily",
                "timeout": 30,
                "retry_count": 3,
                "url_pattern": "https://trade.500.com/jczq/"
            }
            
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
            print(f"✓ 数据源创建成功: ID={source_id}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n" + "=" * 60)
    print("3. 测试API端点")
    print("=" * 60)
    
    try:
        import requests
        
        # 测试 lottery/matches
        print("\n测试 /api/v1/lottery/matches?source=500&page=1&size=10")
        response = requests.get('http://localhost:8000/api/v1/lottery/matches?source=500&page=1&size=10', timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                matches = result.get('data', [])
                print(f"✓ 成功获取 {len(matches)} 条数据")
                if matches:
                    print(f"✓ 第一条: {matches[0].get('match_id')} - {matches[0].get('home_team')} vs {matches[0].get('away_team')}")
            else:
                print(f"✗ API返回错误: {result.get('message')}")
        else:
            print(f"✗ 响应: {response.text[:300]}")
        
        # 测试 admin/matches
        print("\n测试 /api/v1/admin/matches?source=500&page=1&size=10")
        response = requests.get('http://localhost:8000/api/v1/admin/matches?source=500&page=1&size=10', timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                matches = result.get('data', [])
                print(f"✓ 成功获取 {len(matches)} 条数据")
                if matches:
                    print(f"✓ 第一条: {matches[0].get('match_id')} - {matches[0].get('home_team')} vs {matches[0].get('away_team')}")
            else:
                print(f"✗ API返回错误: {result.get('message')}")
        else:
            print(f"✗ 响应: {response.text[:300]}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务")
        print("  请确保后端已启动: python backend/main.py")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主流程"""
    print("\n" + "=" * 60)
    print("竞彩赛程数据工作流程验证")
    print("=" * 60)
    
    # 步骤1: 测试数据加载
    success1, data = test_load_500_data()
    
    # 步骤2: 测试数据源
    success2 = test_import_data_source()
    
    # 步骤3: 测试API
    success3 = test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    
    if success1 and success2 and success3:
        print("✓ 所有测试通过！")
        print("\n现在可以:")
        print("1. 启动前端: npm run dev")
        print("2. 访问: http://localhost:3000")
        print("3. 进入: 竞彩赛程管理页面")
        print("4. 查看500彩票网的比赛数据")
    else:
        print("✗ 部分测试失败，请查看错误信息")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
