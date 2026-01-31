from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func, desc
from datetime import datetime
from backend.crud.base import CRUDBase
from backend.models.department import Department
from backend.schemas.department import DepartmentCreate, DepartmentUpdate


class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentUpdate]):
    async def get_multi_with_filter(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, tree: bool = False, search: Optional[str] = None
    ) -> tuple[List[Department], int]:
        """
        获取部门列表，支持树形结构
        """
        query = select(self.model)
        
        # 搜索过滤
        if search:
            query = query.filter(Department.name.contains(search))
        
        # 获取总数
        count_query = select(func.count()).select_from(self.model)
        if search:
            count_query = count_query.filter(Department.name.contains(search))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        if tree:
            # 返回树形结构
            all_result = await db.execute(query)
            all_departments = all_result.scalars().all()
            return self._build_tree(all_departments), total
        else:
            # 返回列表结构
            query = query.order_by(desc(Department.created_at)).offset(skip).limit(limit)
            result = await db.execute(query)
            departments = result.scalars().all()
            return departments, total

    async def get_children(self, db: AsyncSession, *, parent_id: Optional[int] = None) -> List[Department]:
        """
        获取指定父级的子部门
        """
        if parent_id is None:
            # 获取顶级部门
            query = select(self.model).filter(self.model.parent_id.is_(None))
        else:
            query = select(self.model).filter(self.model.parent_id == parent_id)
        
        result = await db.execute(query)
        return result.scalars().all()

    def _build_tree(self, departments: List[Department]) -> List[Department]:
        """
        构建部门树形结构
        """
        # 创建部门字典，以ID为键
        dept_dict = {dept.id: dept for dept in departments}
        
        # 初始化根节点列表
        roots = []
        
        # 遍历所有部门
        for dept in departments:
            dept.children = []  # 初始化children列表
            
            # 如果parent_id为None或不在字典中，则为根节点
            if dept.parent_id is None or dept.parent_id not in dept_dict:
                roots.append(dept)
            else:
                # 否则添加到其父节点的children列表中
                parent_dept = dept_dict[dept.parent_id]
                if not hasattr(parent_dept, 'children'):
                    parent_dept.children = []
                parent_dept.children.append(dept)
        
        return roots

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Department]:
        """
        根据名称获取部门
        """
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalar_one_or_none()


# 创建部门CRUD实例
crud_department = CRUDDepartment(Department)