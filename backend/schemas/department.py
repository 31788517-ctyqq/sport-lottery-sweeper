from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class DepartmentBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    leader_id: Optional[int] = None
    status: Optional[bool] = True
    sort_order: Optional[int] = 0


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    leader_id: Optional[int] = None
    status: Optional[bool] = None
    sort_order: Optional[int] = None


class DepartmentInDBBase(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Department(DepartmentInDBBase):
    pass


class DepartmentWithChildren(Department):
    children: List["DepartmentWithChildren"] = []