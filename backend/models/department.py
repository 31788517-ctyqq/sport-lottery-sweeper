from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.models.base import Base, BaseFullModel


class Department(BaseFullModel):
    __tablename__ = "departments"

    # 基本信息
    name = Column(String(100), nullable=False, index=True, unique=True)  # 部门名称
    parent_id = Column(Integer, ForeignKey("departments.id", ondelete='SET NULL'), nullable=True, index=True)  # 上级部门ID
    description = Column(Text, nullable=True)  # 描述
    leader_id = Column(Integer, ForeignKey("admin_users.id", ondelete='SET NULL'), nullable=True)  # 部门负责人ID
    status = Column(Boolean, default=True, nullable=False, index=True)  # 状态
    sort_order = Column(Integer, default=0, nullable=False)  # 排序

    # AI_WORKING: coder2 @2026-01-28T09:48:56Z - 修复remote_side参数，使用字符串列表达式而不是内置id函数
    # 关系 - 使用字符串引用避免循环导入
    parent = relationship("Department", remote_side="Department.id", backref="children")  # 父部门
    # AI_DONE: coder2 @2026-01-28T09:48:56Z
    # AI_WORKING: coder2 @2026-01-28T09:54:56Z - 完善leader和users关系的外键指定，解决多外键路径歧义
    leader = relationship("AdminUser", foreign_keys=[leader_id], primaryjoin="Department.leader_id == AdminUser.id", backref="lead_departments")  # 部门负责人
    users = relationship("AdminUser", foreign_keys="AdminUser.department_id", primaryjoin="Department.id == AdminUser.department_id", back_populates="department_obj")  # 部门下的用户
    # AI_DONE: coder2 @2026-01-28T09:54:56Z

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"