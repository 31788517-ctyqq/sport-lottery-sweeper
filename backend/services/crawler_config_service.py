"""
爬虫配置服务
处理爬虫系统配置的CRUD操作
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.system_config import SystemConfig
from ..models.admin_user import AdminUser
from ..schemas.crawler_config import (
    CrawlerConfigCreate, CrawlerConfigUpdate, CrawlerConfigResponse
)
from .crawler_service import BaseCrawlerService


class CrawlerService(BaseCrawlerService):
    """爬虫配置服务类"""
    
    def get_configs(self, config_type: Optional[str] = None) -> List[CrawlerConfigResponse]:
        """
        获取爬虫配置列表
        
        Args:
            config_type: 配置类型筛选
            
        Returns:
            List[CrawlerConfigResponse]: 配置列表
        """
        query = self.db.query(SystemConfig)
        
        # 类型筛选
        if config_type:
            query = query.filter(SystemConfig.key.like(f"{config_type}_%"))
        
        # 只查询爬虫相关配置
        crawler_configs = query.filter(
            SystemConfig.key.like("crawler_%")
        ).all()
        
        # 转换为响应模型
        result = []
        for config in crawler_configs:
            # 解析配置值
            config_value = self._parse_config_value(config.value)
            
            response = CrawlerConfigResponse(
                id=config.id,
                config_key=config.key,
                config_value=config_value,
                description=config.description,
                config_type=self._extract_config_type(config.key),
                created_at=config.created_at,
                updated_at=config.updated_at
            )
            result.append(response)
        
        return result
    
    def create_config(self, config_data: CrawlerConfigCreate, created_by: int) -> CrawlerConfigResponse:
        """
        创建爬虫配置
        
        Args:
            config_data: 配置创建数据
            created_by: 创建者ID
            
        Returns:
            CrawlerConfigResponse: 创建的配置
        """
        # 检查配置键是否已存在
        existing = self.db.query(SystemConfig).filter(
            SystemConfig.key == config_data.config_key
        ).first()
        
        if existing:
            raise ValueError(f"配置键 '{config_data.config_key}' 已存在")
        
        # 序列化配置值
        config_value = self._serialize_config_value(config_data.config_value)
        
        # 创建新配置
        db_config = SystemConfig(
            key=config_data.config_key,
            value=config_value,
            description=config_data.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        
        # 转换为响应模型
        parsed_value = self._parse_config_value(db_config.value)
        
        return CrawlerConfigResponse(
            id=db_config.id,
            config_key=db_config.key,
            config_value=parsed_value,
            description=db_config.description,
            config_type=self._extract_config_type(db_config.key),
            created_at=db_config.created_at,
            updated_at=db_config.updated_at
        )
    
    def update_config(self, config_id: int, config_data: CrawlerConfigUpdate, 
                     updated_by: int) -> Optional[CrawlerConfigResponse]:
        """
        更新爬虫配置
        
        Args:
            config_id: 配置ID
            config_data: 配置更新数据
            updated_by: 更新者ID
            
        Returns:
            Optional[CrawlerConfigResponse]: 更新后的配置
        """
        db_config = self.db.query(SystemConfig).filter(
            SystemConfig.id == config_id
        ).first()
        
        if not db_config:
            return None
        
        # 更新字段
        update_data = config_data.dict(exclude_unset=True)
        
        if 'config_value' in update_data:
            db_config.value = self._serialize_config_value(update_data['config_value'])
        
        if 'description' in update_data:
            db_config.description = update_data['description']
        
        db_config.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_config)
        
        # 转换为响应模型
        parsed_value = self._parse_config_value(db_config.value)
        
        return CrawlerConfigResponse(
            id=db_config.id,
            config_key=db_config.key,
            config_value=parsed_value,
            description=db_config.description,
            config_type=self._extract_config_type(db_config.key),
            created_at=db_config.created_at,
            updated_at=db_config.updated_at
        )
    
    def delete_config(self, config_id: int) -> bool:
        """
        删除爬虫配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            bool: 是否删除成功
        """
        db_config = self.db.query(SystemConfig).filter(
            SystemConfig.id == config_id
        ).first()
        
        if not db_config:
            return False
        
        # 检查是否为系统关键配置
        if db_config.key.startswith("crawler_core_"):
            raise ValueError("不能删除系统核心配置")
        
        self.db.delete(db_config)
        self.db.commit()
        return True
    
    def get_config_by_key(self, config_key: str) -> Optional[CrawlerConfigResponse]:
        """
        根据键获取配置
        
        Args:
            config_key: 配置键
            
        Returns:
            Optional[CrawlerConfigResponse]: 配置对象
        """
        db_config = self.db.query(SystemConfig).filter(
            SystemConfig.key == config_key
        ).first()
        
        if not db_config:
            return None
        
        parsed_value = self._parse_config_value(db_config.value)
        
        return CrawlerConfigResponse(
            id=db_config.id,
            config_key=db_config.key,
            config_value=parsed_value,
            description=db_config.description,
            config_type=self._extract_config_type(db_config.key),
            created_at=db_config.created_at,
            updated_at=db_config.updated_at
        )
    
    def batch_update_configs(self, configs_data: List[Dict[str, Any]], updated_by: int) -> Dict[str, Any]:
        """
        批量更新配置
        
        Args:
            configs_data: 配置数据列表
            updated_by: 更新者ID
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        success_count = 0
        failed_updates = []
        
        for config_item in configs_data:
            try:
                config_key = config_item.get("config_key")
                config_value = config_item.get("config_value")
                
                if not config_key or config_value is None:
                    failed_updates.append({
                        "config_key": config_key,
                        "error": "配置键或值不能为空"
                    })
                    continue
                
                # 查找配置
                db_config = self.db.query(SystemConfig).filter(
                    SystemConfig.key == config_key
                ).first()
                
                if not db_config:
                    failed_updates.append({
                        "config_key": config_key,
                        "error": "配置不存在"
                    })
                    continue
                
                # 检查是否为只读配置
                if db_config.key.startswith("crawler_readonly_"):
                    failed_updates.append({
                        "config_key": config_key,
                        "error": "只读配置不能修改"
                    })
                    continue
                
                # 更新配置
                serialized_value = self._serialize_config_value(config_value)
                db_config.value = serialized_value
                db_config.updated_at = datetime.utcnow()
                
                success_count += 1
                
            except Exception as e:
                failed_updates.append({
                    "config_key": config_item.get("config_key"),
                    "error": str(e)
                })
        
        # 提交事务
        if success_count > 0:
            self.db.commit()
        
        return {
            "total_requested": len(configs_data),
            "success_count": success_count,
            "failed_count": len(failed_updates),
            "failed_updates": failed_updates
        }
    
    def get_config_statistics(self) -> Dict[str, Any]:
        """
        获取配置统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        # 爬虫相关配置总数
        total_crawler_configs = self.db.query(SystemConfig).filter(
            SystemConfig.key.like("crawler_%")
        ).count()
        
        # 按类型分组统计
        type_stats = self.db.query(
            func.substr(SystemConfig.key, 9, instr(SystemConfig.key, '_') - 9).label('type'),
            func.count(SystemConfig.id)
        ).filter(
            SystemConfig.key.like("crawler_%")
        ).group_by(
            func.substr(SystemConfig.key, 9, instr(SystemConfig.key, '_') - 9)
        ).all()
        
        # 最近更新的配置
        recent_configs = self.db.query(SystemConfig).filter(
            SystemConfig.key.like("crawler_%")
        ).order_by(
            SystemConfig.updated_at.desc()
        ).limit(5).all()
        
        return {
            "total_crawler_configs": total_crawler_configs,
            "type_distribution": [
                {"type": item[0], "count": item[1]} for item in type_stats
            ],
            "recent_updates": [
                {
                    "key": config.key,
                    "description": config.description,
                    "updated_at": config.updated_at.isoformat() if config.updated_at else None
                } for config in recent_configs
            ],
            "generated_at": self._get_current_timestamp()
        }
    
    def validate_config_value(self, config_key: str, config_value: Any) -> Dict[str, Any]:
        """
        验证配置值的有效性
        
        Args:
            config_key: 配置键
            config_value: 配置值
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        # 定义配置验证规则
        validation_rules = {
            "crawler_timeout": {
                "type": "integer",
                "min": 1,
                "max": 300,
                "required": True
            },
            "crawler_retry_times": {
                "type": "integer",
                "min": 0,
                "max": 10,
                "required": True
            },
            "crawler_concurrent_limit": {
                "type": "integer",
                "min": 1,
                "max": 100,
                "required": True
            },
            "crawler_log_level": {
                "type": "choice",
                "choices": ["DEBUG", "INFO", "WARNING", "ERROR"],
                "required": True
            },
            "crawler_proxy_enabled": {
                "type": "boolean",
                "required": False
            }
        }
        
        # 提取配置类型
        config_type = config_key.split('_')[1] if '_' in config_key else "unknown"
        rule = validation_rules.get(config_key, validation_rules.get(f"crawler_{config_type}"))
        
        if not rule:
            return {
                "valid": True,
                "message": "无特定验证规则，接受任意值"
            }
        
        # 必填检查
        if rule.get("required", False) and config_value is None:
            return {
                "valid": False,
                "message": f"配置 '{config_key}' 为必填项"
            }
        
        # 类型检查
        if config_value is not None:
            expected_type = rule.get("type")
            
            if expected_type == "integer":
                try:
                    int_value = int(config_value)
                    min_val = rule.get("min")
                    max_val = rule.get("max")
                    
                    if min_val is not None and int_value < min_val:
                        return {
                            "valid": False,
                            "message": f"配置值不能小于 {min_val}"
                        }
                    
                    if max_val is not None and int_value > max_val:
                        return {
                            "valid": False,
                            "message": f"配置值不能大于 {max_val}"
                        }
                        
                except (ValueError, TypeError):
                    return {
                        "valid": False,
                        "message": "配置值必须为整数"
                    }
            
            elif expected_type == "choice":
                choices = rule.get("choices", [])
                if config_value not in choices:
                    return {
                        "valid": False,
                        "message": f"配置值必须是以下之一: {', '.join(map(str, choices))}"
                    }
            
            elif expected_type == "boolean":
                if not isinstance(config_value, bool) and config_value not in [0, 1, "true", "false", "True", "False"]:
                    return {
                        "valid": False,
                        "message": "配置值必须为布尔值"
                    }
        
        return {
            "valid": True,
            "message": "配置值有效"
        }
    
    def _parse_config_value(self, value: str) -> Any:
        """
        解析配置值
        
        Args:
            value: 字符串配置值
            
        Returns:
            Any: 解析后的配置值
        """
        if value is None:
            return None
        
        # 尝试解析为JSON
        try:
            import json
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass
        
        # 尝试解析为布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # 尝试解析为整数
        try:
            return int(value)
        except (ValueError, TypeError):
            pass
        
        # 尝试解析为浮点数
        try:
            return float(value)
        except (ValueError, TypeError):
            pass
        
        # 返回原始字符串
        return value
    
    def _serialize_config_value(self, value: Any) -> str:
        """
        序列化配置值
        
        Args:
            value: 配置值
            
        Returns:
            str: 序列化后的字符串
        """
        if value is None:
            return ""
        
        # 如果是字符串，直接返回
        if isinstance(value, str):
            return value
        
        # 尝试序列化为JSON
        try:
            import json
            return json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            pass
        
        # 转换为字符串
        return str(value)
    
    def _extract_config_type(self, config_key: str) -> str:
        """
        提取配置类型
        
        Args:
            config_key: 配置键
            
        Returns:
            str: 配置类型
        """
        if not config_key.startswith("crawler_"):
            return "other"
        
        # 提取类型部分 (crawler_xxx_...)
        parts = config_key.split('_')
        if len(parts) >= 2:
            return parts[1]
        
        return "general"
    
    def initialize_default_configs(self) -> Dict[str, Any]:
        """
        初始化默认爬虫配置
        
        Returns:
            Dict[str, Any]: 初始化结果
        """
        default_configs = [
            {
                "key": "crawler_timeout",
                "value": "30",
                "description": "爬虫请求超时时间（秒）"
            },
            {
                "key": "crawler_retry_times",
                "value": "3",
                "description": "爬虫重试次数"
            },
            {
                "key": "crawler_concurrent_limit",
                "value": "10",
                "description": "爬虫并发限制"
            },
            {
                "key": "crawler_log_level",
                "value": "INFO",
                "description": "爬虫日志级别"
            },
            {
                "key": "crawler_proxy_enabled",
                "value": "false",
                "description": "是否启用代理"
            },
            {
                "key": "crawler_user_agent",
                "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "description": "爬虫User-Agent"
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for config_item in default_configs:
            # 检查配置是否已存在
            existing = self.db.query(SystemConfig).filter(
                SystemConfig.key == config_item["key"]
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # 创建配置
            db_config = SystemConfig(
                key=config_item["key"],
                value=config_item["value"],
                description=config_item["description"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(db_config)
            created_count += 1
        
        # 提交事务
        if created_count > 0:
            self.db.commit()
        
        return {
            "total_default_configs": len(default_configs),
            "created_count": created_count,
            "skipped_count": skipped_count,
            "message": f"初始化完成：创建 {created_count} 个配置，跳过 {skipped_count} 个已存在的配置"
        }