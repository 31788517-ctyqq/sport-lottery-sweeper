"""
优化的启动脚本 - 带日志轮转配置
支持完整的日志轮转策略和监控
"""
import os
import sys
import time
import logging
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

def check_logging_dependencies():
    """检查日志依赖"""
    try:
        import logging.handlers
        print("✅ 日志处理器依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 日志依赖缺失: {e}")
        return False

def setup_environment():
    """设置环境变量"""
    # 确保日志目录存在
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 设置基本环境变量
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    
    print("✅ 环境设置完成")

def initialize_logging():
    """初始化日志系统"""
    try:
        from backend.utils.logging_config import setup_logging
        from backend.config import settings
        
        print("🔧 初始化日志系统...")
        
        # 从配置读取日志参数
        setup_logging(
            log_level=getattr(logging, settings.LOG_LEVEL.upper()),
            max_bytes=settings.LOG_FILE_MAX_BYTES,
            backup_count=settings.LOG_BACKUP_COUNT,
            rotation_interval=settings.LOG_ROTATION_INTERVAL
        )
        
        logger = logging.getLogger(__name__)
        logger.info("日志系统初始化完成")
        print("✅ 日志系统初始化完成")
        
        return True
    except Exception as e:
        print(f"❌ 日志系统初始化失败: {e}")
        return False

def validate_log_configuration():
    """验证日志配置"""
    try:
        from backend.utils.log_manager import log_manager
        
        print("🔍 验证日志配置...")
        
        # 检查日志目录
        if not Path("logs").exists():
            print("⚠️  日志目录不存在，正在创建...")
            Path("logs").mkdir(exist_ok=True)
        
        # 获取配置信息
        config = log_manager.get_current_log_config()
        stats = log_manager.get_log_statistics()
        
        print(f"📊 日志配置验证结果:")
        print(f"   日志级别: {config['log_level']}")
        print(f"   文件大小限制: {config['log_file_max_bytes']:,} bytes ({config['log_file_max_bytes']//1024//1024} MB)")
        print(f"   备份文件数: {config['log_backup_count']}")
        print(f"   轮转间隔: {config['log_rotation_interval']}")
        print(f"   当前日志文件: {stats['total_files']} 个")
        print(f"   磁盘使用: {stats['total_size_mb']} MB")
        
        print("✅ 日志配置验证完成")
        return True
    except Exception as e:
        print(f"❌ 日志配置验证失败: {e}")
        return False

def start_application():
    """启动应用程序"""
    try:
        print("🚀 启动应用程序...")
        
        # 延迟导入以避免循环依赖
        import subprocess
        import argparse
        
        parser = argparse.ArgumentParser(description='启动体育彩票扫盘系统')
        parser.add_argument('--host', default='0.0.0.0', help='主机地址')
        parser.add_argument('--port', type=int, default=8000, help='端口号')
        parser.add_argument('--reload', action='store_true', help='启用热重载')
        parser.add_argument('--workers', type=int, default=1, help='工作进程数')
        
        args = parser.parse_args([])  # 空参数列表
        
        # 设置环境变量
        env = os.environ.copy()
        env['HOST'] = args.host
        env['PORT'] = str(args.port)
        
        # 启动命令
        cmd = [
            sys.executable, "-m", "uvicorn", "backend.main:app",
            "--host", args.host,
            "--port", str(args.port),
            "--log-level", "info"
        ]
        
        if args.reload:
            cmd.append("--reload")
        
        print(f"执行命令: {' '.join(cmd)}")
        print("🎯 应用程序已启动，查看日志请访问 logs/ 目录")
        print("📋 可用的日志管理API:")
        print("   GET  /api/v1/admin/system/logs/statistics - 日志统计")
        print("   GET  /api/v1/admin/system/logs/files - 日志文件列表")
        print("   POST /api/v1/admin/system/logs/cleanup - 清理旧日志")
        print("   POST /api/v1/admin/system/logs/rotate - 手动轮转")
        print("   POST /api/v1/admin/system/logs/archive - 归档日志")
        
        # 启动应用
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n👋 接收到中断信号，正在关闭应用...")
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 体育彩票扫盘系统 - 日志轮转启动器")
    print("=" * 60)
    
    steps = [
        ("检查依赖", check_logging_dependencies),
        ("设置环境", setup_environment),
        ("初始化日志", initialize_logging),
        ("验证配置", validate_log_configuration),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 步骤: {step_name}")
        if not step_func():
            print(f"❌ {step_name} 失败，退出启动")
            sys.exit(1)
        time.sleep(0.5)  # 短暂暂停以便观察
    
    print("\n" + "=" * 60)
    print("✅ 所有初始化步骤完成，准备启动应用")
    print("=" * 60)
    
    # 询问是否继续启动
    try:
        response = input("\n是否立即启动应用程序? (Y/n): ").strip().lower()
        if response in ['', 'y', 'yes']:
            start_application()
        else:
            print("💡 跳过应用启动。您可以通过 'python scripts/start_with_logging.py' 再次运行")
    except KeyboardInterrupt:
        print("\n👋 用户取消启动")

if __name__ == "__main__":
    main()