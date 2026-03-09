#!/usr/bin/env python3
"""最小化测试应用"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# 定义模型
Base = declarative_base()

class CaipiaoData(Base):
    __tablename__ = "caipiao_data_minimal"

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(String(10), index=True)
    home_team = Column(String(100), index=True)
    guest_team = Column(String(100), index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# 数据库设置
DATABASE_URL = "sqlite:///./test_minimal.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建表
Base.metadata.create_all(bind=engine)

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic模型
class CaipiaoDataSchema(BaseModel):
    id: int
    line_id: str
    home_team: str
    guest_team: str

    class Config:
        from_attributes = True

# FastAPI应用
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test-caipiao", response_model=List[CaipiaoDataSchema])
def get_caipiao_data(skip: int = 0, limit: int = 20, db = Depends(get_db)):
    """测试竞彩数据API"""
    caipiao_data = db.query(CaipiaoData).offset(skip).limit(limit).all()
    return caipiao_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)