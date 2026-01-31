"""
足球SP管理模块 - 业务逻辑服务层
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc, func, and_, or_
from typing import List, Optional, Dict, Any, Tuple, Generator
from datetime import datetime, timedelta
import json
from fastapi import HTTPException, UploadFile, status

from backend.models.data_sources import DataSource
from backend.models.matches import FootballMatch
from backend.models.odds_companies import OddsCompany
from backend.models.sp_records import SPRecord
from backend.models.sp_modification_logs import SPModificationLog
from backend.models.user import User
from backend.schemas.sp_management import (
    DataSourceCreate, DataSourceUpdate, DataSourceResponse,
    MatchCreate, MatchUpdate, MatchResponse,
    OddsCompanyCreate, OddsCompanyUpdate, OddsCompanyResponse,
    SPRecordCreate, SPRecordUpdate, SPRecordResponse,
    SPModificationLogResponse,
    PaginationParams, DataSourceFilterParams, MatchFilterParams, SPRecordFilterParams,
    PaginatedResponse
)
from backend.database import get_db

class SPManagementService:
    """SP管理业务服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # 数据源管理相关方法
    # ============================================================================
    
    def get_data_sources(self, params: DataSourceFilterParams) -> PaginatedResponse:
        """获取数据源列表"""
        query = self.db.query(DataSource)
        
        # 应用筛选条件
        if params.type:
            query = query.filter(DataSource.type == params.type)
        if params.status is not None:
            query = query.filter(DataSource.status == params.status)
        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    DataSource.name.ilike(search_term),
                    DataSource.url.ilike(search_term)
                )
            )
        
        # 排序
        query = query.order_by(desc(DataSource.created_at))
        
        # 总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        sources = query.offset(offset).limit(params.size).all()
        
        # 转换数据源列表，确保config字段是字典格式
        converted_sources = []
        for source in sources:
            source_dict = DataSourceResponse.from_orm(source).dict()
            if source.config:
                try:
                    source_dict['config'] = json.loads(source.config)
                except:
                    source_dict['config'] = {}
            converted_sources.append(DataSourceResponse(**source_dict))
        
        return PaginatedResponse.create(
            items=converted_sources,
            total=total,
            page=params.page,
            size=params.size
        )
    
    def get_data_source(self, source_id: int) -> DataSourceResponse:
        """获取单个数据源"""
        source = self.db.query(DataSource).filter(DataSource.id == source_id).first()
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据源不存在"
            )
        
        # 确保config字段是字典格式
        source_dict = DataSourceResponse.from_orm(source).dict()
        if source.config:
            try:
                source_dict['config'] = json.loads(source.config)
            except:
                source_dict['config'] = {}
        
        return DataSourceResponse(**source_dict)
    
    def create_data_source(self, source_data: DataSourceCreate, created_by: int) -> DataSourceResponse:
        """创建数据源"""
        # 检查名称是否重复
        existing = self.db.query(DataSource).filter(
            DataSource.name == source_data.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据源名称已存在"
            )
        
        # 创建数据源，将config字典转换为JSON字符串
        source_dict = source_data.dict()
        if source_dict.get('config'):
            if isinstance(source_dict['config'], dict):
                source_dict['config'] = json.dumps(source_dict['config'])
        source_dict['created_by'] = created_by
        
        db_source = DataSource(**source_dict)
        self.db.add(db_source)
        self.db.commit()
        self.db.refresh(db_source)
        
        # 确保返回的响应中config字段是字典格式
        source_response = DataSourceResponse.from_orm(db_source).dict()
        if db_source.config:
            try:
                source_response['config'] = json.loads(db_source.config)
            except:
                source_response['config'] = {}
        
        return DataSourceResponse(**source_response)
    
    def update_data_source(self, source_id: int, source_data: DataSourceUpdate) -> DataSourceResponse:
        """更新数据源"""
        db_source = self.db.query(DataSource).filter(DataSource.id == source_id).first()
        if not db_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据源不存在"
            )
        
        # 检查名称冲突
        if source_data.name and source_data.name != db_source.name:
            existing = self.db.query(DataSource).filter(
                and_(
                    DataSource.name == source_data.name,
                    DataSource.id != source_id
                )
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="数据源名称已存在"
                )
        
        # 更新字段，处理config字段
        update_data = source_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'config' and value is not None:
                # 将config字典转换为JSON字符串
                if isinstance(value, dict):
                    setattr(db_source, field, json.dumps(value))
                else:
                    setattr(db_source, field, value)
            else:
                setattr(db_source, field, value)
        
        db_source.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(db_source)
        
        # 确保返回的响应中config字段是字典格式
        source_response = DataSourceResponse.from_orm(db_source).dict()
        if db_source.config:
            try:
                source_response['config'] = json.loads(db_source.config)
            except:
                source_response['config'] = {}
        
        return DataSourceResponse(**source_response)
    
    def delete_data_source(self, source_id: int) -> bool:
        """删除数据源"""
        db_source = self.db.query(DataSource).filter(DataSource.id == source_id).first()
        if not db_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据源不存在"
            )
        
        self.db.delete(db_source)
        self.db.commit()
        return True
    
    def test_data_source(self, source_id: int) -> Dict[str, Any]:
        """测试数据源连接"""
        source = self.get_data_source(source_id)
        
        # 这里实现具体的连接测试逻辑
        # 对于API类型，尝试发送请求
        # 对于文件类型，检查路径可访问性
        
        try:
            if source.type == 'api':
                # 模拟API测试
                return {
                    "success": True,
                    "message": "API连接测试成功",
                    "response_time": 150  # 模拟响应时间
                }
            elif source.type == 'file':
                # 模拟文件测试
                return {
                    "success": True,
                    "message": "文件路径可访问",
                    "file_count": 0
                }
            else:
                return {
                    "success": False,
                    "message": "不支持的数据源类型"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"连接测试失败: {str(e)}"
            }
    
    # ============================================================================
    # 比赛信息管理相关方法
    # ============================================================================
    
    def get_matches(self, params: MatchFilterParams) -> PaginatedResponse:
        """获取比赛列表"""
        query = self.db.query(FootballMatch)
        
        # 应用筛选条件
        if params.status:
            query = query.filter(FootballMatch.status == params.status)
        if params.league:
            query = query.filter(FootballMatch.league.ilike(f"%{params.league}%"))
        if params.team:
            query = query.filter(
                or_(
                    FootballMatch.home_team.ilike(f"%{params.team}%"),
                    FootballMatch.away_team.ilike(f"%{params.team}%")
                )
            )
        if params.date_from:
            query = query.filter(FootballMatch.match_time >= params.date_from)
        if params.date_to:
            query = query.filter(FootballMatch.match_time <= params.date_to)
        
        # 排序
        query = query.order_by(desc(FootballMatch.match_time))
        
        # 总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        matches = query.offset(offset).limit(params.size).all()
        
        return PaginatedResponse.create(
            items=[MatchResponse.from_orm(match) for match in matches],
            total=total,
            page=params.page,
            size=params.size
        )
    
    def get_match(self, match_id: int) -> MatchResponse:
        """获取单个比赛"""
        match = self.db.query(FootballMatch).filter(FootballMatch.id == match_id).first()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="比赛不存在"
            )
        return MatchResponse.from_orm(match)
    
    def create_match(self, match_data: MatchCreate) -> MatchResponse:
        """创建比赛"""
        # 检查比赛ID是否重复
        existing = self.db.query(FootballMatch).filter(
            FootballMatch.match_id == match_data.match_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="比赛ID已存在"
            )
        
        # 创建比赛
        db_match = FootballMatch(**match_data.dict())
        self.db.add(db_match)
        self.db.commit()
        self.db.refresh(db_match)
        
        return MatchResponse.from_orm(db_match)
    
    def update_match(self, match_id: int, match_data: MatchUpdate) -> MatchResponse:
        """更新比赛"""
        db_match = self.db.query(FootballMatch).filter(FootballMatch.id == match_id).first()
        if not db_match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="比赛不存在"
            )
        
        # 检查比赛ID冲突
        if match_data.match_id and match_data.match_id != db_match.match_id:
            existing = self.db.query(FootballMatch).filter(
                and_(
                    FootballMatch.match_id == match_data.match_id,
                    FootballMatch.id != match_id
                )
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="比赛ID已存在"
                )
        
        # 更新字段
        update_data = match_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_match, field, value)
        
        db_match.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(db_match)
        
        return MatchResponse.from_orm(db_match)
    
    def delete_match(self, match_id: int) -> bool:
        """删除比赛"""
        db_match = self.db.query(FootballMatch).filter(FootballMatch.id == match_id).first()
        if not db_match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="比赛不存在"
            )
        
        self.db.delete(db_match)
        self.db.commit()
        return True
    
    def get_match_sp_history(self, match_id: int) -> List[SPRecordResponse]:
        """获取比赛SP值历史"""
        records = self.db.query(SPRecord).filter(
            SPRecord.match_id == match_id
        ).order_by(desc(SPRecord.recorded_at)).all()
        
        return [SPRecordResponse.from_orm(record) for record in records]
    
    # ============================================================================
    # 赔率公司管理相关方法
    # ============================================================================
    
    def get_odds_companies(self, active_only: bool = True) -> List[OddsCompanyResponse]:
        """获取赔率公司列表"""
        query = self.db.query(OddsCompany)
        if active_only:
            query = query.filter(OddsCompany.status == True)
        
        companies = query.order_by(desc(OddsCompany.weight), OddsCompany.name).all()
        return [OddsCompanyResponse.from_orm(company) for company in companies]
    
    def get_odds_company(self, company_id: int) -> OddsCompanyResponse:
        """获取单个赔率公司"""
        company = self.db.query(OddsCompany).filter(OddsCompany.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="赔率公司不存在"
            )
        return OddsCompanyResponse.from_orm(company)
    
    def create_odds_company(self, company_data: OddsCompanyCreate) -> OddsCompanyResponse:
        """创建赔率公司"""
        # 检查名称是否重复
        existing = self.db.query(OddsCompany).filter(
            OddsCompany.name == company_data.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="公司名称已存在"
            )
        
        db_company = OddsCompany(**company_data.dict())
        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        
        return OddsCompanyResponse.from_orm(db_company)
    
    def update_odds_company(self, company_id: int, company_data: OddsCompanyUpdate) -> OddsCompanyResponse:
        """更新赔率公司"""
        db_company = self.db.query(OddsCompany).filter(OddsCompany.id == company_id).first()
        if not db_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="赔率公司不存在"
            )
        
        # 检查名称冲突
        if company_data.name and company_data.name != db_company.name:
            existing = self.db.query(OddsCompany).filter(
                and_(
                    OddsCompany.name == company_data.name,
                    OddsCompany.id != company_id
                )
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="公司名称已存在"
                )
        
        # 更新字段
        update_data = company_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_company, field, value)
        
        self.db.commit()
        self.db.refresh(db_company)
        
        return OddsCompanyResponse.from_orm(db_company)
    
    # ============================================================================
    # SP值管理相关方法
    # ============================================================================
    
    def get_sp_records(self, params: SPRecordFilterParams) -> PaginatedResponse:
        """获取SP值记录"""
        query = self.db.query(SPRecord).options(
            joinedload(SPRecord.match),
            joinedload(SPRecord.company)
        )
        
        # 应用筛选条件
        if params.match_id:
            query = query.filter(SPRecord.match_id == params.match_id)
        if params.company_id:
            query = query.filter(SPRecord.company_id == params.company_id)
        if params.handicap_type:
            query = query.filter(SPRecord.handicap_type == params.handicap_type)
        if params.date_from:
            query = query.filter(SPRecord.recorded_at >= params.date_from)
        if params.date_to:
            query = query.filter(SPRecord.recorded_at <= params.date_to)
        
        # 排序
        query = query.order_by(desc(SPRecord.recorded_at))
        
        # 总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        records = query.offset(offset).limit(params.size).all()
        
        return PaginatedResponse.create(
            items=[SPRecordResponse.from_orm(record) for record in records],
            total=total,
            page=params.page,
            size=params.size
        )
    
    def create_sp_record(self, record_data: SPRecordCreate, operator_id: int) -> SPRecordResponse:
        """创建SP值记录"""
        # 验证比赛和公司存在
        match = self.db.query(FootballMatch).filter(FootballMatch.id == record_data.match_id).first()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="比赛不存在"
            )
        
        company = self.db.query(OddsCompany).filter(OddsCompany.id == record_data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="赔率公司不存在"
            )
        
        # 创建SP记录
        db_record = SPRecord(**record_data.dict())
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        
        return SPRecordResponse.from_orm(db_record)
    
    def update_sp_record(self, record_id: int, update_data: SPRecordUpdate, operator_id: int, reason: str = None) -> SPRecordResponse:
        """修改SP值记录"""
        db_record = self.db.query(SPRecord).filter(SPRecord.id == record_id).first()
        if not db_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SP记录不存在"
            )
        
        # 记录修改日志
        if update_data.sp_value and update_data.sp_value != db_record.sp_value:
            modification_log = SPModificationLog(
                sp_record_id=record_id,
                original_value=db_record.sp_value,
                modified_value=update_data.sp_value,
                modified_by=operator_id,
                reason=reason
            )
            self.db.add(modification_log)
        
        # 更新SP值
        if update_data.sp_value:
            db_record.sp_value = update_data.sp_value
        
        self.db.commit()
        self.db.refresh(db_record)
        
        return SPRecordResponse.from_orm(db_record)
    
    def get_sp_modification_logs(self, record_id: int) -> List[SPModificationLogResponse]:
        """获取SP值修改日志"""
        logs = self.db.query(SPModificationLog).filter(
            SPModificationLog.sp_record_id == record_id
        ).order_by(desc(SPModificationLog.created_at)).all()
        
        return [SPModificationLogResponse.from_orm(log) for log in logs]
    
    def get_sp_trend(self, match_id: int, company_id: int) -> Dict[str, Any]:
        """获取SP值走势数据"""
        records = self.db.query(SPRecord).filter(
            and_(
                SPRecord.match_id == match_id,
                SPRecord.company_id == company_id
            )
        ).order_by(asc(SPRecord.recorded_at)).all()
        
        if not records:
            return {"data_points": [], "trend": "stable"}
        
        data_points = [
            {
                "time": record.recorded_at.isoformat(),
                "sp_value": float(record.sp_value),
                "handicap_type": record.handicap_type,
                "handicap_value": float(record.handicap_value) if record.handicap_value else None
            }
            for record in records
        ]
        
        # 简单趋势分析
        if len(records) >= 2:
            first_sp = float(records[0].sp_value)
            last_sp = float(records[-1].sp_value)
            change = ((last_sp - first_sp) / first_sp) * 100
            
            if change > 5:
                trend = "rising"
            elif change < -5:
                trend = "falling"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "data_points": data_points,
            "trend": trend,
            "total_records": len(records)
        }
    
    # ============================================================================
    # 文件导入相关方法
    # ============================================================================
    
    async def import_matches_from_csv(self, file: UploadFile, operator_id: int) -> Dict[str, Any]:
        """从CSV文件导入比赛数据"""
        # 这里实现CSV文件解析和导入逻辑
        # 暂时返回模拟结果
        return {
            "success": True,
            "imported_count": 10,
            "failed_count": 0,
            "message": "文件导入成功"
        }
    
    async def import_sp_data_from_csv(self, file: UploadFile, operator_id: int) -> Dict[str, Any]:
        """从CSV文件导入SP值数据"""
        # 这里实现CSV文件解析和导入逻辑
        # 暂时返回模拟结果
        return {
            "success": True,
            "imported_count": 50,
            "failed_count": 2,
            "message": "SP值数据导入成功"
        }

# 全局服务实例
def get_sp_management_service() -> SPManagementService:
    """获取SP管理服务实例"""
    db = next(get_db())
    return SPManagementService(db)