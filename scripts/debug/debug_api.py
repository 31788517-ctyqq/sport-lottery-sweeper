#!/usr/bin/env python3
"""调试API端点"""

import sys
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error
import json
import ssl

# 禁用SSL证书验证
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试导入是否正常"""
    try:
        print("正在测试导入...")
        from backend.api.v1.caipiao_data import router
        print("✅ caipiao_data 路由导入成功")
        
        from backend.schemas.caipiao_data import CaipiaoData
        print("✅ CaipiaoData schema 导入成功")
        
        from backend.schemas.response import PageResponse
        print("✅ PageResponse schema 导入成功")
        
        from backend.crud.crud_caipiao_data import get_caipiao_data_list
        print("✅ CRUD 函数导入成功")
        
        from backend.database import get_db
        print("✅ 数据库函数导入成功")
        
        print("所有导入测试通过！")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_db_connection():
    """测试数据库连接"""
    try:
        print("\n正在测试数据库连接...")
        from backend.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✅ 数据库连接正常，找到 {len(tables)} 个表")
        
        if 'caipiao_data' in tables:
            print("✅ caipiao_data 表存在")
        else:
            print("❌ caipiao_data 表不存在")
            
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crud_functions():
    """测试CRUD函数"""
    try:
        print("\n正在测试CRUD函数...")
        from backend.database import SessionLocal
        from backend.crud.crud_caipiao_data import get_caipiao_data_count
        
        db = SessionLocal()
        try:
            count = get_caipiao_data_count(db)
            print(f"✅ 获取caipiao_data数量: {count}")
        finally:
            db.close()
        
        return True
    except Exception as e:
        print(f"❌ CRUD函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint(url, headers=None):
    """测试API端点并返回详细错误信息"""
    if headers is None:
        headers = {}
    
    print(f"测试端点: {url}")
    
    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        response = urllib.request.urlopen(req, context=ssl_context)
        data = response.read().decode('utf-8')
        print(f"状态码: {response.getcode()}")
        print(f"响应数据: {data}")
        return True
    except urllib.error.HTTPError as e:
        print(f"HTTP错误: {e.code} - {e.reason}")
        try:
            error_data = e.read().decode('utf-8')
            print(f"错误详情: {error_data}")
        except:
            print("无法读取错误详情")
        return False
    except urllib.error.URLError as e:
        print(f"URL错误: {e.reason}")
        return False
    except Exception as e:
        print(f"其他错误: {str(e)}")
        return False

def main():
    # 测试API端点
    base_url = "http://localhost:8000/api/v1/admin"
    
    # 模拟token
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTA4ODQwMCwiYWRtaW5faWQiOjEsInVzZXJuYW1lIjoiYWRtaW4ifQ.dummy_token_for_testing",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        f"{base_url}/admin-users?skip=0&limit=10",
        f"{base_url}/admin-users/current-user",
        f"{base_url}/admin-users/stats",
        f"{base_url}/admin-users/stats/overview"
    ]
    
    for endpoint in endpoints:
        test_api_endpoint(endpoint, headers)
        print("-" * 50)

if __name__ == "__main__":
    main()
