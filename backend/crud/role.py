from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
import json
from backend.models.role import Role
from backend.schemas.role import RoleCreate, RoleUpdate


class CRUDRole:
    @staticmethod
    def _normalize_status_filter(status):
        if status is None:
            return None
        if isinstance(status, bool):
            return status
        raw = str(status).strip().lower()
        if raw in {"active", "enabled", "enable", "true", "1", "yes", "on"}:
            return True
        if raw in {"inactive", "disabled", "disable", "false", "0", "no", "off"}:
            return False
        return None

    async def get(self, db: AsyncSession, role_id: int) -> Optional[Role]:
        result = await db.execute(select(Role).filter(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        result = await db.execute(select(Role).filter(Role.name == name))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Role]:
        result = await db.execute(select(Role).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_multi_with_filter(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, status: str = None, search: str = None
    ) -> tuple[List[Role], int]:
        """带过滤条件获取角色列表"""
        query = select(Role)
        
        status_filter = self._normalize_status_filter(status)
        if status_filter is not None:
            query = query.filter(Role.status.is_(status_filter))
        
        if search:
            query = query.filter(Role.name.contains(search) | Role.description.contains(search))
        
        # 获取总数
        count_query = select(func.count()).select_from(Role)
        if status_filter is not None:
            count_query = count_query.filter(Role.status.is_(status_filter))
        if search:
            count_query = count_query.filter(Role.name.contains(search) | Role.description.contains(search))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 获取角色列表
        result = await db.execute(query.offset(skip).limit(limit))
        roles = result.scalars().all()
        
        return roles, total

    async def create(self, db: AsyncSession, *, obj_in: RoleCreate) -> Role:
        data = obj_in.dict()
        permissions = data.get("permissions")
        if isinstance(permissions, (list, dict)):
            data["permissions"] = json.dumps(permissions, ensure_ascii=False)
        db_obj = Role(**data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Role, obj_in: RoleUpdate
    ) -> Role:
        update_data = obj_in.dict(exclude_unset=True)
        if "permissions" in update_data and isinstance(update_data.get("permissions"), (list, dict)):
            update_data["permissions"] = json.dumps(update_data["permissions"], ensure_ascii=False)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_status(self, db: AsyncSession, *, role_id: int, status: str) -> Role:
        """更新角色状态"""
        role = await self.get(db, role_id)
        if role:
            status_filter = self._normalize_status_filter(status)
            if status_filter is None:
                raise ValueError("Invalid role status, expected active/inactive")
            role.status = status_filter
            db.add(role)
            await db.commit()
            await db.refresh(role)
        return role

    async def remove(self, db: AsyncSession, *, role_id: int) -> Role:
        result = await db.execute(select(Role).filter(Role.id == role_id))
        obj = result.scalar_one()
        await db.delete(obj)
        await db.commit()
        return obj

    async def assign_permissions(self, db: AsyncSession, *, role: Role, permission_ids: List[int]) -> Role:
        """为角色分配权限"""
        # 将权限ID列表存储为JSON字符串
        role.permissions = json.dumps(permission_ids)
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    async def count_users(self, db: AsyncSession, *, role_id: int) -> int:
        """统计使用该角色的用户数量"""
        from backend.models.admin_user import AdminUser
        result = await db.execute(
            select(func.count(AdminUser.id)).where(AdminUser.role_id == role_id)
        )
        return result.scalar_one()


crud_role = CRUDRole()
