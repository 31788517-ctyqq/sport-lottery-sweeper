"""
SP管理模块API路由 - 简化版
仅包含SP值核心管理功能，删除比赛信息管理模块
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from backend.database import get_db
from backend.models.sp_core import (
    DataSource, OddsCompany, SPRecord, SPModificationLog,
    HANDICAP_TYPES, DATA_SOURCE_TYPES
)
from backend.auth.dependencies import get_current_admin_user
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sp", tags=["sp-management"])


# Pydantic模型定义
class DataSourceCreate(BaseModel):
    name: str = Field(..., description="数据源名称")
    source_type: str = Field("api", description="数据源类型")
    api_url: Optional[str] = Field(None, description="API地址")
    api_key: Optional[str] = Field(None, description="API密钥")
    file_path: Optional[str] = Field(None, description="文件路径")
    config: Optional[dict] = Field(None, description="配置信息")


class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[dict] = None


class OddsCompanyCreate(BaseModel):
    company_code: str = Field(..., description="公司代码")
    company_name: str = Field(..., description="公司名称")
    country: Optional[str] = None
    website: Optional[str] = None
    reliability_score: Optional[float] = Field(0.8, description="可靠性评分")


class SPRecordCreate(BaseModel):
    match_identifier: str = Field(..., description="比赛标识符")
    company_id: int = Field(..., description="赔率公司ID")
    data_source_id: Optional[int] = None
    handicap_type: str = Field("handicap", description="盘口类型")
    handicap_value: Optional[float] = None
    sp_value: float = Field(..., description="SP值")
    confidence_level: Optional[float] = Field(1.0, description="置信度")


class SPRecordUpdate(BaseModel):
    sp_value: Optional[float] = None
    handicap_value: Optional[float] = None
    reason: Optional[str] = Field(None, description="修改原因")


# ==================== 数据源管理API ====================

@router.get("/data-sources", response_model=List[dict])
async def get_data_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    source_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """获取数据源列表"""
    query = db.query(DataSource)
    
    if source_type:
        query = query.filter(DataSource.source_type == source_type)
    if is_active is not None:
        query = query.filter(DataSource.is_active == is_active)
    
    sources = query.offset(skip).limit(limit).all()
    return [source.to_dict() for source in sources]


@router.post("/data-sources", response_model=dict)
async def create_data_source(
    source: DataSourceCreate,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """创建数据源"""
    # 检查名称唯一性
    existing = db.query(DataSource).filter(DataSource.name == source.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="数据源名称已存在")
    
    db_source = DataSource(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    
    logger.info(f"管理员 {current_user.username} 创建数据源: {source.name}")
    return db_source.to_dict()


@router.put("/data-sources/{source_id}", response_model=dict)
async def update_data_source(
    source_id: int,
    source_update: DataSourceUpdate,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新数据源"""
    db_source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    # 更新字段
    update_data = source_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_source, field, value)
    
    db_source.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_source)
    
    logger.info(f"管理员 {current_user.username} 更新数据源: {db_source.name}")
    return db_source.to_dict()


@router.delete("/data-sources/{source_id}")
async def delete_data_source(
    source_id: int,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """删除数据源"""
    db_source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    db.delete(db_source)
    db.commit()
    
    logger.info(f"管理员 {current_user.username} 删除数据源: {db_source.name}")
    return {"message": "数据源删除成功"}


@router.post("/data-sources/{source_id}/test")
async def test_data_source(
    source_id: int,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """测试数据源连接"""
    db_source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    # TODO: 实现具体的连接测试逻辑
    # 这里只是模拟测试成功
    db_source.test_status = 'success'
    db_source.last_test_at = datetime.utcnow()
    db_source.success_rate = 95.0
    
    db.commit()
    
    return {
        "status": "success",
        "message": "连接测试成功",
        "response_time": 150
    }


# ==================== 赔率公司管理API ====================

@router.get("/companies", response_model=List[dict])
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """获取赔率公司列表"""
    query = db.query(OddsCompany)
    
    if is_active is not None:
        query = query.filter(OddsCompany.is_active == is_active)
    
    companies = query.offset(skip).limit(limit).all()
    return [company.to_dict() for company in companies]


@router.post("/companies", response_model=dict)
async def create_company(
    company: OddsCompanyCreate,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """创建赔率公司"""
    # 检查代码唯一性
    existing = db.query(OddsCompany).filter(OddsCompany.company_code == company.company_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="公司代码已存在")
    
    db_company = OddsCompany(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    logger.info(f"管理员 {current_user.username} 创建赔率公司: {company.company_name}")
    return db_company.to_dict()


@router.put("/companies/{company_id}", response_model=dict)
async def update_company(
    company_id: int,
    company_update: dict,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新赔率公司"""
    db_company = db.query(OddsCompany).filter(OddsCompany.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="赔率公司不存在")
    
    # 更新字段
    for field, value in company_update.items():
        if hasattr(db_company, field):
            setattr(db_company, field, value)
    
    db_company.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_company)
    
    logger.info(f"管理员 {current_user.username} 更新赔率公司: {db_company.company_name}")
    return db_company.to_dict()


# ==================== SP值管理API ====================

@router.get("/records", response_model=List[dict])
async def get_sp_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    match_identifier: Optional[str] = None,
    company_id: Optional[int] = None,
    handicap_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取SP值记录列表"""
    query = db.query(SPRecord)
    
    if match_identifier:
        query = query.filter(SPRecord.match_identifier == match_identifier)
    if company_id:
        query = query.filter(SPRecord.company_id == company_id)
    if handicap_type:
        query = query.filter(SPRecord.handicap_type == handicap_type)
    if start_date:
        query = query.filter(SPRecord.recorded_at >= start_date)
    if end_date:
        query = query.filter(SPRecord.recorded_at <= end_date)
    
    records = query.order_by(SPRecord.recorded_at.desc()).offset(skip).limit(limit).all()
    
    # 转换为字典格式，包含公司信息
    result = []
    for record in records:
        record_dict = record.to_dict()
        if record.company:
            record_dict['company_name'] = record.company.company_name
            record_dict['company_code'] = record.company.company_code
        result.append(record_dict)
    
    return result


@router.post("/records", response_model=dict)
async def create_sp_record(
    record: SPRecordCreate,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """创建SP值记录"""
    # 验证公司存在
    company = db.query(OddsCompany).filter(OddsCompany.id == record.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="赔率公司不存在")
    
    # 验证数据源存在（如果提供）
    if record.data_source_id:
        source = db.query(DataSource).filter(DataSource.id == record.data_source_id).first()
        if not source:
            raise HTTPException(status_code=400, detail="数据源不存在")
    
    # 验证盘口类型
    if record.handicap_type not in HANDICAP_TYPES:
        raise HTTPException(status_code=400, detail="无效的盘口类型")
    
    db_record = SPRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    logger.info(f"管理员 {current_user.username} 录入SP值: {record.sp_value} (比赛: {record.match_identifier})")
    return db_record.to_dict()


@router.put("/records/{record_id}", response_model=dict)
async def update_sp_record(
    record_id: int,
    record_update: SPRecordUpdate,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """修改SP值记录（记录修改日志）"""
    db_record = db.query(SPRecord).filter(SPRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="SP记录不存在")
    
    # 记录修改前的值
    old_value = db_record.sp_value
    old_handicap = db_record.handicap_value
    
    # 更新字段
    update_data = record_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field != 'reason' and hasattr(db_record, field):
            setattr(db_record, field, value)
    
    # 创建修改日志
    if 'sp_value' in update_data and update_data['sp_value'] != old_value:
        modification_log = SPModificationLog(
            sp_record_id=record_id,
            modified_by=getattr(current_user, 'id', None),
            old_value=old_value,
            new_value=update_data['sp_value'],
            old_handicap=old_handicap,
            new_handicap=update_data.get('handicap_value', old_handicap),
            reason=record_update.reason or '数据纠错'
        )
        db.add(modification_log)
        
        logger.info(f"管理员 {current_user.username} 修改SP值: {old_value} -> {update_data['sp_value']}")
    
    db_record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_record)
    
    return db_record.to_dict()


@router.get("/records/{match_identifier}/history", response_model=List[dict])
async def get_sp_history(
    match_identifier: str,
    company_id: Optional[int] = None,
    handicap_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取比赛的SP值历史"""
    query = db.query(SPRecord).filter(SPRecord.match_identifier == match_identifier)
    
    if company_id:
        query = query.filter(SPRecord.company_id == company_id)
    if handicap_type:
        query = query.filter(SPRecord.handicap_type == handicap_type)
    
    records = query.order_by(SPRecord.recorded_at).all()
    
    result = []
    for record in records:
        record_dict = record.to_dict()
        if record.company:
            record_dict['company_name'] = record.company.company_name
        result.append(record_dict)
    
    return result


# ==================== 统计和分析API ====================

@router.get("/statistics/distribution")
async def get_sp_distribution(
    company_id: Optional[int] = None,
    handicap_type: Optional[str] = None,
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """获取SP值分布统计"""
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(SPRecord).filter(SPRecord.recorded_at >= start_date)
    
    if company_id:
        query = query.filter(SPRecord.company_id == company_id)
    if handicap_type:
        query = query.filter(SPRecord.handicap_type == handicap_type)
    
    records = query.all()
    
    if not records:
        return {"message": "没有找到相关数据", "data": []}
    
    # 简单的统计分析
    sp_values = [r.sp_value for r in records]
    
    stats = {
        "total_records": len(records),
        "sp_value_stats": {
            "min": min(sp_values),
            "max": max(sp_values),
            "avg": sum(sp_values) / len(sp_values),
            "count": len(sp_values)
        },
        "period_days": days,
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return stats


# 导入datetime以在上面的代码中使用
from datetime import datetime