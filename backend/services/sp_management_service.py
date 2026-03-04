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

    @staticmethod
    def _status_to_db(value: Any, default: int = 1) -> int:
        """Normalize API status values to DB integer status (1=online, 0=offline)."""
        if value is None:
            return default

        if isinstance(value, bool):
            return 1 if value else 0

        if isinstance(value, (int, float)):
            return 1 if int(value) != 0 else 0

        if isinstance(value, str):
            normalized = value.strip().lower()
            if not normalized:
                return default

            mapping = {
                "online": 1,
                "offline": 0,
                "maintenance": 0,
                "error": 0,
                "true": 1,
                "false": 0,
                "yes": 1,
                "no": 0,
                "on": 1,
                "off": 0,
                "enabled": 1,
                "disabled": 0,
                "1": 1,
                "0": 0,
            }
            if normalized in mapping:
                return mapping[normalized]

            if normalized.lstrip("-").isdigit():
                return 1 if int(normalized) != 0 else 0

        return default

    @staticmethod
    def _status_to_api(value: Any) -> str:
        """Normalize DB status values to API string status."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in ("online", "offline"):
                return normalized
            if normalized in ("1", "true", "yes", "on", "enabled"):
                return "online"
            if normalized in ("0", "false", "no", "off", "disabled"):
                return "offline"
            return "online"

        if isinstance(value, bool):
            return "online" if value else "offline"

        if isinstance(value, (int, float)):
            return "online" if int(value) != 0 else "offline"

        return "online"
    
    # ============================================================================
    # 数据源管理相关方法
    # ============================================================================
    
    def get_data_sources(self, params: DataSourceFilterParams) -> PaginatedResponse:
        """获取数据源列表"""
        # 使用原生SQL查询以绕过ORM映射问题
        from sqlalchemy import text
        
        # 构建基础查询
        base_query = """
            SELECT id, source_id, name, type, status, url, config, 
                   last_update, error_rate, created_at, updated_at, created_by,
                   last_error, last_error_time
            FROM data_sources
        """
        count_query = "SELECT COUNT(*) FROM data_sources"
        conditions = []
        params_values = {}
        
        # 应用筛选条件
        if params.type:
            conditions.append("type = :type")
            params_values['type'] = params.type
        if params.status is not None:
            conditions.append("status = :status")
            params_values['status'] = self._status_to_db(params.status)
        if params.search:
            conditions.append("(name LIKE :search OR url LIKE :search)")
            params_values['search'] = f"%{params.search}%"
        # 添加内容分类筛选 - 确保只查找config中确实包含category字段且值匹配的记录
        if params.category:
            # 使用适合SQLite的方式处理JSON查询，如果SQLite版本较低则回退到LIKE查询
            # 这里我们使用LIKE查询作为更兼容的方式
            conditions.append("config LIKE :category_pattern")
            params_values['category_pattern'] = f'%category%{params.category}%'
        # 添加源ID筛选
        if params.source_id:
            conditions.append("source_id = :source_id")
            params_values['source_id'] = params.source_id
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
            count_query += " WHERE " + " AND ".join(conditions)
        
        # 排序
        base_query += " ORDER BY created_at DESC"
        
        # 执行总数查询
        count_result = self.db.execute(text(count_query), params_values).fetchone()
        total = count_result[0]
        
        # 分页查询 - 修正：将LIMIT和OFFSET放在ORDER BY之后
        offset = (params.page - 1) * params.size
        final_query = base_query + f" LIMIT {params.size} OFFSET {offset}"
        result = self.db.execute(text(final_query), params_values)  # 修正参数传递
        
        rows = result.fetchall()
        
        # 转换为字典格式
        converted_sources = []
        for row in rows:
            # 将状态数字转换为字符串
            status_val = row[4]
            if isinstance(status_val, int):
                # 假设1代表'online'，0代表'offline'，其他值可以根据需要映射
                if status_val == 1:
                    status_str = 'online'
                elif status_val == 0:
                    status_str = 'offline'
                else:
                    status_str = 'online'  # 默认值
            else:
                status_str = status_val
            
            status_str = self._status_to_api(row[4])
            source_dict = {
                'id': row[0],
                'source_id': row[1] or f"DS{row[0]:03d}",  # 确保source_id被包含
                'name': row[2],
                'type': row[3],
                'status': status_str,  # 使用转换后的状态字符串
                'url': row[5],
                'config': json.loads(row[6]) if row[6] else {},
                'last_update': row[7],
                'error_rate': row[8],
                'created_at': row[9],
                'updated_at': row[10],
                'created_by': row[11],
                'last_error': row[12],  # 新增字段
                'last_error_time': row[13]  # 新增字段
            }
            converted_sources.append(DataSourceResponse(**source_dict))
        
        return PaginatedResponse.create(
            items=converted_sources,
            total=total,
            page=params.page,
            size=params.size
        )
    
    def get_data_source(self, source_id: int) -> DataSourceResponse:
        """获取单个数据源"""
        # 使用原生SQL查询以绕过ORM映射问题
        from sqlalchemy import text
        
        query = """
            SELECT id, source_id, name, type, status, url, config, 
                   last_update, error_rate, created_at, updated_at, created_by,
                   last_error, last_error_time
            FROM data_sources
            WHERE id = :source_id
        """
        
        result = self.db.execute(text(query), {'source_id': source_id}).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据源不存在"
            )
        
        # 将状态数字转换为字符串
        status_val = result[4]
        if isinstance(status_val, int):
            # 假设1代表'online'，0代表'offline'，其他值可以根据需要映射
            if status_val == 1:
                status_str = 'online'
            elif status_val == 0:
                status_str = 'offline'
            else:
                status_str = 'online'  # 默认值
        else:
            status_str = status_val
        
        status_str = self._status_to_api(result[4])
        source_dict = {
            'id': result[0],
            'source_id': result[1] or f"DS{result[0]:03d}",
            'name': result[2],
            'type': result[3],
            'status': status_str,  # 使用转换后的状态字符串
            'url': result[5],
            'config': json.loads(result[6]) if result[6] else {},
            'last_update': result[7],
            'error_rate': result[8],
            'created_at': result[9],
            'updated_at': result[10],
            'created_by': result[11],
            'last_error': result[12],  # 新增字段
            'last_error_time': result[13]  # 新增字段
        }
        
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
        if 'config' in source_dict and source_dict['config'] is not None:
            if isinstance(source_dict['config'], dict):
                source_dict['config'] = json.dumps(source_dict['config'], ensure_ascii=False)
            # 如果config已经是字符串，保持不变
        else:
            # 如果没有提供config，设置为默认的空JSON字符串
            source_dict['config'] = '{}'
        
        source_dict['status'] = self._status_to_db(source_dict.get('status'))
        source_dict['created_by'] = created_by
        
        # 先不设置source_id，让它为None，稍后在保存后设置
        db_source = DataSource(**source_dict)
        self.db.add(db_source)
        self.db.commit()
        self.db.refresh(db_source)  # 获取数据库生成的ID
        
        # 现在设置source_id为DS+3位数字ID格式
        db_source.source_id = f"DS{db_source.id:03d}"
        self.db.commit()
        self.db.refresh(db_source)
        
        # 使用字典方式构建响应，确保source_id被正确包含
        source_response = {
            'id': db_source.id,
            'source_id': db_source.source_id or f"DS{db_source.id:03d}",
            'name': db_source.name,
            'type': db_source.type,
            'status': self._status_to_api(db_source.status),
            'url': db_source.url,
            'config': db_source.config_dict,  # 使用属性获取字典格式的配置
            'last_update': db_source.last_update,
            'error_rate': db_source.error_rate,
            'created_at': db_source.created_at,
            'updated_at': db_source.updated_at,
            'created_by': db_source.created_by
        }
        
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
                    setattr(db_source, field, json.dumps(value, ensure_ascii=False))
                else:
                    setattr(db_source, field, value)
            elif field == 'status':
                setattr(
                    db_source,
                    field,
                    self._status_to_db(
                        value,
                        default=self._status_to_db(db_source.status)
                    )
                )
            else:
                setattr(db_source, field, value)
        
        db_source.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(db_source)
        
        # 确保返回的响应中config字段是字典格式，并处理状态字段
        source_dict = {
            'id': db_source.id,
            'source_id': db_source.source_id or f"DS{db_source.id:03d}",
            'name': db_source.name,
            'type': db_source.type,
            'status': self._status_to_api(db_source.status),
            'url': db_source.url,
            'config': db_source.config_dict if hasattr(db_source, 'config_dict') else (json.loads(db_source.config) if db_source.config else {}),
            'last_update': db_source.last_update,
            'error_rate': db_source.error_rate,
            'created_at': db_source.created_at,
            'updated_at': db_source.updated_at,
            'created_by': db_source.created_by,
            'last_error': db_source.last_error,
            'last_error_time': db_source.last_error_time
        }
        
        return DataSourceResponse(**source_dict)
    
    def delete_data_source(self, source_id: int) -> bool:
        """删除数据源"""
        # 使用原生SQL检查并删除，避免关系加载问题
        from sqlalchemy import text
        
        # 先检查是否存在
        check_query = text("SELECT id FROM data_sources WHERE id = :source_id")
        result = self.db.execute(check_query, {'source_id': source_id}).fetchone()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据源不存在"
            )
        
        # 执行删除，让数据库外键约束处理关联记录（ON DELETE SET NULL）
        delete_query = text("DELETE FROM data_sources WHERE id = :source_id")
        self.db.execute(delete_query, {'source_id': source_id})
        self.db.commit()
        return True
    
    def batch_delete_data_sources(self, source_ids: List[int]) -> int:
        """批量删除数据源"""
        # 首先检查所有要删除的数据源是否存在
        sources_to_delete = self.db.query(DataSource).filter(DataSource.id.in_(source_ids)).all()
        
        # 检查是否存在不存在的数据源
        existing_ids = {source.id for source in sources_to_delete}
        requested_ids = set(source_ids)
        missing_ids = requested_ids - existing_ids
        
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"以下数据源不存在: {list(missing_ids)}"
            )
        
        # 直接删除数据源，避免加载关联对象
        deleted_count = 0
        for source in sources_to_delete:
            # 先更新关联的爬虫配置，将source_id设为NULL
            from backend.models.crawler_config import CrawlerConfig
            self.db.query(CrawlerConfig).filter(CrawlerConfig.source_id == source.id).update({CrawlerConfig.source_id: None})
            
            # 然后删除数据源
            self.db.delete(source)
            deleted_count += 1
        
        self.db.commit()
        return deleted_count
    
    def test_data_source(self, source_id: int) -> Dict[str, Any]:
        """测试数据源连接"""
        source = self.get_data_source(source_id)
        
        # 这里实现具体的连接测试逻辑
        # 对于API类型，尝试发送请求
        # 对于文件类型，检查路径可访问性
        
        try:
            if source.type == 'api':
                # 模拟API测试 - 在实际实现中应替换为真实的连接测试
                # 这里暂时使用模拟逻辑
                import random
                # 模拟连接测试，随机成功或失败以演示错误状态
                if random.random() < 0.3:  # 30%概率失败
                    error_msg = "API连接测试失败：网络超时或服务不可达"
                    # 更新数据源状态为错误
                    update_data = {
                        "status": "error",
                        "last_error": error_msg,
                        "last_error_time": datetime.utcnow()
                    }
                    self.update_data_source_fields(source_id, update_data)
                    
                    return {
                        "success": False,
                        "message": error_msg,
                        "status": "error"
                    }
                else:
                    # 成功时更新状态为online并清除错误信息
                    update_data = {
                        "status": "online",
                        "last_error": None,
                        "last_error_time": None
                    }
                    self.update_data_source_fields(source_id, update_data)
                    
                    return {
                        "success": True,
                        "message": "API连接测试成功",
                        "response_time": 150,  # 模拟响应时间
                        "status": "online"
                    }
            elif source.type == 'file':
                # 模拟文件测试
                import os
                if source.url and os.path.exists(source.url):
                    # 文件存在则成功
                    update_data = {
                        "status": "online",
                        "last_error": None,
                        "last_error_time": None
                    }
                    self.update_data_source_fields(source_id, update_data)
                    
                    return {
                        "success": True,
                        "message": "文件路径可访问",
                        "file_count": 1,
                        "status": "online"
                    }
                else:
                    error_msg = f"文件路径不可访问: {source.url}"
                    # 更新数据源状态为错误
                    update_data = {
                        "status": "error",
                        "last_error": error_msg,
                        "last_error_time": datetime.utcnow()
                    }
                    self.update_data_source_fields(source_id, update_data)
                    
                    return {
                        "success": False,
                        "message": error_msg,
                        "status": "error"
                    }
            else:
                error_msg = "不支持的数据源类型"
                # 更新数据源状态为错误
                update_data = {
                    "status": "error",
                    "last_error": error_msg,
                    "last_error_time": datetime.utcnow()
                }
                self.update_data_source_fields(source_id, update_data)
                
                return {
                    "success": False,
                    "message": error_msg,
                    "status": "error"
                }
        except Exception as e:
            error_msg = f"连接测试失败: {str(e)}"
            # 更新数据源状态为错误
            update_data = {
                "status": "error",
                "last_error": error_msg,
                "last_error_time": datetime.utcnow()
            }
            self.update_data_source_fields(source_id, update_data)
            
            return {
                "success": False,
                "message": error_msg,
                "status": "error"
            }
    
    def update_data_source_fields(self, source_id: int, update_data: dict):
        """更新数据源字段"""
        db_source = self.db.query(DataSource).filter(DataSource.id == source_id).first()
        if not db_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据源不存在"
            )
        
        # 更新字段
        for field, value in update_data.items():
            if field == "status":
                setattr(
                    db_source,
                    field,
                    self._status_to_db(
                        value,
                        default=self._status_to_db(db_source.status)
                    )
                )
            else:
                setattr(db_source, field, value)
        
        db_source.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(db_source)
    
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
