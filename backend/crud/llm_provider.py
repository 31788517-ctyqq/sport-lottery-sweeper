"""
LLM供应商CRUD操作
"""
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_, func, desc, asc
from datetime import datetime

from backend.models.llm_provider import LLMProvider, LLMProviderTypeEnum, LLMProviderStatusEnum
from backend.schemas.llm_provider import LLMProviderCreate, LLMProviderUpdate
from backend.core.security import encrypt_sensitive_data, decrypt_sensitive_data
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class CRUDLLMProvider:
    """LLM供应商CRUD操作类"""
    
    def __init__(self, model: LLMProvider = LLMProvider):
        self.model = model
    
    def get(self, db: Session, provider_id: int) -> Optional[LLMProvider]:
        """根据ID获取供应商"""
        try:
            return db.query(self.model).filter(self.model.id == provider_id).first()
        except Exception as e:
            logger.error(f"获取LLM供应商失败: {e}")
            return None
    
    def get_by_name(self, db: Session, name: str) -> Optional[LLMProvider]:
        """根据名称获取供应商"""
        try:
            return db.query(self.model).filter(self.model.name == name).first()
        except Exception as e:
            logger.error(f"根据名称获取LLM供应商失败: {e}")
            return None
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        enabled: Optional[bool] = None,
        provider_type: Optional[LLMProviderTypeEnum] = None,
        health_status: Optional[LLMProviderStatusEnum] = None,
        search: Optional[str] = None,
        order_by: str = "priority",
        order_desc: bool = False
    ) -> List[LLMProvider]:
        """获取供应商列表"""
        try:
            query = db.query(self.model)
            
            # 应用过滤条件
            if enabled is not None:
                query = query.filter(self.model.enabled == enabled)
            if provider_type is not None:
                query = query.filter(self.model.provider_type == provider_type)
            if health_status is not None:
                query = query.filter(self.model.health_status == health_status)
            if search:
                query = query.filter(or_(
                    self.model.name.contains(search),
                    self.model.description.contains(search)
                ))
            
            # 应用排序
            if hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))
            else:
                # 默认按优先级排序
                if order_desc:
                    query = query.order_by(desc(self.model.priority))
                else:
                    query = query.order_by(asc(self.model.priority))
            
            # 应用分页
            if limit > 0:
                query = query.offset(skip).limit(limit)
            
            # 调试：打印SQL查询
            logger.info(f"Executing query: {query}")
            
            result = query.all()
            logger.info(f"Query returned {len(result)} results")
            return result
        except Exception as e:
            logger.error(f"获取LLM供应商列表失败: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def get_count(
        self,
        db: Session,
        *,
        enabled: Optional[bool] = None,
        provider_type: Optional[LLMProviderTypeEnum] = None,
        health_status: Optional[LLMProviderStatusEnum] = None,
        search: Optional[str] = None
    ) -> int:
        """获取供应商数量"""
        try:
            query = db.query(func.count(self.model.id))
            
            # 应用相同的过滤条件
            if enabled is not None:
                query = query.filter(self.model.enabled == enabled)
            if provider_type is not None:
                query = query.filter(self.model.provider_type == provider_type)
            if health_status is not None:
                query = query.filter(self.model.health_status == health_status)
            if search:
                query = query.filter(or_(
                    self.model.name.contains(search),
                    self.model.description.contains(search)
                ))
            
            return query.scalar() or 0
        except Exception as e:
            logger.error(f"获取LLM供应商数量失败: {e}")
            return 0
    
    def create(self, db: Session, *, obj_in: LLMProviderCreate, created_by: Optional[int] = None) -> Optional[LLMProvider]:
        """创建新供应商"""
        try:
            # 检查名称是否已存在
            existing = self.get_by_name(db, obj_in.name)
            if existing:
                logger.warning(f"LLM供应商名称已存在: {obj_in.name}")
                return None
            
            # 加密API密钥
            encrypted_api_key = self._encrypt_api_key(obj_in.api_key)
            
            # 创建数据库对象
            # 将Pydantic枚举转换为SQLAlchemy模型枚举
            logger.info(f"原始provider_type: {obj_in.provider_type}, 类型: {type(obj_in.provider_type)}, name: {obj_in.provider_type.name}, value: {obj_in.provider_type.value}")
            # 通过名称映射到SQLAlchemy枚举成员
            try:
                provider_type = LLMProviderTypeEnum[obj_in.provider_type.name]
                logger.info(f"通过名称映射后provider_type: {provider_type}, 类型: {type(provider_type)}, name: {provider_type.name}, value: {provider_type.value}")
            except KeyError:
                # 如果名称不匹配，尝试通过值查找
                logger.warning(f"名称 {obj_in.provider_type.name} 不在SQLAlchemy枚举中，尝试通过值查找")
                provider_type = LLMProviderTypeEnum(obj_in.provider_type.value)
                logger.info(f"通过值查找后provider_type: {provider_type}, 类型: {type(provider_type)}")
                
            db_obj = self.model(
                name=obj_in.name,
                provider_type=provider_type,
                description=obj_in.description,
                api_key=encrypted_api_key,
                base_url=obj_in.base_url,
                default_model=obj_in.default_model,
                available_models=obj_in.available_models or [],
                enabled=obj_in.enabled,
                priority=obj_in.priority,
                max_requests_per_minute=obj_in.max_requests_per_minute,
                timeout_seconds=obj_in.timeout_seconds,
                cost_per_token=obj_in.cost_per_token or {},
                rate_limit_strategy=obj_in.rate_limit_strategy,
                retry_policy=obj_in.retry_policy or {},
                circuit_breaker_config=obj_in.circuit_breaker_config or {},
                version=obj_in.version,
                tags=obj_in.tags or [],
                created_by=created_by,
                updated_by=created_by
            )
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            logger.info(f"LLM供应商创建成功: {db_obj.name} (ID: {db_obj.id})")
            return db_obj
        except Exception as e:
            db.rollback()
            import traceback
            logger.error(f"创建LLM供应商失败: {e}")
            logger.error(f"堆栈跟踪: {traceback.format_exc()}")
            return None
    
    def update(
        self, 
        db: Session, 
        *, 
        db_obj: LLMProvider, 
        obj_in: Union[LLMProviderUpdate, Dict[str, Any]],
        updated_by: Optional[int] = None
    ) -> Optional[LLMProvider]:
        """更新供应商信息"""
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            
            # 如果更新名称，检查是否与其他供应商冲突
            if "name" in update_data and update_data["name"] != db_obj.name:
                existing = self.get_by_name(db, update_data["name"])
                if existing and existing.id != db_obj.id:
                    logger.warning(f"LLM供应商名称已存在: {update_data['name']}")
                    return None
            
            # 如果更新API密钥，进行加密
            if "api_key" in update_data:
                update_data["api_key"] = self._encrypt_api_key(update_data["api_key"])
            
            # 更新字段
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    # 特殊处理枚举字段转换
                    if field == 'provider_type':
                        if hasattr(value, 'name') and hasattr(value, 'value'):
                            # Pydantic枚举实例
                            try:
                                # 通过名称映射到SQLAlchemy枚举成员
                                value = LLMProviderTypeEnum[value.name]
                            except KeyError:
                                # 如果名称不匹配，尝试通过值查找
                                value = LLMProviderTypeEnum(value.value)
                        elif isinstance(value, str):
                            # 字符串值，尝试通过值查找
                            value = LLMProviderTypeEnum(value)
                    elif field == 'health_status':
                        if hasattr(value, 'name') and hasattr(value, 'value'):
                            # Pydantic枚举实例
                            try:
                                value = LLMProviderStatusEnum[value.name]
                            except KeyError:
                                value = LLMProviderStatusEnum(value.value)
                        elif isinstance(value, str):
                            value = LLMProviderStatusEnum(value)
                    setattr(db_obj, field, value)
            
            # 更新审计信息
            if updated_by:
                db_obj.updated_by = updated_by
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            logger.info(f"LLM供应商更新成功: {db_obj.name} (ID: {db_obj.id})")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"更新LLM供应商失败: {e}")
            return None
    
    def delete(self, db: Session, *, provider_id: int) -> bool:
        """删除供应商"""
        try:
            db_obj = self.get(db, provider_id)
            if not db_obj:
                logger.warning(f"要删除的LLM供应商不存在: {provider_id}")
                return False
            
            db.delete(db_obj)
            db.commit()
            
            logger.info(f"LLM供应商删除成功: {db_obj.name} (ID: {provider_id})")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"删除LLM供应商失败: {e}")
            return False
    
    def enable(self, db: Session, *, provider_id: int) -> bool:
        """启用供应商"""
        try:
            db_obj = self.get(db, provider_id)
            if not db_obj:
                return False
            
            db_obj.enabled = True
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            logger.info(f"LLM供应商已启用: {db_obj.name} (ID: {provider_id})")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"启用LLM供应商失败: {e}")
            return False
    
    def disable(self, db: Session, *, provider_id: int) -> bool:
        """禁用供应商"""
        try:
            db_obj = self.get(db, provider_id)
            if not db_obj:
                return False
            
            db_obj.enabled = False
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            logger.info(f"LLM供应商已禁用: {db_obj.name} (ID: {provider_id})")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"禁用LLM供应商失败: {e}")
            return False
    
    def update_health_status(
        self, 
        db: Session, 
        *, 
        provider_id: int, 
        is_healthy: bool,
        response_time_ms: Optional[int] = None
    ) -> bool:
        """更新供应商健康状态"""
        try:
            db_obj = self.get(db, provider_id)
            if not db_obj:
                return False
            
            from datetime import datetime
            db_obj.last_checked_at = datetime.utcnow()
            
            if is_healthy:
                db_obj.health_status = LLMProviderStatusEnum.HEALTHY
                db_obj.last_success_at = datetime.utcnow()
                db_obj.successful_requests += 1
            else:
                db_obj.health_status = LLMProviderStatusEnum.UNHEALTHY
                db_obj.failed_requests += 1
            
            db_obj.total_requests += 1
            db_obj.updated_at = datetime.utcnow()
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            logger.info(f"LLM供应商健康状态更新: {db_obj.name} -> {'健康' if is_healthy else '不健康'}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"更新LLM供应商健康状态失败: {e}")
            return False
    
    def increment_cost(
        self,
        db: Session,
        *,
        provider_id: int,
        cost_cents: int  # 成本（分）
    ) -> bool:
        """增加供应商成本"""
        try:
            db_obj = self.get(db, provider_id)
            if not db_obj:
                return False
            
            db_obj.total_cost += cost_cents
            db_obj.monthly_cost += cost_cents
            db_obj.updated_at = datetime.utcnow()
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"增加LLM供应商成本失败: {e}")
            return False
    
    def get_available_providers(
        self,
        db: Session,
        *,
        provider_type: Optional[LLMProviderTypeEnum] = None,
        min_priority: int = 1,
        max_priority: int = 10
    ) -> List[LLMProvider]:
        """获取可用的供应商（启用且健康）"""
        try:
            query = db.query(self.model).filter(
                self.model.enabled == True,
                self.model.health_status == LLMProviderStatusEnum.HEALTHY,
                self.model.priority >= min_priority,
                self.model.priority <= max_priority
            )
            
            if provider_type is not None:
                query = query.filter(self.model.provider_type == provider_type)
            
            # 按优先级升序排序（优先级值越小越优先）
            query = query.order_by(asc(self.model.priority))
            
            return query.all()
        except Exception as e:
            logger.error(f"获取可用LLM供应商失败: {e}")
            return []
    
    def get_stats(self, db: Session) -> Dict[str, Any]:
        """获取供应商统计信息"""
        try:
            total = self.get_count(db)
            enabled = self.get_count(db, enabled=True)
            
            # 获取健康供应商数量
            healthy_count = db.query(func.count(self.model.id)).filter(
                self.model.enabled == True,
                self.model.health_status == LLMProviderStatusEnum.HEALTHY
            ).scalar() or 0
            
            # 获取总请求数和成本
            total_requests = db.query(func.sum(self.model.total_requests)).scalar() or 0
            total_cost = db.query(func.sum(self.model.total_cost)).scalar() or 0
            monthly_cost = db.query(func.sum(self.model.monthly_cost)).scalar() or 0
            
            # 按类型统计
            type_stats = {}
            for provider_type in LLMProviderTypeEnum:
                count = self.get_count(db, provider_type=provider_type)
                if count > 0:
                    type_stats[provider_type.value] = count
            
            return {
                "total_providers": total,
                "enabled_providers": enabled,
                "healthy_providers": healthy_count,
                "total_requests": total_requests,
                "total_cost": total_cost / 100.0,  # 转换为元
                "monthly_cost": monthly_cost / 100.0,  # 转换为元
                "type_stats": type_stats
            }
        except Exception as e:
            logger.error(f"获取LLM供应商统计信息失败: {e}")
            return {}
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """加密API密钥"""
        try:
            # 使用系统密钥加密
            key = settings.SECRET_KEY.encode()[:32].ljust(32, b'0')[:32]
            encrypted = encrypt_sensitive_data(api_key, key)
            return encrypted
        except Exception as e:
            logger.error(f"加密API密钥失败: {e}")
            # 如果加密失败，返回原始密钥（不推荐）
            return api_key
    
    def _decrypt_api_key(self, encrypted_api_key: str) -> str:
        """解密API密钥"""
        try:
            key = settings.SECRET_KEY.encode()[:32].ljust(32, b'0')[:32]
            decrypted = decrypt_sensitive_data(encrypted_api_key, key)
            return decrypted
        except Exception as e:
            logger.error(f"解密API密钥失败: {e}")
            # 如果解密失败，返回原始值
            return encrypted_api_key
    
    def get_decrypted_api_key(self, db: Session, provider_id: int) -> Optional[str]:
        """获取解密后的API密钥"""
        try:
            db_obj = self.get(db, provider_id)
            if not db_obj:
                return None
            
            return self._decrypt_api_key(db_obj.api_key)
        except Exception as e:
            logger.error(f"获取解密API密钥失败: {e}")
            return None


# 创建CRUD实例
llm_provider = CRUDLLMProvider()