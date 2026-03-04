import time
import sys
import os
from contextlib import contextmanager
from typing import Callable, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
        self.order = []
        
    @contextmanager
    def measure(self, name: str):
        """测量代码块执行时间的上下文管理器"""
        start = time.perf_counter()
        print(f"[{time.strftime('%H:%M:%S')}] 开始执行: {name}")
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.metrics[name] = elapsed
            self.order.append(name)
            print(f"[{time.strftime('%H:%M:%S')}] 完成: {name} ({elapsed:.3f}s)")
    
    def report(self):
        """打印性能报告"""
        print("\n" + "="*60)
        print("性能监控报告")
        print("="*60)
        
        total_time = sum(self.metrics.values())
        print(f"总启动时间: {total_time:.3f}s")
        print()
        
        print("各组件启动时间:")
        for name in self.order:
            time_taken = self.metrics[name]
            percentage = (time_taken / total_time) * 100
            print(f"  {name:<30} {time_taken:>6.3f}s ({percentage:>5.1f}%)")
        
        print("\n性能建议:")
        slow_components = [(k, v) for k, v in self.metrics.items() if v > 0.5]
        if slow_components:
            print("  以下组件启动时间较长 (>0.5s)，建议优化:")
            for name, time_taken in slow_components:
                print(f"    - {name}: {time_taken:.3f}s")
        else:
            print("  所有组件启动时间正常 (<0.5s)")
        
        print("="*60)
    
    def get_backend_config(self):
        """
        获取后端配置
        """
        try:
            from backend.config import settings
            from backend.middleware import RequestLoggingMiddleware
            from backend.api import router as api_router
            
            return {
                'settings': settings,
                'middleware': RequestLoggingMiddleware,
                'api_router': api_router
            }
        except ImportError as e:
            print(f"❌ 无法导入后端配置: {e}")
            return None

    def get_backend_performance_metrics(self):
        """
        获取后端性能指标
        """
        try:
            # 获取后端配置
            from backend.config import settings
            from backend.middleware import RequestLoggingMiddleware
            from backend.api import router as api_router
            
            # 返回性能指标
            return {
                'config_loaded': True,
                'middleware_count': len(getattr(RequestLoggingMiddleware, '__dict__', {})),
                'api_routes_count': len(api_router.routes),
                'debug_mode': settings.DEBUG if hasattr(settings, 'DEBUG') else False
            }
        except ImportError as e:
            print(f"❌ 无法获取后端性能指标: {e}")
            return {'config_loaded': False, 'error': str(e)}

    def calculate_backend_startup_time(self):
        """
        计算后端启动时间
        """
        try:
            import time
            from backend.config import settings
            from backend.middleware import RequestLoggingMiddleware
            from backend.api import router as api_router

            start_time = time.time()
                
            # 引入更多组件以测试加载性能
            from backend.core.config import settings as core_settings
            from backend.database import engine, SessionLocal
            from backend.models import Base
            from backend.schemas.response import UnifiedResponse
            from backend.api.v1.matches import router as matches_router
            from backend.api.v1.auth import router as auth_router
                
                end_time = time.time()
                startup_time = (end_time - start_time) * 1000
                
                return {
                    'startup_time_ms': startup_time,
                    'components_loaded': True,
                    'timestamp': datetime.now().isoformat()
                }
            except ImportError as e:
                print(f"❌ 无法计算后端启动时间: {e}")
                return {'components_loaded': False, 'error': str(e)}

    def get_component_loading_times(self):
        """
        获取各组件加载时间
        """
        import time
            
        times = {}
            
        # 测试配置加载时间
        start_time = time.time()
        try:
            from backend.config import settings
            from backend.middleware import RequestLoggingMiddleware
            from backend.api import router as api_router
            end_time = time.time()
            times['config'] = (end_time - start_time) * 1000
        except ImportError as e:
            times['config'] = f"Error: {e}"
            
        # 测试数据库组件加载时间
        start_time = time.time()
        try:
            from backend.database import engine, SessionLocal
            from backend.models import Base
            end_time = time.time()
            times['database'] = (end_time - start_time) * 1000
        except ImportError as e:
            times['database'] = f"Error: {e}"
            
        # 测试核心服务加载时间
        start_time = time.time()
        try:
            from backend.core.config import settings as core_settings
            from backend.core.security import get_password_hash
            from backend.schemas.response import UnifiedResponse
            from backend.api.v1.matches import router as matches_router
            end_time = time.time()
            times['core_services'] = (end_time - start_time) * 1000
        except ImportError as e:
            times['core_services'] = f"Error: {e}"
            
        return times

    def run_monitoring_cycle(self):
        """
        执行监控周期
        """
        while self.monitoring_active:
            # 获取性能指标
            metrics = self.get_backend_performance_metrics()
            loading_times = self.get_component_loading_times()
            
            # 打印指标
            print(f"\n📊 性能监控指标:")
            print(f"   配置加载时间: {loading_times.get('config', 'N/A')}ms")
            print(f"   数据库组件加载时间: {loading_times.get('database', 'N/A')}ms")
            print(f"   核心服务加载时间: {loading_times.get('core_services', 'N/A')}ms")
            print(f"   组件加载状态: {metrics.get('config_loaded', 'N/A')}")
            
            # 等待下一个周期
            time.sleep(self.interval)

        def analyze_backend_performance(self):
            """
            分析后端性能瓶颈
            """
            try:
                import time
                
                analysis_results = {}
                
                # 测量配置加载时间
                start_time = time.time()
                from backend.config import settings
                end_time = time.time()
                analysis_results['config_load_time'] = (end_time - start_time) * 1000
                
                # 测量中间件加载时间
                start_time = time.time()
                from backend.middleware import RequestLoggingMiddleware
                end_time = time.time()
                analysis_results['middleware_load_time'] = (end_time - start_time) * 1000
                
                # 测量API路由加载时间
                start_time = time.time()
                from backend.api import router as api_router
                end_time = time.time()
                analysis_results['api_router_load_time'] = (end_time - start_time) * 1000
                
                # 测量数据库连接建立时间
                start_time = time.time()
                from backend.database import engine
                end_time = time.time()
                analysis_results['db_connection_time'] = (end_time - start_time) * 1000
                
                # 综合分析
                total_load_time = sum(analysis_results.values())
                
                return {
                    'analysis_results': analysis_results,
                    'total_load_time_ms': total_load_time,
                    'recommendations': self.generate_recommendations(analysis_results)
                }
            except ImportError as e:
                print(f"❌ 无法分析后端性能: {e}")
                return {'analysis_error': str(e)}

def create_app_with_monitoring():
    """使用性能监控创建应用"""
    monitor = PerformanceMonitor()
    
    with monitor.measure("导入FastAPI"):
        from fastapi import FastAPI
        from fastapi.staticfiles import StaticFiles
        from fastapi.middleware.cors import CORSMiddleware
        from contextlib import asynccontextmanager
        import logging
        import os
    
    with monitor.measure("导入配置"):
        from backend.config import settings
    
    with monitor.measure("导入中间件"):
        from backend.middleware import RequestLoggingMiddleware
    
    with monitor.measure("导入API路由"):
        from backend.api import router as api_router
    
    with monitor.measure("创建FastAPI应用"):
        app = FastAPI(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            description=settings.DESCRIPTION,
            openapi_url=f"{settings.API_V1_STR}/openapi.json",
            docs_url="/docs" if settings.DOCS_ENABLED else None,
            redoc_url="/redoc" if settings.DOCS_ENABLED else None,
        )
    
    with monitor.measure("配置CORS中间件"):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    with monitor.measure("添加自定义中间件"):
        app.add_middleware(RequestLoggingMiddleware)
    
    with monitor.measure("挂载静态文件"):
        static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        app.mount("/jczq", StaticFiles(directory=static_dir, html=True), name="jczq")
    
    with monitor.measure("包含API路由"):
        app.include_router(api_router, prefix=settings.API_V1_STR)
    
    with monitor.measure("添加根路径路由"):
        @app.get("/")
        async def root():
            """根路径返回欢迎信息"""
            return {"message": "Welcome to Sport Lottery Sweeper API"}
    
    # 输出性能报告
    monitor.report()
    
    return app


if __name__ == "__main__":
    app = create_app_with_monitoring()
    
    print("\n启动Uvicorn服务器...")
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8007,
        log_level="info"
    )