"""
最终系统功能检查脚本
验证竞彩足球扫盘系统核心功能是否就绪
"""
import requests
import json
import time
import sys
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def check_backend_service():
    """检查后端服务可用性"""
    print_section("1. 后端服务可用性检查")
    
    base_url = "http://localhost:8000"
    endpoints = [
        ("/api/v1/admin/sources", "GET", None),
        ("/api/v1/admin/tasks", "GET", None),
        ("/api/v1/crawler/crawler/", "GET", None),
        ("/api/v1/real-time-decision/decisions", "GET", None),
    ]
    
    all_ok = True
    for path, method, data in endpoints:
        try:
            if method == "GET":
                r = requests.get(f"{base_url}{path}", timeout=5)
            elif method == "POST":
                r = requests.post(f"{base_url}{path}", json=data, timeout=5)
            
            status = r.status_code
            if 200 <= status < 300:
                print(f"✅ {path}: {status}")
            else:
                print(f"❌ {path}: {status} - {r.text[:100]}")
                all_ok = False
        except Exception as e:
            print(f"❌ {path}: 连接失败 - {e}")
            all_ok = False
    
    return all_ok

def check_admin_auth():
    """检查管理员认证功能"""
    print_section("2. 管理员认证功能检查")
    
    try:
        login_data = {"username": "admin", "password": "admin123"}
        r = requests.post("http://localhost:8000/api/v1/auth/login", 
                         json=login_data, timeout=5)
        
        if r.status_code == 200:
            data = r.json()
            token = data.get("data", {}).get("access_token", "")
            if token:
                print(f"✅ 管理员登录成功")
                print(f"   令牌长度: {len(token)} 字符")
                print(f"   令牌前缀: {token[:50]}...")
                return token
            else:
                print("❌ 登录成功但未返回令牌")
                return None
        else:
            print(f"❌ 登录失败: {r.status_code}")
            print(f"   响应: {r.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ 认证检查失败: {e}")
        return None

def check_data_source_config():
    """检查数据源配置"""
    print_section("3. 数据源配置检查")
    
    try:
        r = requests.get("http://localhost:8000/api/v1/admin/sources", timeout=5)
        if r.status_code == 200:
            data = r.json()
            items = data.get("data", {}).get("items", [])
            print(f"✅ 数据源API正常，共 {len(items)} 个数据源")
            
            # 检查100球网数据源
            hundred_qiu = [s for s in items if "100球网" in s.get("name", "")]
            if hundred_qiu:
                source = hundred_qiu[0]
                print(f"✅ 100球网数据源已配置")
                print(f"   数据源ID: {source.get('id')}")
                print(f"   数据源URL: {source.get('url')}")
                print(f"   状态: {'启用' if source.get('status') else '禁用'}")
                return True
            else:
                print("❌ 100球网数据源未找到")
                return False
        else:
            print(f"❌ 数据源API错误: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ 数据源检查失败: {e}")
        return False

def check_task_management():
    """检查任务管理功能"""
    print_section("4. 任务管理功能检查")
    
    try:
        r = requests.get("http://localhost:8000/api/v1/admin/tasks", timeout=5)
        if r.status_code == 200:
            data = r.json()
            items = data.get("data", {}).get("items", [])
            print(f"✅ 任务API正常，共 {len(items)} 个任务")
            
            if items:
                for task in items[:3]:  # 显示前3个任务
                    print(f"   - 任务: {task.get('name')} (ID: {task.get('id')})")
                return True
            else:
                print("⚠️  任务列表为空（可能需要创建任务）")
                return True  # API正常，只是没有任务
        else:
            print(f"❌ 任务API错误: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ 任务检查失败: {e}")
        return False

def check_frontend_service():
    """检查前端服务"""
    print_section("5. 前端服务检查")
    
    try:
        r = requests.get("http://localhost:3002", timeout=5)
        if r.status_code == 200:
            content = r.text
            if "体育彩票扫盘系统" in content or "竞彩" in content:
                print("✅ 前端服务运行正常")
                print("   页面标题包含: '体育彩票扫盘系统'")
                return True
            else:
                print("⚠️  前端服务运行但内容异常")
                return False
        else:
            print(f"❌ 前端服务错误: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端检查失败: {e}")
        return False

def check_database():
    """检查数据库状态"""
    print_section("6. 数据库状态检查")
    
    import os
    import sqlite3
    
    db_path = "data/sport_lottery.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取表数量
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # 关键表检查
            key_tables = ["data_sources", "crawler_tasks", "matches", "users"]
            found_tables = []
            
            for table in tables:
                table_name = table[0]
                if table_name in key_tables:
                    found_tables.append(table_name)
            
            print(f"✅ 数据库文件存在: {db_path}")
            print(f"   数据库表数量: {len(tables)}")
            print(f"   关键表找到: {len(found_tables)}/{len(key_tables)}个")
            
            if found_tables:
                print("   已找到的表:", ", ".join(found_tables))
            
            conn.close()
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    else:
        print(f"❌ 数据库文件不存在: {db_path}")
        return False

def check_crawler_functionality():
    """检查爬虫功能"""
    print_section("7. 爬虫功能检查")
    
    try:
        # 检查爬虫管理API
        r = requests.get("http://localhost:8000/api/v1/crawler/crawler/", timeout=5)
        if r.status_code == 200:
            print("✅ 爬虫管理API正常")
            return True
        else:
            print(f"⚠️  爬虫管理API返回: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ 爬虫功能检查失败: {e}")
        return False

def main():
    print("竞彩足球扫盘系统 - 最终功能检查")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "backend": check_backend_service(),
        "auth": bool(check_admin_auth()),
        "data_source": check_data_source_config(),
        "task": check_task_management(),
        "frontend": check_frontend_service(),
        "database": check_database(),
        "crawler": check_crawler_functionality(),
    }
    
    print_section("检查结果汇总")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    print("\n详细结果:")
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status} - {name}")
    
    print("\n" + "="*60)
    if passed == total:
        print("🎉 所有核心功能检查通过！系统已准备好投入使用。")
        print("下一步建议:")
        print("  1. 访问前端: http://localhost:3002")
        print("  2. 使用管理员账号登录: admin / admin123")
        print("  3. 在数据源管理页面验证100球网数据源")
        print("  4. 创建数据采集任务并启动")
        return 0
    else:
        print("⚠️  部分功能需要检查。")
        print("建议检查项目:")
        for name, passed in results.items():
            if not passed:
                print(f"  - {name}")
        return 1

if __name__ == "__main__":
    sys.exit(main())