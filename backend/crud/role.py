from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models.role import Role
from backend.schemas.role import RoleCreate, RoleUpdate


class CRUDRole:
    async def get(self, db: AsyncSession, role_id: int) -> Optional[Role]:
        result = await db.execute(select(Role).filter(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Role]:
        result = await db.execute(select(Role).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: RoleCreate) -> Role:
        db_obj = Role(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Role, obj_in: RoleUpdate
    ) -> Role:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, role_id: int) -> Role:
        result = await db.execute(select(Role).filter(Role.id == role_id))
        obj = result.scalar_one()
        await db.delete(obj)
        await db.commit()
        return obj


crud_role = CRUDRole()