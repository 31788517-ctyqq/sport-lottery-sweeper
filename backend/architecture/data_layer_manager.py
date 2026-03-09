#!/usr/bin/env python3
"""
数据分层架构管理器
实现数据访问层、业务逻辑层、缓存层的统一管理
支持读写分离、数据分片、冷热数据分离
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Type
from datetime import datetime, timedelta
from enum import Enum
from contextlib import contextmanager
import asyncio
import aioredis
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

from backend.database import get_db, get_read_db
from backend.core.config import settings
from backend.services.unified_user_manager import unified_user_manager

# 配置日志
logger = logging.getLogger(__name__)

class DataLayer(Enum):
    """数据层级枚举"""
    HOT_DATA = "hot"          # 热数据层（频繁访问）
    WARM_DATA = "warm"         # 温数据层（偶尔访问）
    COLD_DATA = "cold"         # 冷数据层（很少访问）
    ARCHIVE_DATA = "archive"   # 归档数据层（历史数据）

class DataAccessPattern(Enum):
    """数据访问模式枚举"""
    READ_HEAVY = "read_heavy"      # 读多写少
    WRITE_HEAVY = "write_heavy"    # 写多读少
    BALANCED = "balanced"          # 读写均衡
    REAL_TIME = "real_time"        # 实时性要求高

class CacheStrategy(Enum):
    """缓存策略枚举"""
    NONE = "none"              # 不缓存
    LRU = "lru"                # 最近最少使用
    LFU = "lfu"                # 最不经常使用
    TTL = "ttl"                # 时间生存
    WRITE_THROUGH = "write_through"  # 写穿透
    WRITE_BACK = "write_back"      # 写回

class DataShardingStrategy(Enum):
    """数据分片策略枚举"""
    HASH = "hash"              # 哈希分片
    RANGE = "range"            # 范围分片
    LIST = "list"              # 列表分片
    GEOGRAPHIC = "geographic"  # 地理分片

class BaseDataRepository(ABC):
    """数据仓储基类"""
    
    def __init__(self, layer: DataLayer = DataLayer.HOT_DATA):
        self.layer = layer
        self.cache_strategy = CacheStrategy.TTL
        self.access_pattern = DataAccessPattern.BALANCED
        self.cache_ttl = 3600  # 默认1小时
        
    @abstractmethod
    async def get_by_id(self, entity_id: Union[int, str]) -> Optional[Any]:
        """根据ID获取数据"""
        pass
    
    @abstractmethod
    async def list(self, filters: Dict = None, limit: int = 100, offset: int = 0) -> List[Any]:
        """列表查询"""
        pass
    
    @abstractmethod
    async def create(self, data: Dict) -> Any:
        """创建数据"""
        pass
    
    @abstractmethod
    async def update(self, entity_id: Union[int, str], data: Dict) -> bool:
        """更新数据"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: Union[int, str]) -> bool:
        """删除数据"""
        pass

class HotDataRepository(BaseDataRepository):
    """热数据仓储 - 处理频繁访问的数据"""
    
    def __init__(self):
        super().__init__(DataLayer.HOT_DATA)
        self.cache_ttl = 1800  # 30分钟
        self.cache_strategy = CacheStrategy.WRITE_THROUGH
        self.access_pattern = DataAccessPattern.READ_HEAVY
        
    async def get_by_id(self, entity_id: Union[int, str]) -> Optional[Any]:
        """从热数据层获取，优先使用缓存"""
        cache_key = f"hot:{self.__class__.__name__}:{entity_id}"
        
        # 尝试从缓存获取
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for {cache_key}")
            return cached_data
        
        # 缓存未命中，从数据库获取
        with unified_user_manager.get_db_session() as db:
            data = await self._fetch_from_hot_db(db, entity_id)
            
        if data:
            # 写入缓存
            await self._set_to_cache(cache_key, data, self.cache_ttl)
            
        return data
    
    async def list(self, filters: Dict = None, limit: int = 100, offset: int = 0) -> List[Any]:
        """热数据列表查询，使用优化的索引"""
        cache_key = f"hot_list:{self.__class__.__name__}:{hash(str(filters))}:{limit}:{offset}"
        
        # 尝试缓存
        cached_result = await self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # 数据库查询
        with unified_user_manager.get_db_session() as db:
            result = await self._fetch_list_from_hot_db(db, filters, limit, offset)
            
        # 缓存结果
        if result:
            await self._set_to_cache(cache_key, result, self.cache_ttl // 2)
            
        return result
    
    async def create(self, data: Dict) -> Any:
        """创建热数据，立即更新缓存"""
        with unified_user_manager.get_db_session() as db:
            result = await self._insert_to_hot_db(db, data)
            
        # 写穿透：同时更新缓存
        if result and hasattr(result, 'id'):
            cache_key = f"hot:{self.__class__.__name__}:{result.id}"
            await self._set_to_cache(cache_key, result, self.cache_ttl)
            
        return result
    
    async def update(self, entity_id: Union[int, str], data: Dict) -> bool:
        """更新热数据，失效相关缓存"""
        with unified_user_manager.get_db_session() as db:
            success = await self._update_hot_db(db, entity_id, data)
            
        if success:
            # 失效缓存
            cache_key = f"hot:{self.__class__.__name__}:{entity_id}"
            await self._delete_from_cache(cache_key)
            
            # 失效相关列表缓存
            await self._invalidate_list_caches()
            
        return success
    
    async def delete(self, entity_id: Union[int, str]) -> bool:
        """删除热数据，清理缓存"""
        with unified_user_manager.get_db_session() as db:
            success = await self._delete_from_hot_db(db, entity_id)
            
        if success:
            cache_key = f"hot:{self.__class__.__name__}:{entity_id}"
            await self._delete_from_cache(cache_key)
            await self._invalidate_list_caches()
            
        return success
    
    # 抽象方法 - 子类实现具体的数据访问逻辑
    @abstractmethod
    async def _fetch_from_hot_db(self, db: Session, entity_id: Union[int, str]) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def _fetch_list_from_hot_db(self, db: Session, filters: Dict, limit: int, offset: int) -> List[Any]:
        pass
    
    @abstractmethod
    async def _insert_to_hot_db(self, db: Session, data: Dict) -> Any:
        pass
    
    @abstractmethod
    async def _update_hot_db(self, db: Session, entity_id: Union[int, str], data: Dict) -> bool:
        pass
    
    @abstractmethod
    async def _delete_from_hot_db(self, db: Session, entity_id: Union[int, str]) -> bool:
        pass
    
    # 缓存操作方法
    async def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        try:
            if hasattr(self, '_redis_client'):
                cached = await self._redis_client.get(key)
                if cached:
                    return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get failed for {key}: {e}")
        return None
    
    async def _set_to_cache(self, key: str, value: Any, ttl: int):
        """设置缓存"""
        try:
            if hasattr(self, '_redis_client'):
                await self._redis_client.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.warning(f"Cache set failed for {key}: {e}")
    
    async def _delete_from_cache(self, key: str):
        """删除缓存"""
        try:
            if hasattr(self, '_redis_client'):
                await self._redis_client.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete failed for {key}: {e}")
    
    async def _invalidate_list_caches(self):
        """失效列表缓存"""
        try:
            if hasattr(self, '_redis_client'):
                # 使用通配符删除相关的列表缓存
                pattern = f"hot_list:{self.__class__.__name__}:*"
                keys = await self._redis_client.keys(pattern)
                if keys:
                    await self._redis_client.delete(*keys)
        except Exception as e:
            logger.warning(f"List cache invalidation failed: {e}")

class WarmDataRepository(BaseDataRepository):
    """温数据仓储 - 处理中等频率访问的数据"""
    
    def __init__(self):
        super().__init__(DataLayer.WARM_DATA)
        self.cache_ttl = 7200  # 2小时
        self.cache_strategy = CacheStrategy.LRU
        self.access_pattern = DataAccessPattern.BALANCED
        
    async def get_by_id(self, entity_id: Union[int, str]) -> Optional[Any]:
        """温数据查询，适度使用缓存"""
        # 实现类似热数据，但缓存策略更保守
        cache_key = f"warm:{self.__class__.__name__}:{entity_id}"
        
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        with unified_user_manager.get_db_session() as db:
            data = await self._fetch_from_warm_db(db, entity_id)
            
        if data:
            await self._set_to_cache(cache_key, data, self.cache_ttl)
            
        return data
    
    # 其他方法实现... (类似热数据，但策略更保守)
    async def _fetch_from_warm_db(self, db: Session, entity_id: Union[int, str]) -> Optional[Any]:
        """从温数据存储获取"""
        pass
    
    async def _fetch_list_from_warm_db(self, db: Session, filters: Dict, limit: int, offset: int) -> List[Any]:
        """温数据列表查询"""
        pass
    
    async def _insert_to_warm_db(self, db: Session, data: Dict) -> Any:
        """插入温数据"""
        pass
    
    async def _update_warm_db(self, db: Session, entity_id: Union[int, str], data: Dict) -> bool:
        """更新温数据"""
        pass
    
    async def _delete_from_warm_db(self, db: Session, entity_id: Union[int, str]) -> bool:
        """删除温数据"""
        pass

class ColdDataRepository(BaseDataRepository):
    """冷数据仓储 - 处理很少访问的数据"""
    
    def __init__(self):
        super().__init__(DataLayer.COLD_DATA)
        self.cache_ttl = 86400  # 24小时
        self.cache_strategy = CacheStrategy.TTL
        self.access_pattern = DataAccessPattern.READ_HEAVY
        
    async def get_by_id(self, entity_id: Union[int, str]) -> Optional[Any]:
        """冷数据查询，主要依赖数据库"""
        # 冷数据很少缓存，直接查数据库
        with unified_user_manager.get_db_session() as db:
            return await self._fetch_from_cold_db(db, entity_id)
    
    # 冷数据方法实现... (最小缓存策略)
    async def _fetch_from_cold_db(self, db: Session, entity_id: Union[int, str]) -> Optional[Any]:
        """从冷数据存储获取"""
        pass

class ArchiveDataRepository(BaseDataRepository):
    """归档数据仓储 - 处理历史数据"""
    
    def __init__(self):
        super().__init__(DataLayer.ARCHIVE_DATA)
        self.cache_ttl = 604800  # 7天
        self.cache_strategy = CacheStrategy.NONE  # 归档数据不缓存
        self.access_pattern = DataAccessPattern.READ_HEAVY
        
    async def get_by_id(self, entity_id: Union[int, str]) -> Optional[Any]:
        """归档数据查询，直接从归档存储获取"""
        # 归档数据通常存储在专门的归档数据库或文件中
        return await self._fetch_from_archive_storage(entity_id)
    
    async def _fetch_from_archive_storage(self, entity_id: Union[int, str]) -> Optional[Any]:
        """从归档存储获取"""
        # 实现归档数据访问逻辑
        pass

class DataLayerManager:
    """数据分层架构管理器"""
    
    def __init__(self):
        self.repositories: Dict[str, BaseDataRepository] = {}
        self.redis_client = None
        self._initialized = False
        
    async def initialize(self):
        """初始化数据层管理器"""
        try:
            # 初始化Redis连接
            if settings.REDIS_URL:
                self.redis_client = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                
            # 注册各层数据仓库
            await self._register_repositories()
            
            self._initialized = True
            logger.info("数据分层架构管理器初始化完成")
            
        except Exception as e:
            logger.error(f"数据层管理器初始化失败: {e}")
            raise
    
    async def _register_repositories(self):
        """注册各层数据仓库"""
        # 这里注册具体的仓储实现
        # 例如：
        # self.repositories['user_hot'] = UserHotRepository()
        # self.repositories['user_warm'] = UserWarmRepository()
        # self.repositories['match_hot'] = MatchHotRepository()
        pass
    
    def get_repository(self, entity_type: str, layer: DataLayer = None) -> BaseDataRepository:
        """获取数据仓储"""
        if not self._initialized:
            raise RuntimeError("数据层管理器未初始化")
        
        # 如果没有指定层级，根据访问模式自动选择
        if layer is None:
            layer = self._determine_optimal_layer(entity_type)
        
        repo_key = f"{entity_type}_{layer.value}"
        return self.repositories.get(repo_key)
    
    def _determine_optimal_layer(self, entity_type: str) -> DataLayer:
        """根据实体类型确定最优数据层"""
        # 基于业务规则的层级选择逻辑
        hot_entities = ['user_session', 'match_live', 'intelligence_breaking']
        warm_entities = ['user_profile', 'match_recent', 'team_stats']
        cold_entities = ['user_history', 'match_old', 'analytics_monthly']
        archive_entities = ['user_archive', 'match_archive', 'logs_old']
        
        if entity_type in hot_entities:
            return DataLayer.HOT_DATA
        elif entity_type in warm_entities:
            return DataLayer.WARM_DATA
        elif entity_type in cold_entities:
            return DataLayer.COLD_DATA
        elif entity_type in archive_entities:
            return DataLayer.ARCHIVE_DATA
        else:
            return DataLayer.WARM_DATA  # 默认层级
    
    @contextmanager
    def get_transaction(self, layer: DataLayer = DataLayer.HOT_DATA):
        """事务上下文管理器"""
        # 根据数据层级选择合适的事务管理策略
        if layer == DataLayer.HOT_DATA:
            # 热数据使用强一致性事务
            with unified_user_manager.get_db_session() as db:
                yield db
        else:
            # 其他层级可以使用最终一致性
            with unified_user_manager.get_db_session() as db:
                yield db
    
    async def migrate_data(self, from_layer: DataLayer, to_layer: DataLayer, 
                          entity_type: str, criteria: Dict = None):
        """数据迁移 - 支持冷热数据分离"""
        """
        实现数据在不同层级间的迁移
        例如：将超过30天的比赛数据从热数据迁移到温数据
        """
        logger.info(f"开始数据迁移: {entity_type} 从 {from_layer} 到 {to_layer}")
        
        # 实现数据迁移逻辑
        # 1. 查询符合条件的源数据
        # 2. 批量读取并转换
        # 3. 写入目标层级
        # 4. 验证数据完整性
        # 5. 清理源数据（可选）
        
        pass
    
    async def sync_data_layers(self):
        """数据层同步 - 保持数据一致性"""
        """
        定期同步不同数据层级间的数据
        确保热点数据在各层保持一致
        """
        while True:
            try:
                # 同步热数据和温数据
                await self._sync_hot_to_warm()
                
                # 检查冷数据归档条件
                await self._check_cold_data_archival()
                
                # 等待下次同步
                await asyncio.sleep(300)  # 5分钟同步一次
                
            except Exception as e:
                logger.error(f"数据层同步失败: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟重试
    
    async def _sync_hot_to_warm(self):
        """同步热数据到温数据"""
        # 实现热->温数据同步逻辑
        pass
    
    async def _check_cold_data_archival(self):
        """检查冷数据归档条件"""
        # 实现冷数据归档检查逻辑
        pass

# 全局数据层管理器实例
data_layer_manager = DataLayerManager()