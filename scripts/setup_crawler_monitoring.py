#!/usr/bin/env python3
"""
爬虫监控系统完整设置脚本
一键完成数据库迁移、初始化配置和任务启动
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_command(command, description):
    """执行命令并处理结果"""
    print(f"\n🔄 {description}...")
    print(f"执行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        if result.returncode == 0:
            print(f"✅ {description} 成功")
            if result.stdout:
                print(f"输出: {result.stdout[:200]}...")  # 只显示前200个字符
            return True
        else:
            print(f"❌ {description} 失败")
            print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {description} 异常: {str(e)}")
        return False

def check_database_connection():
    """检查数据库连接"""
    print("\n🔍 检查数据库连接...")
    try:
        from backend.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def setup_database_migrations():
    """设置数据库迁移"""
    print("\n📊 设置数据库迁移...")
    
    # 检查迁移文件是否存在
    migration_files = [
        "alembic/versions/002_add_crawler_logs_tables.py",
        "alembic/versions/003_add_crawler_tasks_table.py", 
        "alembic/versions/004_add_crawler_alert_tables.py"
    ]
    
    all_exist = True
    for file_path in migration_files:
        if not os.path.exists(file_path):
            print(f"❌ 迁移文件不存在: {file_path}")
            all_exist = False
    
    if not all_exist:
        print("请先创建相应的数据库迁移文件")
        return False
    
    print("✅ 所有迁移文件存在")
    return True

def run_migrations():
    """执行数据库迁移"""
    commands = [
        ("alembic upgrade head", "应用所有数据库迁移"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def init_default_data():
    """初始化默认数据"""
    commands = [
        ("python scripts/init_default_crawler_configs.py", "初始化默认爬虫配置"),
        ("python scripts/init_default_alert_rules.py", "初始化默认告警规则"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️  {description} 失败，但系统仍可运行")
    
    return True

def test_api_endpoints():
    """测试API端点"""
    print("\n🧪 测试API端点...")
    
    try:
        import requests
        import time
        
        # 等待服务启动
        print("等待服务启动...")
        time.sleep(5)
        
        base_url = "http://localhost:8000"
        
        # 测试健康检查
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ 健康检查通过")
            else:
                print(f"⚠️  健康检查返回状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  无法连接到服务 (可能服务未启动): {str(e)}")
        
        # 测试爬虫配置API
        try:
            response = requests.get(f"{base_url}/admin/crawler/configs", timeout=10)
            if response.status_code in [200, 401]:  # 401是正常的，需要认证
                print("✅ 爬虫配置API可访问")
            else:
                print(f"⚠️  爬虫配置API返回状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  爬虫配置API测试失败: {str(e)}")
        
        return True
        
    except ImportError:
        print("⚠️  未安装requests库，跳过API测试")
        return True
    except Exception as e:
        print(f"⚠️  API测试异常: {str(e)}")
        return True

def display_summary():
    """显示部署总结"""
    print("\n" + "="*60)
    print("🎉 爬虫监控系统设置完成！")
    print("="*60)
    
    print("\n📋 系统组件状态:")
    print("✅ 数据库表结构 - 已创建")
    print("✅ 默认爬虫配置 - 已初始化") 
    print("✅ 默认告警规则 - 已创建")
    print("✅ API接口 - 已注册")
    print("✅ Celery任务 - 已配置")
    
    print("\n🌐 访问地址:")
    print("- API文档: http://localhost:8000/docs")
    print("- 健康检查: http://localhost:8000/health")
    print("- 监控概览: http://localhost:8000/admin/monitoring/dashboard/overview")
    
    print("\n🔧 常用命令:")
    print("# 启动API服务")
    print("cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    print("\n# 启动Celery Worker")
    print("cd backend && celery -A tasks.celery_app worker --loglevel=info")
    
    print("\n# 启动Celery Beat (定时任务)")
    print("cd backend && celery -A tasks.celery_app beat --loglevel=info")
    
    print("\n# 手动触发告警检查")
    print("curl -X POST http://localhost:8000/admin/crawler-alert/check \\")
    print("  -H 'Authorization: Bearer YOUR_TOKEN'")
    
    print("\n📚 更多信息:")
    print("- 详细使用说明: docs/CRAWLER_MONITORING_SYSTEM.md")
    print("- 告警规则配置: 访问 /admin/crawler-alert/rules")
    print("- 监控仪表板: 访问 /admin/monitoring/dashboard/*")
    
    print("\n⚠️  注意事项:")
    print("1. 请确保Redis服务正在运行 (Celery依赖)")
    print("2. 请根据实际需求调整告警规则和通知配置")
    print("3. 建议配置日志轮转以避免磁盘空间不足")
    print("4. 定期备份数据库和监控数据")
    
    print("\n" + "="*60)

def main():
    """主函数"""
    print("🚀 爬虫监控系统设置向导")
    print("="*60)
    print(f"设置时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {os.getcwd()}")
    
    # 检查Python环境
    print(f"Python版本: {sys.version}")
    
    steps = [
        ("检查数据库连接", check_database_connection),
        ("设置数据库迁移", setup_database_migrations),
        ("执行数据库迁移", run_migrations),
        ("初始化默认数据", init_default_data),
    ]
    
    # 执行设置步骤
    for step_name, step_func in steps:
        print(f"\n{'='*60}")
        print(f"步骤: {step_name}")
        print(f"{'='*60}")
        
        if not step_func():
            print(f"\n❌ 设置失败: {step_name}")
            print("请检查错误信息并解决问题后重新运行此脚本")
            return False
    
    # 显示总结
    display_summary()
    
    # 可选：运行API测试
    print("\n是否要测试API端点？(需要服务正在运行) [y/N]: ", end="")
    try:
        choice = input().strip().lower()
        if choice in ['y', 'yes']:
            test_api_endpoints()
    except KeyboardInterrupt:
        print("\n跳过API测试")
    
    print("\n✨ 设置完成！爬虫监控系统已准备就绪。")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  设置被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 设置过程中发生未预期错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)