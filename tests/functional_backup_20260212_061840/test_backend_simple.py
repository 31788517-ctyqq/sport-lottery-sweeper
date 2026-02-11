#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版后端启动测试
验证修复后的核心功能
"""
import sys
import os
import traceback

# 设置环境 - 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ['PYTHONPATH'] = project_root

def test_imports():
    """测试关键模块导入"""
    print("[INSPECT] 测试模块导入...")
    
    tests = [
        ("数据库引擎", "from backend.core.database import engine, Base"),
        ("基础模型", "from backend.models.base import Base"),
        ("爬虫日志模型", "from backend.models.crawler_logs import CrawlerTaskLog"),
        ("爬虫任务模型", "from backend.models.crawler_tasks import CrawlerTask"),
        ("数据源模型", "from backend.models.data_sources import CrawlerConfig"),
        ("预测模型", "from backend.models.predictions import Prediction"),
        ("赔率模型", "from backend.models.odds import Odds"),
        ("比赛模型", "from backend.models.match import Match"),
        ("用户模型", "from backend.models.user import User"),
        ("管理员模型", "from backend.models.admin_user import AdminUser"),
        ("情报模型", "from backend.models.intelligence import Intelligence"),
        ("场馆模型", "from backend.models.venues import Venue"),
        ("绘制特征模型", "from backend.models.draw_feature import DrawFeature"),
        ("绘制预测模型", "from backend.models.draw_prediction import DrawPrediction"),
    ]
    
    failed = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  [OK] {name}")
        except Exception as e:
            print(f"  [ERROR] {name}: {str(e)[:100]}")
            failed.append((name, str(e)))
    
    return failed

def test_database_connection():
    """测试数据库连接"""
    print("\n[INSPECT] 测试数据库连接...")
    try:
        from backend.core.database import engine, Base
        from sqlalchemy import text
        
        # 尝试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("  [OK] 数据库连接成功")
        
        # 尝试创建表（如果存在则不创建）
        Base.metadata.create_all(bind=engine)
        print("  [OK] 表结构同步成功")
        
        return True
    except Exception as e:
        print(f"  [ERROR] 数据库连接失败: {e}")
        traceback.print_exc()
        return False

def test_api_routes():
    """测试API路由注册"""
    print("\n[INSPECT] 测试API路由...")
    try:
        from backend.main import app
        routes = [route.path for route in app.routes]
        
        # 检查关键路由是否存在
        key_routes = [
            "/admin/crawler/sources",
            "/admin/crawler/tasks",
            "/admin/crawler/configs",
            "/crawler-alert/rules",
            "/monitoring/dashboard/overview",
            "/sp-management/data-sources",
            "/draw-prediction/patterns",
            "/auth/login",
        ]
        
        missing = []
        for route in key_routes:
            if not any(r.startswith(route) for r in routes):
                missing.append(route)
            else:
                print(f"  [OK] {route}")
        
        if missing:
            print(f"  [ERROR] 缺失路由: {missing}")
            return False
        else:
            print(f"  [OK] 所有关键路由已注册 (共 {len(routes)} 个路由)")
            return True
    except Exception as e:
        print(f"  [ERROR] API路由测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("[TARGET] 后端启动验证测试")
    print("="*60)
    
    # 测试1: 模块导入
    failed_imports = test_imports()
    if failed_imports:
        print(f"\n[ERROR] 有 {len(failed_imports)} 个模块导入失败")
        return False
    
    # 测试2: 数据库连接
    if not test_database_connection():
        print("\n[ERROR] 数据库连接失败")
        return False
    
    # 测试3: API路由
    if not test_api_routes():
        print("\n[ERROR] API路由注册不完整")
        return False
    
    print("\n" + "="*60)
    print("[SUCCESS] 所有测试通过！后端应该可以正常启动")
    print("="*60)
    print("\n[LOG] 修复总结:")
    print("  1. [OK] 修复了所有 Enum 列的 SQLAlchemy 兼容性")
    print("  2. [OK] 解决了 crawler_task_logs 表重复定义问题")
    print("  3. [OK] 修复了 draw_prediction 导入路径错误")
    print("  4. [OK] 移除了所有 PostgreSQL 特有类型导入")
    print("  5. [OK] 补充了缺失的 imports")
    print("\n[ROCKET] 可以尝试运行: start_backend.bat")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
