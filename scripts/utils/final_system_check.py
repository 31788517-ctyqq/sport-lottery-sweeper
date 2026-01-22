#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终系统完整性检查
验证管理后台功能是否完整实现
"""
import sys
import os
import sqlite3

def check_database_tables():
    """检查数据库表是否完整"""
    print("=== 数据库表检查 ===")
    try:
        conn = sqlite3.connect('sport_lottery.db')
        c = conn.cursor()
        c.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name;')
        tables = [row[0] for row in c.fetchall()]
        
        required_tables = [
            'admin_data',      # 通用数据管理
            'system_configs',  # 系统配置管理
            'crawler_configs', # 爬虫配置管理
            'intelligence_records'  # 智能分析记录管理
        ]
        
        print(f"现有表: {tables}")
        
        missing_tables = []
        for table in required_tables:
            if table in tables:
                print(f"✓ {table} 表存在")
            else:
                print(f"✗ {table} 表缺失")
                missing_tables.append(table)
        
        conn.close()
        
        if not missing_tables:
            print("✓ 所有必需的数据表都存在")
            return True
        else:
            print(f"✗ 缺失表: {missing_tables}")
            return False
            
    except Exception as e:
        print(f"✗ 数据库检查失败: {e}")
        return False

def check_backend_modules():
    """检查后端模块是否完整"""
    print("\n=== 后端模块检查 ===")
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_root, 'backend')
    sys.path.insert(0, backend_dir)
    sys.path.insert(0, project_root)
    
    required_modules = {
        'models': 'backend.models',
        'crud.data': 'backend.crud.data',
        'crud.system_config': 'backend.crud.system_config', 
        'crud.crawler_config': 'backend.crud.crawler_config',
        'crud.intelligence_record': 'backend.crud.intelligence_record',
        'schemas.data': 'backend.schemas.data',
        'schemas.system_config': 'backend.schemas.system_config',
        'schemas.crawler_config': 'backend.schemas.crawler_config',
        'schemas.intelligence_record': 'backend.schemas.intelligence_record',
        'admin.api.v1.crawler_config_admin': 'backend.admin.api.v1.crawler_config_admin',
        'admin.api.v1.intelligence_admin': 'backend.admin.api.v1.intelligence_admin'
    }
    
    all_passed = True
    for module_name, import_path in required_modules.items():
        try:
            __import__(import_path)
            print(f"✓ {module_name} 模块导入成功")
        except Exception as e:
            print(f"✗ {module_name} 模块导入失败: {e}")
            all_passed = False
    
    return all_passed

def check_frontend_pages():
    """检查前端页面文件是否存在"""
    print("\n=== 前端页面检查 ===")
    
    frontend_admin_dir = 'frontend/src/views/admin'
    required_pages = [
        'Data.vue',      # 数据管理
        'System.vue',    # 系统配置
        'Matches.vue',   # 比赛管理
        'Intelligence.vue', # 智能分析
        'CrawlerConfig.vue' # 爬虫配置
    ]
    
    all_passed = True
    for page in required_pages:
        page_path = os.path.join(frontend_admin_dir, page)
        if os.path.exists(page_path):
            print(f"✓ {page} 页面存在")
        else:
            print(f"✗ {page} 页面缺失")
            all_passed = False
    
    return all_passed

def check_api_structure():
    """检查API结构是否完整"""
    print("\n=== API结构检查 ===")
    
    api_dir = 'frontend/src/api'
    required_apis = [
        'admin.js',      # 管理后台API
        'crawler.js',    # 爬虫API
        'intelligence.js' # 智能分析API
    ]
    
    all_passed = True
    for api_file in required_apis:
        api_path = os.path.join(api_dir, api_file)
        if os.path.exists(api_path):
            print(f"✓ {api_file} API文件存在")
        else:
            print(f"✗ {api_file} API文件缺失")
            all_passed = False
    
    return all_passed

def main():
    """主检查函数"""
    print("🔍 开始系统完整性检查...")
    print("=" * 50)
    
    checks = [
        ("数据库表", check_database_tables),
        ("后端模块", check_backend_modules),
        ("前端页面", check_frontend_pages),
        ("API结构", check_api_structure)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"✗ {check_name} 检查异常: {e}")
            results.append((check_name, False))
    
    # 输出总结
    print("\n" + "=" * 50)
    print("📊 检查结果总结")
    print("=" * 50)
    
    passed_count = 0
    total_count = len(results)
    
    for check_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{check_name}: {status}")
        if result:
            passed_count += 1
    
    print(f"\n总计: {passed_count}/{total_count} 项检查通过")
    
    if passed_count == total_count:
        print("\n🎉 恭喜！所有检查都通过了！")
        print("✅ 管理后台功能已完整实现")
        print("\n📋 可进行的后续操作:")
        print("1. 安装项目依赖: pip install -r requirements.txt")
        print("2. 启动后端服务: cd scripts && python start_backend.py")
        print("3. 启动前端服务: npm run dev (在frontend目录下)")
        print("4. 访问管理后台: http://localhost:5173/admin")
        return True
    else:
        print("\n⚠️  部分检查未通过，请检查上述错误信息")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)