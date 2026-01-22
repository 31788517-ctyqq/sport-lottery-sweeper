#!/usr/bin/env python3
"""
性能优化启动脚本
一键启动优化版后端服务，包含时间监测
"""
import time
import os
from datetime import datetime
import uvicorn
from backend.optimized_main import app


def launch_backend():
    """
    启动后端服务
    """
    try:
        from backend.optimized_main import app
        import uvicorn
        
        # 从配置文件获取设置
        host = os.getenv("BACKEND_HOST", "127.0.0.1")
        port = int(os.getenv("BACKEND_PORT", 8000))
        
        print(f"🚀 启动后端服务在 {host}:{port}")
        print(f"📋 API 文档: http://{host}:{port}/docs")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,  # 生产环境不启用热重载
            log_level="info",
            timeout_keep_alive=30  # 增加keep-alive超时时间
        )
    except ImportError as e:
        print(f"❌ 后端服务启动失败: {e}")
        print("💡 请检查 backend.optimized_main 模块是否存在")
        return False
    except Exception as e:
        print(f"❌ 启动过程中发生未知错误: {e}")
        return False

def run_backend_with_monitoring():
    """
    启动带监控的后端服务
    """
    try:
        from backend.optimized_main import app
        import uvicorn
        from threading import Thread
        
        # 启动监控线程
        monitor_thread = Thread(target=monitor_backend_performance, daemon=True)
        monitor_thread.start()
        
        # 启动后端服务
        host = os.getenv("BACKEND_HOST", "127.0.0.1")
        port = int(os.getenv("BACKEND_PORT", 8000))
        
        print(f"🚀 启动带监控的后端服务在 {host}:{port}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ 启动带监控的后端服务失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 启动过程中发生未知错误: {e}")
        return False


def run_backend_with_debugger():
    """
    启动带调试器的后端服务
    """
    try:
        from backend.optimized_main import app
        import uvicorn
        
        # 启动后端服务
        host = os.getenv("BACKEND_HOST", "127.0.0.1")
        port = int(os.getenv("BACKEND_PORT", 8000))
        
        print(f"🐛 启动带调试器的后端服务在 {host}:{port}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=True,  # 开启热重载
            debug=True,
            log_level="debug"
        )
    except ImportError as e:
        print(f"❌ 启动带调试器的后端服务失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 启动过程中发生未知错误: {e}")
        return False

def run_backend_dev():
    """
    启动开发环境的后端服务
    """
    try:
        from backend.main import app
        import uvicorn
        
        # 从环境变量获取配置，如果不存在则使用默认值
        host = os.getenv("BACKEND_HOST", "127.0.0.1")
        port = int(os.getenv("BACKEND_PORT", 8000))
        
        print(f"🚀 启动开发环境后端服务在 {host}:{port}")
        print(f"📋 API 文档: http://{host}:{port}/docs")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=True,  # 开发环境启用热重载
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ 后端服务启动失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 启动过程中发生未知错误: {e}")
        return False

def launch_server():
    """启动优化版服务器"""
    # 从配置文件获取设置
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", 8000))
    
    print("🚀 启动优化版竞彩足球扫盘系统后端服务")
    print("="*60)
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 服务地址: http://{host}:{port}")
    print(f"📋 API文档: http://{host}:{port}/docs")
    print(f"🔍 健康检查: http://{host}:{port}/health")
    print("="*60)
    
    start_time = time.time()
    
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 🚀 正在启动服务器...")
    
    try:
        # 启动Uvicorn服务器
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,  # 生产环境不启用热重载
            log_level="info",
            timeout_keep_alive=30  # 增加keep-alive超时时间
        )
    except KeyboardInterrupt:
        total_runtime = time.time() - start_time
        print(f"\n[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 💤 服务已停止")
        print(f"🕒 总运行时间: {total_runtime:.2f}秒")
        print("👋 感谢使用优化版竞彩足球扫盘系统！")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='Backend Service Launcher')
    parser.add_argument('--mode', choices=['normal', 'monitored', 'debug'], 
                        default='normal', help='Launch mode')
    parser.add_argument('--host', type=str, default=None, help='Host address')
    parser.add_argument('--port', type=int, default=None, help='Port number')
    
    args = parser.parse_args()
    
    # 设置环境变量
    if args.host:
        os.environ["BACKEND_HOST"] = args.host
    if args.port:
        os.environ["BACKEND_PORT"] = str(args.port)
    
    # 根据模式启动后端
    if args.mode == 'normal':
        print("📡 启动普通模式...")
        launch_backend()
    elif args.mode == 'monitored':
        print("📈 启动监控模式...")
        run_backend_with_monitoring()
    elif args.mode == 'debug':
        print("🐛 启动调试模式...")
        run_backend_with_debugger()

if __name__ == "__main__":
    main()
