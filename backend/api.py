from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Match, Intelligence, Prediction
from database import get_db
from pydantic import BaseModel

router = APIRouter()

# Pydantic模型定义
class MatchBase(BaseModel):
    match_id: str
    league: str
    home_team: str
    away_team: str
    venue: str
    kickoff_time: datetime
    sell_deadline: datetime

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: int

    class Config:
        from_attributes = True

class IntelligenceBase(BaseModel):
    match_id: str
    summary: str
    content: str
    category: str
    source: str
    weight: float
    publish_time: datetime
    is_new: bool = False

class IntelligenceCreate(IntelligenceBase):
    pass

class Intelligence(IntelligenceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PredictionBase(BaseModel):
    match_id: str
    type: str
    prediction: str
    source: str
    weight: float

class PredictionCreate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# API路由实现
@router.get("/matches", response_model=List[Match])
async def get_matches(
    league: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """获取比赛列表"""
    query = db.query(Match)
    if league:
        query = query.filter(Match.league == league)
    if start_date:
        query = query.filter(Match.kickoff_time >= start_date)
    if end_date:
        query = query.filter(Match.kickoff_time <= end_date)
    return query.all()

@router.get("/matches/{match_id}", response_model=Match)
async def get_match(match_id: str, db: Session = Depends(get_db)):
    """获取单场比赛详情"""
    match = db.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@router.get("/intelligence/{match_id}", response_model=List[Intelligence])
async def get_match_intelligence(
    match_id: str,
    category: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取比赛情报"""
    query = db.query(Intelligence).filter(Intelligence.match_id == match_id)
    if category:
        query = query.filter(Intelligence.category == category)
    if source:
        query = query.filter(Intelligence.source == source)
    return query.order_by(Intelligence.weight.desc()).all()

@router.get("/predictions/{match_id}", response_model=List[Prediction])
async def get_match_predictions(
    match_id: str,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取比赛预测"""
    query = db.query(Prediction).filter(Prediction.match_id == match_id)
    if type:
        query = query.filter(Prediction.type == type)
    return query.order_by(Prediction.weight.desc()).all()

@router.get("/leagues")
async def get_leagues(db: Session = Depends(get_db)):
    """获取所有联赛列表"""
    return db.query(Match.league).distinct().all()

@router.post("/matches", response_model=Match)
async def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    """创建新比赛"""
    db_match = Match(**match.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

@router.post("/intelligence", response_model=Intelligence)
async def create_intelligence(intelligence: IntelligenceCreate, db: Session = Depends(get_db)):
    """创建新情报"""
    db_intelligence = Intelligence(**intelligence.dict())
    db.add(db_intelligence)
    db.commit()
    db.refresh(db_intelligence)
    return db_intelligence

@router.post("/predictions", response_model=Prediction)
async def create_prediction(prediction: PredictionCreate, db: Session = Depends(get_db)):
    """创建新预测"""
    db_prediction = Prediction(**prediction.dict())
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

@router.post("/scrape/{match_id}")
async def trigger_scrape(match_id: str, db: Session = Depends(get_db)):
    """手动触发数据抓取"""
    # TODO: 实现实际的爬虫调用
    return {"message": f"Scraping triggered for match {match_id}"}