"""
启动时间监测脚本
测量应用各部分的启动时间，评估优化效果
"""
import time
import sys
import os
from datetime import datetime


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class StartupAnalyzer:
    """
    启动性能分析器
    用于系统化地测量和分析应用的启动时间
    """

    def measure_backend_config_loading_time(self):
        """
        测量后端配置加载时间
        """
        try:
            import time
            
            start_time = time.time()
            
            # 导入后端配置
            from backend.config import settings
            from backend.middleware import RequestLoggingMiddleware
            from backend.api import router as api_router
            
            end_time = time.time()
            loading_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            return {
                'loading_time_ms': loading_time,
                'measured_at': datetime.now().isoformat(),
                'configs_loaded': ['settings', 'middleware', 'api_router']
            }
        except ImportError as e:
            print(f"❌ 无法测量后端配置加载时间: {e}")
            return {'loading_time_ms': -1, 'error': str(e)}

    def calculate_backend_startup_time(self):
        """
        计算后端启动时间
        """
        try:
            import time
            
            # 记录开始时间
            start_time = time.time()
            
            # 导入后端配置
            from backend.config import settings
            from backend.middleware import RequestLoggingMiddleware
            from backend.api import router as api_router
            
            # 记录结束时间并计算耗时
            end_time = time.time()
            startup_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            return {
                'startup_time_ms': startup_time,
                'components_loaded': True,
                'timestamp': datetime.now().isoformat()
            }
        except ImportError as e:
            print(f"❌ 无法计算后端启动时间: {e}")
            return {'components_loaded': False, 'error': str(e)}

    def measure_backend_full_startup_time(self):
        """
        测量后端完整启动时间
        """
        try:
            import time
            from backend.config import settings
            from backend.middleware import RequestLoggingMiddleware
            from backend.api import router as api_router
            from backend.database import engine, SessionLocal
            from backend.models import Base
            from backend.core.config import settings as core_settings
            from backend.utils.logging_config import logger
            from backend.schemas.response import UnifiedResponse
            from backend.api.v1.matches import router as matches_router
            from backend.api.v1.auth import router as auth_router
            from backend.api.v1.jczq import router as jczq_router
            from backend.services.crawler_service import CrawlerService
            from backend.core.security import get_password_hash, verify_password
            
            end_time = time.time()
            startup_time = (end_time - self.start_time) * 1000
            
            return {
                'full_startup_time_ms': startup_time,
                'components_loaded': 12,  # 记录加载的组件数量
                'timestamp': datetime.now().isoformat()
            }
        except ImportError as e:
            print(f"❌ 无法测量后端完整启动时间: {e}")
            return {'full_startup_time_ms': -1, 'error': str(e)}

    def get_backend_components(self):
        """
        获取后端组件用于性能测试
        """
        try:
            # 导入后端配置
            from backend.config import settings
            from backend.middleware import RequestLoggingMiddleware
            from backend.api import router as api_router
            
            return {
                'settings': settings,
                'middleware': RequestLoggingMiddleware,
                'api_router': api_router
            }
        except ImportError as e:
            print(f"❌ 无法导入后端组件: {e}")
            return None

    def measure_specific_component_times(self):
        """
        测量特定组件加载时间
        """
        import time
        
        # 测量配置组件加载时间
        start_time = time.time()
        try:
            from backend.config import settings
            from backend.middleware import RequestLoggingMiddleware
            from backend.api import router as api_router
            config_end_time = time.time()
            config_load_time = (config_end_time - start_time) * 1000
        except ImportError as e:
            print(f"❌ 配置组件加载失败: {e}")
            config_load_time = -1
        
        # 测量数据库组件加载时间
        db_start_time = time.time()
        try:
            from backend.database import engine, SessionLocal
            from backend.models import Base
            from backend.core.config import settings as core_settings
            db_end_time = time.time()
            db_load_time = (db_end_time - db_start_time) * 1000
        except ImportError as e:
            print(f"❌ 数据库组件加载失败: {e}")
            db_load_time = -1
        
        # 测量API组件加载时间
        api_start_time = time.time()
        try:
            from backend.api.v1.matches import router as matches_router
            from backend.api.v1.auth import router as auth_router
            from backend.api.v1.jczq import router as jczq_router
            api_end_time = time.time()
            api_load_time = (api_end_time - api_start_time) * 1000
        except ImportError as e:
            print(f"❌ API组件加载失败: {e}")
            api_load_time = -1
        
        return {
            'config_load_time_ms': config_load_time,
            'database_load_time_ms': db_load_time,
            'api_load_time_ms': api_load_time,
            'measured_at': datetime.now().isoformat()
        }


# 创建分析器实例
analyzer = StartupAnalyzer()


@contextmanager
def timer_section(name: str):
    """计时上下文管理器"""
    start = time.perf_counter()
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] 开始: {name}")
    yield
    elapsed = time.perf_counter() - start
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] 完成: {name} (耗时: {elapsed:.3f}s)")


def test_import_times():
    """测试各模块的导入时间"""
    print("="*60)
    print("🚀 模块导入时间测试")
    print("="*60)
    
    total_start = time.time()
    
    with timer_section("导入FastAPI"):
        from fastapi import FastAPI
    
    with timer_section("导入配置"):
        from backend.config import settings
    
    with timer_section("导入中间件"):
        from backend.middleware import RequestLoggingMiddleware
    
    with timer_section("导入CORS中间件"):
        from fastapi.middleware.cors import CORSMiddleware
    
    with timer_section("导入静态文件"):
        from fastapi.staticfiles import StaticFiles
    
    with timer_section("导入API路由"):
        from backend.api import router as api_router
    
    with timer_section("创建FastAPI应用"):
        app = FastAPI(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            description=settings.DESCRIPTION,
            openapi_url=f"{settings.API_V1_STR}/openapi.json",
            docs_url="/docs" if settings.DOCS_ENABLED else None,
            redoc_url="/redoc" if settings.DOCS_ENABLED else None,
        )
    
    with timer_section("配置CORS中间件"):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    with timer_section("添加自定义中间件"):
        app.add_middleware(RequestLoggingMiddleware)
    
    with timer_section("挂载静态文件"):
        static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        app.mount("/jczq", StaticFiles(directory=static_dir, html=True), name="jczq")
    
    with timer_section("包含API路由"):
        app.include_router(api_router, prefix=settings.API_V1_STR)
    
    with timer_section("添加根路径路由"):
        @app.get("/")
        async def root():
            """根路径返回欢迎信息"""
            return {"message": "Welcome to Sport Lottery Sweeper API", "startup_time": time.time() - total_start}
    
    total_time = time.time() - total_start
    
    print("="*60)
    print(f"✅ 应用创建完成，总耗时: {total_time:.3f}s")
    print("="*60)
    
    return app, total_time


def run_detailed_benchmark():
    """运行详细的基准测试"""
    print("🎯 详细启动时间基准测试")
    print("-" * 40)
    
    # 多次运行以获得更准确的结果
    times = []
    for i in range(3):
        print(f"\n第 {i+1} 次测试:")
        _, time_taken = test_import_times()
        times.append(time_taken)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print("\n" + "="*60)
    print("📊 启动时间基准测试结果")
    print("="*60)
    print(f"平均启动时间: {avg_time:.3f}s")
    print(f"最快启动时间: {min_time:.3f}s")
    print(f"最慢启动时间: {max_time:.3f}s")
    print(f"测试次数: {len(times)}")
    print("="*60)
    
    # 性能评级
    if avg_time < 0.5:
        rating = "⭐⭐⭐⭐⭐ 极快 - 优秀"
    elif avg_time < 1.0:
        rating = "⭐⭐⭐⭐  很快 - 良好" 
    elif avg_time < 2.0:
        rating = "⭐⭐⭐   中等 - 可接受"
    elif avg_time < 3.0:
        rating = "⭐⭐    较慢 - 需优化"
    else:
        rating = "⭐     很慢 - 急需优化"
    
    print(f"性能评级: {rating}")
    print("="*60)


if __name__ == "__main__":
    print("⏱️  启动时间监测工具")
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    run_detailed_benchmark()