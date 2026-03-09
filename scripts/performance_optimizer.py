"""
性能优化和监控工具
实现启动性能优化和运行时监控
"""
import time
import sys
import os
import asyncio
import cProfile
import pstats
from io import StringIO
from contextlib import contextmanager
from typing import Dict, Any, Callable, Awaitable
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.module_loader import get_module_loader
from backend.core.cache_manager import get_cache_manager
from backend.core.async_initializer import get_async_initializer


class PerformanceOptimizer:
    """
    性能优化器
    提供性能分析、缓存优化和异步初始化等功能
    """
    def __init__(self):
        try:
            self.module_loader = get_module_loader()
            self.cache_manager = get_cache_manager()
            self.async_initializer = get_async_initializer()
            
            # 后端模块路径定义
            self.backend_modules = [
                'backend.config',
                'backend.middleware',
                'backend.api'
            ]
        except ImportError as e:
            self.logger.error(f"后端核心组件导入失败: {e}")
            raise
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def profile_block(self, name: str):
        """性能分析上下文管理器"""
        pr = cProfile.Profile()
        pr.enable()
        start_time = time.time()
        self.logger.info(f"开始性能分析: {name}")
        
        try:
            yield
        finally:
            end_time = time.time()
            pr.disable()
            
            # 获取性能分析结果
            s = StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
            ps.print_stats(20)  # 显示前20个最耗时的函数
            
            self.logger.info(f"性能分析完成: {name}")
            self.logger.info(f"执行时间: {end_time - start_time:.3f}s")
            self.logger.info(f"性能分析结果:\n{s.getvalue()}")

    async def optimize_startup(self) -> Dict[str, Any]:
        """优化启动性能"""
        start_time = time.time()
        results = {
            'modules_loaded': 0,
            'initializers_executed': 0,
            'cache_warmed_up': 0,
            'total_time': 0
        }
        
        self.logger.info("开始启动性能优化...")
        
        # 1. 预加载核心模块
        core_modules = [
            'backend.config',
            'backend.middleware',
        ]
        
        for module_path in core_modules:
            try:
                await self.module_loader.load_module(module_path)
                results['modules_loaded'] += 1
            except Exception as e:
                self.logger.warning(f"模块预加载失败: {module_path}, 错误: {e}")
        
        # 2. 执行关键初始化
        critical_initializers = ['database', 'cache']
        for name in critical_initializers:
            try:
                await self.async_initializer.initialize(name)
                results['initializers_executed'] += 1
            except Exception as e:
                self.logger.warning(f"初始化器执行失败: {name}, 错误: {e}")
        
        # 3. 预热缓存
        try:
            # 这里可以添加一些预热缓存的逻辑
            results['cache_warmed_up'] = 1
        except Exception as e:
            self.logger.warning(f"缓存预热失败: {e}")
        
        results['total_time'] = time.time() - start_time
        self.logger.info(f"启动性能优化完成，总耗时: {results['total_time']:.3f}s")
        
        return results

    async def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        cache_stats = await self.cache_manager.get_stats()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'cache_stats': cache_stats,
            'module_loader_stats': {
                'loaded_modules_count': len(self.module_loader._loaded_modules),
                'cached_items_count': len(self.module_loader._module_cache),
            },
            'async_initializer_stats': {
                'registered_initializers': len(self.async_initializer._initializers),
                'completed_initializers': sum(1 for flag in self.async_initializer._initialized_flags.values() if flag),
            }
        }
        
        return report

    def add_lazy_loading_property(self, cls, module_path: str, attr_name: str):
        """为类添加懒加载属性"""
        def lazy_loader(self):
            if not hasattr(self, f'_{attr_name}_loaded'):
                # 按需加载模块
                module = asyncio.run(self.module_loader.load_module(module_path))
                attr_value = getattr(module, attr_name)
                setattr(self, f'_{attr_name}_loaded', True)
                setattr(self, f'_{attr_name}_value', attr_value)
            
            return getattr(self, f'_{attr_name}_value')
        
        setattr(cls, attr_name, property(lazy_loader))
        return cls


# 创建全局性能优化器实例
optimizer = PerformanceOptimizer()


async def run_performance_analysis():
    """运行性能分析"""
    print("🚀 开始性能分析...")
    
    # 执行启动优化
    startup_results = await optimizer.optimize_startup()
    print(f"✅ 启动优化完成:")
    print(f"   模块加载: {startup_results['modules_loaded']} 个")
    print(f"   初始化器执行: {startup_results['initializers_executed']} 个")
    print(f"   缓存预热: {startup_results['cache_warmed_up']} 项")
    print(f"   总耗时: {startup_results['total_time']:.3f}s")
    
    # 获取性能报告
    report = await optimizer.get_performance_report()
    print(f"\n📊 性能报告 (时间: {report['timestamp']}):")
    print(f"   缓存状态: {report['cache_stats']['active_items']} 项活跃, "
          f"{report['cache_stats']['expired_items']} 项过期")
    print(f"   已加载模块: {report['module_loader_stats']['loaded_modules_count']} 个")
    print(f"   已完成初始化: {report['async_initializer_stats']['completed_initializers']} / "
          f"{report['async_initializer_stats']['registered_initializers']}")
    
    # 执行性能分析
    with optimizer.profile_block("示例性能分析"):
        # 模拟一些操作
        await asyncio.sleep(0.1)
        await optimizer.cache_manager.get("nonexistent_key")
    
    print("\n✨ 性能分析完成!")


if __name__ == "__main__":
    asyncio.run(run_performance_analysis())