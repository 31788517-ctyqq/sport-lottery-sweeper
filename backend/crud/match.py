from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.match import Match
from ..schemas.match import MatchCreate, MatchUpdate


class CRUDMatch:
    async def get(self, db: AsyncSession, id: int) -> Optional[Match]:
        result = await db.execute(select(Match).filter(Match.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Match).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: MatchCreate) -> Match:
        db_obj = Match(
            home_team=obj_in.home_team,
            away_team=obj_in.away_team,
            match_time=obj_in.match_time,
            league=obj_in.league,
            odds_home=obj_in.odds_home,
            odds_draw=obj_in.odds_draw,
            odds_away=obj_in.odds_away,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: Match, obj_in: MatchUpdate) -> Match:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, id: int) -> Match:
        result = await db.execute(select(Match).filter(Match.id == id))
        obj = result.scalar_one()
        await db.delete(obj)
        await db.commit()
        return obj


match = CRUDMatch()