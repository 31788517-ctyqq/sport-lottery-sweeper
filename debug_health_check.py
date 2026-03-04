#!/usr/bin/env python3
"""
调试健康检查API和100qiu数据获取问题
"""
import requests
import json
import sys
import sqlite3
from datetime import datetime

def test_backend_connection():
    """测试后端连接"""
    print("=" * 60)
    print("测试后端连接")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:8000/api/v1/health', timeout=5)
        print(f"后端健康检查响应: {response.status_code}")
        print(f"响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            print(f"解析后的JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"无法连接到后端: {e}")
        return False

def test_data_source_health():
    """测试数据源健康检查API"""
    print("\n" + "=" * 60)
    print("测试数据源健康检查API")
    print("=" * 60)
    
    # 从数据库获取一个数据源ID
    try:
        conn = sqlite3.connect('data/sport_lottery.db')
        cursor = conn.cursor()
        
        # 先尝试获取100qiu数据源
        cursor.execute("""
            SELECT id, name, type 
            FROM data_sources 
            WHERE type = '100qiu' OR 
                  (config LIKE '%100qiu%' OR config LIKE '%source_type%')
            LIMIT 1
        """)
        row = cursor.fetchone()
        
        if not row:
            # 获取任何数据源
            cursor.execute("SELECT id, name, type FROM data_sources LIMIT 1")
            row = cursor.fetchone()
            
        if row:
            source_id, source_name, source_type = row
            print(f"找到数据源: ID={source_id}, 名称={source_name}, 类型={source_type}")
            
            # 测试健康检查API
            print(f"\n测试健康检查API: POST /api/v1/admin/sources/{source_id}/health")
            try:
                response = requests.post(
                    f'http://localhost:8000/api/v1/admin/sources/{source_id}/health',
                    timeout=10
                )
                print(f"响应状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"解析后的JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    # 检查返回格式
                    if data.get('success'):
                        print("✓ API返回success: true")
                        if 'data' in data:
                            health_data = data['data']
                            print(f"健康检查数据: {health_data}")
                            if 'message' in health_data:
                                print(f"✓ message字段存在: {health_data['message']}")
                            else:
                                print("✗ message字段缺失")
                        else:
                            print("✗ data字段缺失")
                    else:
                        print("✗ API返回success: false")
                        print(f"错误信息: {data.get('message', '无message字段')}")
                else:
                    print(f"✗ API返回非200状态码: {response.status_code}")
                    
            except Exception as e:
                print(f"调用API失败: {e}")
                
        else:
            print("数据库中未找到数据源")
            
        conn.close()
        
    except Exception as e:
        print(f"数据库操作失败: {e}")

def test_100qiu_fetch():
    """测试100qiu数据获取API"""
    print("\n" + "=" * 60)
    print("测试100qiu数据获取API")
    print("=" * 60)
    
    # 从数据库获取一个100qiu数据源ID
    try:
        conn = sqlite3.connect('data/sport_lottery.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, type, config
            FROM data_sources 
            WHERE type = '100qiu' OR 
                  (config LIKE '%100qiu%' OR config LIKE '%source_type%')
            LIMIT 1
        """)
        row = cursor.fetchone()
        
        if row:
            source_id, source_name, source_type, config_str = row
            print(f"找到100qiu数据源: ID={source_id}, 名称={source_name}, 类型={source_type}")
            print(f"配置: {config_str}")
            
            # 测试获取API
            print(f"\n测试获取API: POST /api/v1/data-source-100qiu/{source_id}/fetch")
            try:
                response = requests.post(
                    f'http://localhost:8000/api/v1/data-source-100qiu/{source_id}/fetch',
                    timeout=30
                )
                print(f"响应状态码: {response.status_code}")
                print(f"响应内容: {response.text[:1000]}...")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"解析后的JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    if data.get('success'):
                        print(f"✓ 获取成功: {data.get('message', '无消息')}")
                        print(f"获取数量: {data.get('total_fetched', 0)}")
                    else:
                        print(f"✗ 获取失败: {data.get('message', '无消息')}")
                        
                else:
                    print(f"✗ API返回非200状态码: {response.status_code}")
                    
            except Exception as e:
                print(f"调用API失败: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print("数据库中未找到100qiu数据源")
            
        conn.close()
        
    except Exception as e:
        print(f"数据库操作失败: {e}")
        import traceback
        traceback.print_exc()

def check_database_schema():
    """检查数据库表结构"""
    print("\n" + "=" * 60)
    print("检查数据库表结构")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('data/sport_lottery.db')
        cursor = conn.cursor()
        
        # 检查football_matches表
        cursor.execute('PRAGMA table_info(football_matches)')
        columns = cursor.fetchall()
        
        print("football_matches表结构:")
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            not_null = col[3]
            default_val = col[4]
            pk = col[5]
            print(f"  {col_name}: type={col_type}, notnull={not_null}, default={default_val}, pk={pk}")
            
        # 检查data_sources表
        cursor.execute('PRAGMA table_info(data_sources)')
        columns = cursor.fetchall()
        
        print("\ndata_sources表结构:")
        for col in columns:
            col_name = col[1]
            print(f"  {col_name}")
            
        conn.close()
        
    except Exception as e:
        print(f"检查数据库结构失败: {e}")

def main():
    print("开始调试健康检查API和100qiu数据获取问题")
    print("=" * 60)
    
    # 检查后端连接
    if not test_backend_connection():
        print("\n后端未运行，请先启动后端服务")
        print("命令: cd backend && uvicorn main:app --reload --port 8000")
        return
    
    # 检查数据库结构
    check_database_schema()
    
    # 测试健康检查API
    test_data_source_health()
    
    # 测试100qiu获取API
    test_100qiu_fetch()
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)

if __name__ == '__main__':
    main()