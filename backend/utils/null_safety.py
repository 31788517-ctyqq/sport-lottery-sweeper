#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Null安全处理工具包
提供统一的null值防护机制，避免AttributeError和TypeError

核心功能：
1. coalesce: 返回第一个非None值
2. safe_get: 安全获取嵌套对象属性
3. ensure_not_null: 验证值不为None
4. null_safe装饰器: 自动捕获NoneType错误
"""

from typing import Any, Optional, TypeVar, Callable, Dict, List
from functools import wraps

T = TypeVar("T")


class NullSafety:
    """Null安全处理核心类"""

    @staticmethod
    def coalesce(*args: Any) -> Any:
        """
        返回第一个非None值

        Args:
            *args: 任意数量的参数

        Returns:
            第一个非None值，如果所有参数都为None则返回None

        Examples:
            >>> NullSafety.coalesce(None, None, "default")
            'default'
            >>> NullSafety.coalesce(None, 0, False)
            0
        """
        for arg in args:
            if arg is not None:
                return arg
        return None

    @staticmethod
    def safe_get(obj: Any, path: str, default: Any = None) -> Any:
        """
        安全获取对象属性，支持点分路径和列表索引

        Args:
            obj: 要获取属性的对象
            path: 属性路径，如 "user.profile.name" 或 "users[0].name"
            default: 路径不存在时的默认值

        Returns:
            属性值或默认值

        Examples:
            >>> data = {"user": {"profile": {"name": "John"}}}
            >>> NullSafety.safe_get(data, "user.profile.name")
            'John'
            >>> NullSafety.safe_get(data, "user.profile.age", 30)
            30
            >>> NullSafety.safe_get(None, "anything", "default")
            'default'
        """
        if obj is None:
            return default

        try:
            # 解析路径：支持 . 和 [] 语法
            parts = []
            current = ""
            in_bracket = False

            for char in path:
                if char == "[" and not in_bracket:
                    if current:
                        parts.append(current)
                    current = ""
                    in_bracket = True
                elif char == "]" and in_bracket:
                    parts.append(f"[{current}]")
                    current = ""
                    in_bracket = False
                elif char == "." and not in_bracket:
                    if current:
                        parts.append(current)
                    current = ""
                else:
                    current += char

            if current:
                parts.append(current)

            # 遍历路径
            current_obj = obj
            for part in parts:
                if current_obj is None:
                    return default

                # 处理列表索引，如 "[0]"
                if part.startswith("[") and part.endswith("]"):
                    index_str = part[1:-1]
                    try:
                        index = int(index_str)
                        if (
                            isinstance(current_obj, (list, tuple))
                            and 0 <= index < len(current_obj)
                        ):
                            current_obj = current_obj[index]
                        else:
                            return default
                    except (ValueError, TypeError):
                        return default
                else:
                    # 处理字典或对象属性
                    if isinstance(current_obj, dict):
                        current_obj = current_obj.get(part)
                    elif hasattr(current_obj, part):
                        current_obj = getattr(current_obj, part)
                    else:
                        return default

            return current_obj if current_obj is not None else default

        except (AttributeError, KeyError, IndexError, TypeError):
            return default

    @staticmethod
    def ensure_not_null(
        value: Optional[T],
        name: str = "value",
        error_message: Optional[str] = None,
    ) -> T:
        """
        确保值不为None，否则抛出业务异常

        Args:
            value: 要检查的值
            name: 值的名称（用于错误消息）
            error_message: 自定义错误消息

        Returns:
            如果值不为None，则返回该值

        Raises:
            BusinessException: 当值为None时

        Examples:
            >>> NullSafety.ensure_not_null("test", "name")
            'test'
            >>> NullSafety.ensure_not_null(None, "id")
            BusinessException: id cannot be null
        """
        if value is None:
            from backend.core.exceptions import BusinessException

            message = error_message or f"{name} cannot be null"
            raise BusinessException(message)
        return value

    @staticmethod
    def safe_call(func: Callable, *args, **kwargs) -> Optional[Any]:
        """
        安全调用函数，捕获NoneType相关异常

        Args:
            func: 要调用的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            函数返回值，如果发生NoneType异常则返回None
        """
        try:
            return func(*args, **kwargs)
        except (AttributeError, TypeError) as e:
            if "NoneType" in str(e):
                return None
            raise

    @staticmethod
    def normalize_null(value: Any, default: Any = "") -> Any:
        """
        规范化null值：将None、空字符串、空列表等转换为默认值

        Args:
            value: 要规范化的值
            default: 当值为null时的默认值

        Returns:
            规范化后的值
        """
        if value is None:
            return default
        if isinstance(value, str) and value.strip() == "":
            return default
        if isinstance(value, (list, dict, set, tuple)) and len(value) == 0:
            return default
        return value


def null_safe(func: Callable) -> Callable:
    """
    装饰器：自动处理函数中的null值相关异常

    使用场景：
    1. 数据库查询可能返回None
    2. 嵌套对象访问可能引发AttributeError
    3. 需要将NoneType异常转换为业务异常

    Args:
        func: 要装饰的函数

    Returns:
        包装后的函数

    Examples:
        @null_safe
        def get_user_name(user_id):
            user = db.query(User).get(user_id)
            return user.profile.name  # 如果user为None会抛出BusinessException
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (AttributeError, TypeError) as e:
            if "NoneType" in str(e):
                from backend.core.exceptions import BusinessException

                func_name = func.__name__
                raise BusinessException(
                    f"Null value encountered in {func_name}: {str(e)}"
                )
            raise

    return wrapper


def safe_dict_get(dict_obj: Dict, key: Any, default: Any = None) -> Any:
    """
    安全获取字典值，避免KeyError

    Args:
        dict_obj: 字典对象
        key: 键
        default: 默认值

    Returns:
        字典值或默认值
    """
    if dict_obj is None:
        return default
    return dict_obj.get(key, default)


def safe_list_get(list_obj: List, index: int, default: Any = None) -> Any:
    """
    安全获取列表元素，避免IndexError

    Args:
        list_obj: 列表对象
        index: 索引
        default: 默认值

    Returns:
        列表元素或默认值
    """
    if list_obj is None:
        return default
    try:
        return list_obj[index]
    except (IndexError, TypeError):
        return default


# 导出常用函数
__all__ = [
    "NullSafety",
    "null_safe",
    "safe_dict_get",
    "safe_list_get",
    "coalesce",
    "safe_get",
    "ensure_not_null",
    "normalize_null",  # 添加此行以导出normalize_null函数
]

# 提供简化的函数别名
coalesce = NullSafety.coalesce
safe_get = NullSafety.safe_get
ensure_not_null = NullSafety.ensure_not_null
normalize_null = NullSafety.normalize_null  # 添加此行以导出函数别名
