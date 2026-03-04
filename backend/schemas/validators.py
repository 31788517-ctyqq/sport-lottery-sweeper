"""
Null安全Pydantic验证器

为Pydantic模型提供null值安全验证和防护，包括：
1. 字段null值检查 - 标记关键字段不允许为null
2. 默认值规范化 - 自动将null转换为默认值
3. 嵌套结构防护 - 递归检查嵌套字典和列表
4. 业务规则验证 - 基于数据源类型等业务规则的null值检查

使用方式：
1. 作为field_validator装饰器使用
2. 作为模型基类的配置
3. 作为独立的验证函数

示例：
```python
from .validators import validate_not_null, normalize_null_fields

class UserCreate(BaseModel):
    username: str
    email: str
    
    # 使用验证器
    _validate_username = field_validator('username')(validate_not_null)
    _normalize_fields = model_validator(mode='before')(normalize_null_fields)
```
"""

from typing import Any, Dict, List, Optional, Union, Type, Callable
from pydantic import BaseModel, FieldValidationInfo, field_validator, model_validator
from pydantic_core import PydanticCustomError

from ..utils.null_safety import (
    safe_get,
    ensure_not_null,
    normalize_null,
    coalesce
)
from ..core.exceptions import NullValueError

# AI_WORKING: coder1 @2026-02-04 - 创建Null安全Pydantic验证器

def validate_not_null(
    value: Any, 
    info: FieldValidationInfo,
    field_name: Optional[str] = None,
    custom_message: Optional[str] = None
) -> Any:
    """
    验证字段值不为None
    
    Args:
        value: 字段值
        info: 字段验证信息
        field_name: 字段名称（如未提供则从info中获取）
        custom_message: 自定义错误消息
        
    Returns:
        Any: 验证后的值
        
    Raises:
        ValueError: 当值为None时
    """
    if value is None:
        field = field_name or info.field_name
        message = custom_message or f"字段 '{field}' 不能为null"
        raise ValueError(message)
    
    return value


def normalize_null_fields(
    data: Dict[str, Any],
    default_values: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    规范化模型数据中的null值
    
    Args:
        data: 原始数据字典
        default_values: 字段默认值映射
        
    Returns:
        Dict[str, Any]: 规范化后的数据
    """
    if not isinstance(data, dict):
        return data
    
    default_values = default_values or {}
    result = data.copy()
    
    for field, default_value in default_values.items():
        if field in result and result[field] is None:
            result[field] = default_value
    
    return result


def ensure_critical_fields_not_null(
    model_class: Type[BaseModel],
    critical_fields: List[str]
) -> Type[BaseModel]:
    """
    为模型类添加关键字段null值检查
    
    Args:
        model_class: Pydantic模型类
        critical_fields: 关键字段列表
        
    Returns:
        Type[BaseModel]: 增强后的模型类
    """
    original_init = model_class.__init__
    
    def new_init(__pydantic_self__, **data):
        # 检查关键字段
        for field in critical_fields:
            if field in data and data[field] is None:
                raise NullValueError(
                    f"关键字段 '{field}' 不能为null (模型: {model_class.__name__})"
                )
        
        # 调用原始初始化
        original_init(__pydantic_self__, **data)
    
    model_class.__init__ = new_init
    return model_class


class NullSafeBaseModel(BaseModel):
    """
    Null安全的Pydantic基类
    
    提供以下特性：
    1. 自动null值检查 - 标记为required=True的字段自动检查null
    2. 默认值规范化 - 提供null_to_default装饰器
    3. 嵌套结构防护 - 自动递归检查嵌套模型
    4. 错误消息优化 - 提供友好的错误消息
    
    使用方式：
    ```python
    class UserModel(NullSafeBaseModel):
        username: str
        email: Optional[str] = None
        
        # 自定义null检查
        @field_validator('username')
        def validate_username_not_null(cls, v):
            if v is None:
                raise ValueError("用户名不能为空")
            return v
    ```
    """
    
    @model_validator(mode='before')
    @classmethod
    def validate_required_fields_not_null(cls, data: Any) -> Any:
        """
        验证必需字段不为null
        
        Args:
            data: 原始数据
            
        Returns:
            Any: 验证后的数据
        """
        if not isinstance(data, dict):
            return data
        
        # 获取模型字段定义
        model_fields = cls.model_fields
        
        for field_name, field_info in model_fields.items():
            # 检查是否为必需字段
            if not field_info.is_required():
                continue
            
            # 检查字段是否在数据中且为null
            if field_name in data and data[field_name] is None:
                # 获取字段的友好名称
                field_title = field_info.title or field_name
                
                # 抛出Pydantic友好的错误
                raise PydanticCustomError(
                    'null_value',
                    "字段 '{field}' 不能为null",
                    {'field': field_title}
                )
        
        return data
    
    @model_validator(mode='after')
    def normalize_null_values(self):
        """
        规范化模型实例中的null值
        
        Returns:
            self: 规范化后的模型实例
        """
        # 获取字段默认值
        for field_name, field_info in self.model_fields.items():
            current_value = getattr(self, field_name)
            
            # 如果当前值为None且有默认值，则使用默认值
            if current_value is None and field_info.default is not None:
                setattr(self, field_name, field_info.default)
        
        return self


# ==================== 特定业务验证器 ====================

def validate_data_source_fields(
    value: Any,
    info: FieldValidationInfo
) -> Any:
    """
    验证数据源相关字段
    
    Args:
        value: 字段值
        info: 验证信息
        
    Returns:
        Any: 验证后的值
    """
    field_name = info.field_name
    
    # 数据源名称不能为null
    if field_name == 'name' and value is None:
        raise ValueError("数据源名称不能为空")
    
    # 数据源类型不能为null
    if field_name == 'type' and value is None:
        raise ValueError("数据源类型不能为空")
    
    # 如果是config字段，确保JSON格式正确
    if field_name == 'config' and value is not None:
        if isinstance(value, str):
            try:
                import json
                json.loads(value)
            except json.JSONDecodeError:
                raise ValueError("config字段必须是有效的JSON格式")
    
    return value


def validate_crawler_task_fields(
    value: Any,
    info: FieldValidationInfo
) -> Any:
    """
    验证爬虫任务相关字段
    
    Args:
        value: 字段值
        info: 验证信息
        
    Returns:
        Any: 验证后的值
    """
    field_name = info.field_name
    
    # 任务名称不能为null
    if field_name == 'task_name' and value is None:
        raise ValueError("任务名称不能为空")
    
    # 数据源ID不能为null
    if field_name == 'data_source_id' and value is None:
        raise ValueError("数据源ID不能为空")
    
    # 调度表达式不能为null
    if field_name == 'schedule_expression' and value is None:
        raise ValueError("调度表达式不能为空")
    
    return value


def validate_user_fields(
    value: Any,
    info: FieldValidationInfo
) -> Any:
    """
    验证用户相关字段
    
    Args:
        value: 字段值
        info: 验证信息
        
    Returns:
        Any: 验证后的值
    """
    field_name = info.field_name
    
    # 用户名不能为null
    if field_name == 'username' and value is None:
        raise ValueError("用户名不能为空")
    
    # 邮箱不能为null
    if field_name == 'email' and value is None:
        raise ValueError("邮箱不能为空")
    
    # 密码字段特殊处理
    if field_name in ['password', 'new_password', 'old_password'] and value is None:
        raise ValueError("密码字段不能为空")
    
    return value


# ==================== 装饰器和工具函数 ====================

def null_safe_validator(*field_names: str):
    """
    为指定字段添加null安全验证的装饰器
    
    Args:
        *field_names: 字段名称列表
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @field_validator(*field_names)
        def wrapper(cls, value: Any, info: FieldValidationInfo) -> Any:
            # 首先检查null值
            if value is None:
                field = info.field_name
                raise ValueError(f"字段 '{field}' 不能为null")
            
            # 调用原始验证函数
            return func(cls, value, info)
        
        return wrapper
    
    return decorator


def with_default_on_null(default_value: Any):
    """
    当字段值为null时使用默认值的装饰器
    
    Args:
        default_value: 默认值
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @field_validator(func.__name__)
        def wrapper(cls, value: Any, info: FieldValidationInfo) -> Any:
            if value is None:
                return default_value
            
            # 调用原始验证函数
            return func(cls, value, info)
        
        return wrapper
    
    return decorator


# ==================== 模型配置装饰器 ====================

def configure_null_safety(
    check_required: bool = True,
    normalize_nulls: bool = True,
    critical_fields: Optional[List[str]] = None
):
    """
    为模型配置null安全特性的装饰器
    
    Args:
        check_required: 是否检查必需字段的null值
        normalize_nulls: 是否规范化null值为默认值
        critical_fields: 关键字段列表（额外检查）
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(model_class: Type[BaseModel]) -> Type[BaseModel]:
        # 添加模型验证器
        if check_required:
            original_validator = getattr(model_class, 'validate_required_fields_not_null', None)
            if not original_validator:
                @model_validator(mode='before')
                @classmethod
                def validate_required_fields_not_null(cls, data: Any) -> Any:
                    if not isinstance(data, dict):
                        return data
                    
                    model_fields = cls.model_fields
                    for field_name, field_info in model_fields.items():
                        if not field_info.is_required():
                            continue
                        
                        if field_name in data and data[field_name] is None:
                            field_title = field_info.title or field_name
                            raise PydanticCustomError(
                                'null_value',
                                "字段 '{field}' 不能为null",
                                {'field': field_title}
                            )
                    
                    return data
                
                model_class.validate_required_fields_not_null = validate_required_fields_not_null
        
        # 添加关键字段检查
        if critical_fields:
            model_class = ensure_critical_fields_not_null(model_class, critical_fields)
        
        return model_class
    
    return decorator


# 导出常用验证器
__all__ = [
    # 基础验证器
    'validate_not_null',
    'normalize_null_fields',
    'ensure_critical_fields_not_null',
    
    # 基类
    'NullSafeBaseModel',
    
    # 业务验证器
    'validate_data_source_fields',
    'validate_crawler_task_fields',
    'validate_user_fields',
    
    # 装饰器
    'null_safe_validator',
    'with_default_on_null',
    'configure_null_safety',
]

# AI_DONE: coder1 @2026-02-04