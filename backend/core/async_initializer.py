"""
异步初始化管理器
管理应用启动时的异步初始化任务
"""
import asyncio
import logging
from typing import Dict, Callable, Any, Awaitable
from datetime import datetime


class AsyncInitializer:
    """
    异步初始化管理器
    管理应用启动时的异步初始化任务
    """
    def __init__(self):
        self._initializers: Dict[str, Callable[[], Awaitable[Any]]] = {}
        self._initialized_flags: Dict[str, bool] = {}
        self._results: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    def register(self, name: str, initializer: Callable[[], Awaitable[Any]]):
        """注册异步初始化器"""
        self._initializers[name] = initializer
        self._initialized_flags[name] = False
        self.logger.info(f"注册异步初始化器: {name}")

    async def initialize(self, name: str, force: bool = False) -> Any:
        """执行指定的初始化器"""
        if not force and self._initialized_flags.get(name, False):
            self.logger.debug(f"初始化器已执行，跳过: {name}")
            return self._results.get(name)

        if name not in self._initializers:
            raise ValueError(f"未找到初始化器: {name}")

        self.logger.info(f"开始执行初始化器: {name}")
        start_time = datetime.now()

        try:
            result = await self._initializers[name]()
            duration = (datetime.now() - start_time).total_seconds()
            
            self._results[name] = result
            self._initialized_flags[name] = True
            
            self.logger.info(f"初始化器完成: {name}, 耗时: {duration:.2f}s")
            return result
        except Exception as e:
            self.logger.error(f"初始化器执行失败: {name}, 错误: {e}")
            raise

    async def initialize_all(self) -> Dict[str, Any]:
        """执行所有初始化器"""
        results = {}
        for name in self._initializers:
            try:
                results[name] = await self.initialize(name)
            except Exception as e:
                self.logger.error(f"初始化器 {name} 执行失败: {e}")
                results[name] = None
        return results

    def is_initialized(self, name: str) -> bool:
        """检查指定初始化器是否已完成"""
        return self._initialized_flags.get(name, False)

    async def reset(self, name: str = None):
        """重置初始化状态"""
        if name:
            self._initialized_flags[name] = False
            if name in self._results:
                del self._results[name]
            self.logger.info(f"重置初始化器状态: {name}")
        else:
            for key in self._initialized_flags:
                self._initialized_flags[key] = False
            self._results.clear()
            self.logger.info("重置所有初始化器状态")


# 创建全局异步初始化器实例
async_initializer = AsyncInitializer()


def get_async_initializer() -> AsyncInitializer:
    """获取异步初始化器实例"""
    return async_initializer


# 定义常用的初始化任务
async def init_database():
    """初始化数据库连接"""
    # 这里应该是实际的数据库初始化逻辑
    await asyncio.sleep(0.1)  # 模拟异步操作
    return {"status": "database_connected", "connection_pool_size": 10}


async def init_cache():
    """初始化缓存系统"""
    # 这里应该是实际的缓存初始化逻辑
    await asyncio.sleep(0.05)  # 模拟异步操作
    return {"status": "cache_ready", "size": "1GB"}


async def init_external_apis():
    """初始化外部API连接"""
    # 这里应该是实际的外部API初始化逻辑
    await asyncio.sleep(0.15)  # 模拟异步操作
    return {"status": "apis_connected", "count": 3}


# 注册默认的初始化器
async_initializer.register("database", init_database)
async_initializer.register("cache", init_cache)
async_initializer.register("external_apis", init_external_apis)