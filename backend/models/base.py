"""
SQLAlchemy基础模型和混入类
"""
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, DateTime, Integer, String, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    """
    SQLAlchemy基础模型类
    """
    __allow_unmapped__ = True
    
    # 为主键ID添加声明，让继承的模型可以使用
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 生成表名
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # 将类名转换为小写复数形式（如：User -> users）
        name = cls.__name__
        if name.endswith('y'):
            return name[:-1] + 'ies'
        elif name.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return name + 'es'
        else:
            return name.lower() + 's'

    def to_dict(self) -> Dict[str, Any]:
        """
        将模型转换为字典
        
        Returns:
            Dict[str, Any]: 模型数据字典
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def update(self, **kwargs) -> None:
        """
        更新模型字段
        
        Args:
            **kwargs: 要更新的字段和值
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class TimestampMixin:
    """
    时间戳混入类
    """
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, index=True)


class SoftDeleteMixin:
    """
    软删除混入类
    """
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    def soft_delete(self) -> None:
        """
        软删除方法
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """
        恢复软删除
        """
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin:
    """
    审计混入类
    """
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)


class UUIDMixin:
    """
    UUID混入类
    """
    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)


# 创建常用模型基类
class BaseModel(Base, TimestampMixin):
    """
    基础模型类（带时间戳）
    """
    __abstract__ = True
    # id已经在Base中定义了，所以不需要重复定义


class BaseAuditModel(Base, TimestampMixin, AuditMixin):
    """
    基础审计模型类（带时间戳和审计信息）
    """
    __abstract__ = True
    # id已经在Base中定义了，所以不需要重复定义


class BaseSoftDeleteModel(Base, TimestampMixin, SoftDeleteMixin):
    """
    基础软删除模型类（带时间戳和软删除）
    """
    __abstract__ = True
    # id已经在Base中定义了，所以不需要重复定义


class BaseFullModel(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """
    完整基础模型类（带时间戳、软删除和审计信息）
    """
    __abstract__ = True
    # id已经在Base中定义了，所以不需要重复定义


class BaseUUIDModel(Base, UUIDMixin, TimestampMixin):
    """
    UUID基础模型类（带UUID和时间戳）
    """
    __abstract__ = True
    # id已经在Base中定义了，所以不需要重复定义