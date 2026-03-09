"""
模块按需加载器
实现延迟加载和缓存机制，优化启动性能
"""
import asyncio
import importlib
import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta


class ModuleLoader:
    """
    模块按需加载器
    实现延迟加载、缓存和异步初始化功能
    """
    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}
        self._module_cache: Dict[str, tuple] = {}  # (data, timestamp, ttl)
        self._initializers: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)

    def register_initializer(self, name: str, initializer: Callable):
        """注册异步初始化器"""
        self._initializers[name] = initializer

    async def load_module(self, module_path: str) -> Any:
        """按需加载模块"""
        if module_path in self._loaded_modules:
            return self._loaded_modules[module_path]

        try:
            self.logger.info(f"正在加载模块: {module_path}")
            module = importlib.import_module(module_path)
            self._loaded_modules[module_path] = module
            self.logger.info(f"模块加载成功: {module_path}")
            return module
        except ImportError as e:
            self.logger.error(f"模块加载失败: {module_path}, 错误: {e}")
            raise

    def get_cached_data(self, key: str, ttl_seconds: int = 300) -> Optional[Any]:
        """获取缓存数据"""
        if key in self._module_cache:
            data, timestamp, original_ttl = self._module_cache[key]
            if ttl_seconds <= 0 or (datetime.now() - timestamp).seconds < min(ttl_seconds, original_ttl):
                self.logger.debug(f"缓存命中: {key}")
                return data
            else:
                # 缓存过期，删除它
                del self._module_cache[key]
                self.logger.debug(f"缓存过期: {key}")
        
        return None

    def set_cached_data(self, key: str, data: Any, ttl_seconds: int = 300) -> None:
        """设置缓存数据"""
        self._module_cache[key] = (data, datetime.now(), ttl_seconds)
        self.logger.debug(f"缓存设置: {key}, TTL: {ttl_seconds}s")

    async def initialize_async(self, name: str):
        """异步初始化指定模块"""
        if name in self._initializers:
            self.logger.info(f"开始异步初始化: {name}")
            start_time = datetime.now()
            try:
                result = await self._initializers[name]()
                duration = (datetime.now() - start_time).total_seconds()
                self.logger.info(f"异步初始化完成: {name}, 耗时: {duration:.2f}s")
                return result
            except Exception as e:
                self.logger.error(f"异步初始化失败: {name}, 错误: {e}")
                raise
        else:
            self.logger.warning(f"未找到初始化器: {name}")
            return None

    def lazy_load_property(self, module_path: str, attr_name: str):
        """装饰器：懒加载属性"""
        def decorator(func):
            attr_key = f"{module_path}.{attr_name}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 检查是否已经加载
                if not hasattr(wrapper, '_loaded_value'):
                    # 按需加载模块
                    module = asyncio.run(self.load_module(module_path))
                    attr_value = getattr(module, attr_name)
                    setattr(wrapper, '_loaded_value', attr_value)
                
                return getattr(wrapper, '_loaded_value')
            
            return wrapper
        return decorator


# 创建全局模块加载器实例
loader = ModuleLoader()


def get_module_loader() -> ModuleLoader:
    """获取模块加载器实例"""
    return loader