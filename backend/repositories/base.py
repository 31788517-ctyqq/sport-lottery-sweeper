#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repository模式基础层
提供null安全的数据访问和CRUD操作

设计目标：
1. 封装数据访问逻辑，减少重复代码
2. 提供null安全的查询方法
3. 统一错误处理模式
4. 支持事务性操作
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import SQLAlchemyError

from backend.utils.null_safety import NullSafety, null_safe
from backend.core.exceptions import NotFoundException, NullValueError, EmptyResultError

T = TypeVar('T', bound=Any)


class BaseRepository:
    """
    基础Repository类
    
    提供通用的数据访问方法，所有具体的Repository应继承此类
    """
    
    def __init__(self, model: Type[T], db_session: Session):
        """
        初始化Repository
        
        Args:
            model: SQLAlchemy模型类
            db_session: 数据库会话
        """
        self.model = model
        self.db = db_session
    
    @null_safe
    def get_by_id(self, id: Any) -> Optional[T]:
        """
        根据ID获取记录
        
        Args:
            id: 记录ID
            
        Returns:
            找到的记录，如果不存在则返回None
            
        Examples:
            >>> repo.get_by_id(1)
            <User(id=1, name='John')>
            >>> repo.get_by_id(999)
            None
        """
        return self.db.query(self.model).filter_by(id=id).first()
    
    def get_by_id_or_none(self, id: Any) -> Optional[T]:
        """
        根据ID获取记录，不存在时返回None（null安全版本）
        
        Args:
            id: 记录ID
            
        Returns:
            找到的记录，如果不存在则返回None
            
        Notes:
            此方法会自动处理数据库查询中的null值
        """
        try:
            return self.get_by_id(id)
        except (AttributeError, TypeError):
            return None
    
    def get_by_id_or_raise(self, id: Any, error_message: Optional[str] = None) -> T:
        """
        根据ID获取记录，不存在时抛出NotFoundException
        
        Args:
            id: 记录ID
            error_message: 自定义错误消息
            
        Returns:
            找到的记录
            
        Raises:
            NotFoundException: 当记录不存在时
            
        Examples:
            >>> repo.get_by_id_or_raise(1)
            <User(id=1, name='John')>
            >>> repo.get_by_id_or_raise(999)
            NotFoundException: 记录不存在
        """
        record = self.get_by_id_or_none(id)
        if record is None:
            msg = error_message or f"{self.model.__name__} with id {id} not found"
            raise NotFoundException(msg)
        return record
    
    @null_safe
    def get_one(self, **filters: Any) -> Optional[T]:
        """
        根据过滤条件获取第一条记录
        
        Args:
            **filters: 过滤条件
            
        Returns:
            找到的记录，如果不存在则返回None
            
        Examples:
            >>> repo.get_one(name='John', status='active')
            <User(id=1, name='John', status='active')>
        """
        query = self.db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.first()
    
    def get_one_or_none(self, **filters: Any) -> Optional[T]:
        """
        根据过滤条件获取记录，不存在时返回None（null安全版本）
        
        Args:
            **filters: 过滤条件
            
        Returns:
            找到的记录，如果不存在则返回None
        """
        try:
            return self.get_one(**filters)
        except (AttributeError, TypeError):
            return None
    
    def get_one_or_raise(self, **filters: Any) -> T:
        """
        根据过滤条件获取记录，不存在时抛出EmptyResultError
        
        Args:
            **filters: 过滤条件
            
        Returns:
            找到的记录
            
        Raises:
            EmptyResultError: 当记录不存在时
        """
        record = self.get_one_or_none(**filters)
        if record is None:
            filter_str = ", ".join([f"{k}={v}" for k, v in filters.items()])
            raise EmptyResultError(f"No record found with filters: {filter_str}")
        return record
    
    def get_all(self, **filters: Any) -> List[T]:
        """
        获取所有记录（可过滤）
        
        Args:
            **filters: 过滤条件
            
        Returns:
            记录列表，如果没有记录则返回空列表
            
        Examples:
            >>> repo.get_all(status='active')
            [<User(id=1)>, <User(id=2)>]
        """
        query = self.db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.all()
    
    def get_all_or_empty(self, **filters: Any) -> List[T]:
        """
        获取所有记录，保证返回列表（null安全版本）
        
        Args:
            **filters: 过滤条件
            
        Returns:
            记录列表，保证不为None
        """
        try:
            result = self.get_all(**filters)
            return result if result is not None else []
        except (AttributeError, TypeError):
            return []
    
    @null_safe
    def create(self, **data: Any) -> T:
        """
        创建新记录
        
        Args:
            **data: 记录数据
            
        Returns:
            创建的记录
            
        Raises:
            NullValueError: 当必填字段为null时
            
        Examples:
            >>> repo.create(name='John', email='john@example.com')
            <User(id=1, name='John', email='john@example.com')>
        """
        # 过滤掉None值，避免数据库插入null
        clean_data = {k: v for k, v in data.items() if v is not None}
        
        # 验证必填字段
        required_fields = getattr(self.model, '__required_fields__', [])
        for field in required_fields:
            if field not in clean_data or clean_data[field] is None:
                raise NullValueError(f"Field '{field}' is required")
        
        instance = self.model(**clean_data)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def create_safe(self, **data: Any) -> Optional[T]:
        """
        安全创建记录，失败时返回None
        
        Args:
            **data: 记录数据
            
        Returns:
            创建的记录，如果失败则返回None
        """
        try:
            return self.create(**data)
        except (SQLAlchemyError, NullValueError, AttributeError):
            self.db.rollback()
            return None
    
    @null_safe
    def update(self, instance: T, **data: Any) -> T:
        """
        更新记录
        
        Args:
            instance: 要更新的记录实例
            **data: 更新数据
            
        Returns:
            更新后的记录
            
        Examples:
            >>> user = repo.get_by_id(1)
            >>> repo.update(user, name='John Updated', status='inactive')
            <User(id=1, name='John Updated', status='inactive')>
        """
        # 过滤掉None值，避免将有效字段设置为null
        clean_data = {k: v for k, v in data.items() if v is not None}
        
        for key, value in clean_data.items():
            setattr(instance, key, value)
        
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def update_safe(self, instance: T, **data: Any) -> Optional[T]:
        """
        安全更新记录，失败时返回None
        
        Args:
            instance: 要更新的记录实例
            **data: 更新数据
            
        Returns:
            更新后的记录，如果失败则返回None
        """
        try:
            return self.update(instance, **data)
        except (SQLAlchemyError, AttributeError):
            self.db.rollback()
            return None
    
    def update_by_id(self, id: Any, **data: Any) -> Optional[T]:
        """
        根据ID更新记录
        
        Args:
            id: 记录ID
            **data: 更新数据
            
        Returns:
            更新后的记录，如果记录不存在则返回None
        """
        instance = self.get_by_id_or_none(id)
        if instance is None:
            return None
        return self.update_safe(instance, **data)
    
    @null_safe
    def delete(self, instance: T) -> bool:
        """
        删除记录
        
        Args:
            instance: 要删除的记录实例
            
        Returns:
            删除是否成功
        """
        try:
            self.db.delete(instance)
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            return False
    
    def delete_by_id(self, id: Any) -> bool:
        """
        根据ID删除记录
        
        Args:
            id: 记录ID
            
        Returns:
            删除是否成功
        """
        instance = self.get_by_id_or_none(id)
        if instance is None:
            return False
        return self.delete(instance)
    
    def exists(self, **filters: Any) -> bool:
        """
        检查记录是否存在
        
        Args:
            **filters: 过滤条件
            
        Returns:
            是否存在
        """
        record = self.get_one_or_none(**filters)
        return record is not None
    
    def count(self, **filters: Any) -> int:
        """
        统计记录数量
        
        Args:
            **filters: 过滤条件
            
        Returns:
            记录数量
        """
        query = self.db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.count()
    
    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """
        批量创建记录
        
        Args:
            data_list: 记录数据列表
            
        Returns:
            创建的记录列表
        """
        instances = []
        for data in data_list:
            # 过滤None值
            clean_data = {k: v for k, v in data.items() if v is not None}
            instance = self.model(**clean_data)
            instances.append(instance)
        
        self.db.add_all(instances)
        self.db.commit()
        
        # 刷新所有实例
        for instance in instances:
            self.db.refresh(instance)
        
        return instances
    
    def safe_bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """
        安全批量创建记录，失败时回滚
        
        Args:
            data_list: 记录数据列表
            
        Returns:
            创建的记录列表，如果失败则返回空列表
        """
        try:
            return self.bulk_create(data_list)
        except (SQLAlchemyError, AttributeError):
            self.db.rollback()
            return []
    
    def with_transaction(self, func: callable) -> Any:
        """
        在事务中执行函数
        
        Args:
            func: 要执行的函数
            
        Returns:
            函数返回值
            
        Examples:
            >>> def update_user_and_log(user_id, new_status):
            ...     user = repo.get_by_id_or_raise(user_id)
            ...     repo.update(user, status=new_status)
            ...     log_repo.create(user_id=user_id, action='update')
            ...     return user
            >>> repo.with_transaction(lambda: update_user_and_log(1, 'active'))
        """
        try:
            result = func()
            self.db.commit()
            return result
        except Exception as e:
            self.db.rollback()
            raise e


# 导出常用函数和类
__all__ = ["BaseRepository"]