"""
足球SP管理模块 - API控制器层
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.services.sp_management_service import SPManagementService, get_sp_management_service
from backend.schemas.sp_management import (
    DataSourceCreate, DataSourceUpdate, DataSourceResponse,
    MatchCreate, MatchUpdate, MatchResponse,
    OddsCompanyCreate, OddsCompanyUpdate, OddsCompanyResponse,
    SPRecordCreate, SPRecordUpdate, SPRecordResponse,
    SPModificationLogResponse,
    PaginationParams, DataSourceFilterParams, MatchFilterParams, SPRecordFilterParams,
    PaginatedResponse
)
from backend.models.user import User
from backend.dependencies import get_current_active_user
from backend.core.auth import get_current_admin_user

router = APIRouter()
security = HTTPBearer(auto_error=False)

# =============================================================================
# 数据源管理API
# =============================================================================

@router.get(
    "/data-sources",
    response_model=PaginatedResponse[DataSourceResponse],
    summary="获取数据源列表",
    description="获取数据源列表，支持分页、筛选和搜索"
)
async def get_data_sources(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    type: Optional[str] = Query(None, description="数据源类型筛选"),
    status: Optional[bool] = Query(None, description="启用状态筛选"),
    search: Optional[str] = Query(None, max_length=50, description="搜索关键词"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取数据源列表"""
    params = DataSourceFilterParams(
        page=page,
        size=size,
        type=type,
        status=status,
        search=search
    )
    return service.get_data_sources(params)

@router.get(
    "/data-sources/{source_id}",
    response_model=DataSourceResponse,
    summary="获取数据源详情",
    description="根据ID获取数据源详细信息"
)
async def get_data_source(
    source_id: int,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取单个数据源"""
    return service.get_data_source(source_id)

@router.post(
    "/data-sources",
    response_model=DataSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建数据源",
    description="创建新的数据源配置"
)
async def create_data_source(
    source_data: DataSourceCreate,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可创建
):
    """创建数据源"""
    return service.create_data_source(source_data, current_user.id)

@router.put(
    "/data-sources/{source_id}",
    response_model=DataSourceResponse,
    summary="更新数据源",
    description="更新数据源配置信息"
)
async def update_data_source(
    source_id: int,
    source_data: DataSourceUpdate,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可更新
):
    """更新数据源"""
    return service.update_data_source(source_id, source_data)

@router.delete(
    "/data-sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除数据源",
    description="删除数据源配置"
)
async def delete_data_source(
    source_id: int,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可删除
):
    """删除数据源"""
    service.delete_data_source(source_id)
    return None

@router.post(
    "/data-sources/{source_id}/test",
    summary="测试数据源连接",
    description="测试数据源的连接状态"
)
async def test_data_source(
    source_id: int,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可测试
):
    """测试数据源连接"""
    return service.test_data_source(source_id)

@router.get(
    "/data-sources/api",
    response_model=PaginatedResponse[DataSourceResponse],
    summary="获取API类型数据源",
    description="获取所有API类型的数据源"
)
async def get_api_data_sources(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取API类型数据源"""
    params = DataSourceFilterParams(page=page, size=size, type='api')
    return service.get_data_sources(params)

@router.get(
    "/data-sources/file",
    response_model=PaginatedResponse[DataSourceResponse],
    summary="获取文件类型数据源",
    description="获取所有文件类型的数据源"
)
async def get_file_data_sources(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取文件类型数据源"""
    params = DataSourceFilterParams(page=page, size=size, type='file')
    return service.get_data_sources(params)

# =============================================================================
# 比赛信息管理API
# =============================================================================

@router.get(
    "/matches",
    response_model=PaginatedResponse[MatchResponse],
    summary="获取比赛列表",
    description="获取比赛列表，支持分页、筛选和搜索"
)
async def get_matches(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="比赛状态筛选"),
    league: Optional[str] = Query(None, max_length=50, description="联赛名称筛选"),
    team: Optional[str] = Query(None, max_length=50, description="队伍名称筛选"),
    date_from: Optional[datetime] = Query(None, description="开始日期"),
    date_to: Optional[datetime] = Query(None, description="结束日期"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取比赛列表"""
    params = MatchFilterParams(
        page=page,
        size=size,
        status=status,
        league=league,
        team=team,
        date_from=date_from,
        date_to=date_to
    )
    return service.get_matches(params)

@router.get(
    "/matches/{match_id}",
    response_model=MatchResponse,
    summary="获取比赛详情",
    description="根据ID获取比赛详细信息"
)
async def get_match(
    match_id: int,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取单个比赛"""
    return service.get_match(match_id)

@router.post(
    "/matches",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建比赛",
    description="创建新的比赛记录"
)
async def create_match(
    match_data: MatchCreate,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """创建比赛"""
    return service.create_match(match_data)

@router.put(
    "/matches/{match_id}",
    response_model=MatchResponse,
    summary="更新比赛",
    description="更新比赛信息"
)
async def update_match(
    match_id: int,
    match_data: MatchUpdate,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """更新比赛"""
    return service.update_match(match_id, match_data)

@router.delete(
    "/matches/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除比赛",
    description="删除比赛记录"
)
async def delete_match(
    match_id: int,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可删除
):
    """删除比赛"""
    service.delete_match(match_id)
    return None

@router.get(
    "/matches/{match_id}/sp-history",
    response_model=List[SPRecordResponse],
    summary="获取比赛SP值历史",
    description="获取指定比赛的所有SP值记录"
)
async def get_match_sp_history(
    match_id: int,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取比赛SP值历史"""
    return service.get_match_sp_history(match_id)

@router.get(
    "/matches/{match_id}/sp-chart",
    summary="获取SP值走势图数据",
    description="获取SP值走势图表数据"
)
async def get_sp_chart_data(
    match_id: int,
    company_id: Optional[int] = Query(None, description="指定赔率公司ID"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取SP值走势图数据"""
    # 如果指定了公司，获取该公司的走势
    if company_id:
        return service.get_sp_trend(match_id, company_id)
    
    # 否则获取所有公司的走势概览
    companies = service.get_odds_companies(active_only=True)
    trends = {}
    
    for company in companies:
        trends[company.short_name or company.name] = service.get_sp_trend(match_id, company.id)
    
    return {"match_id": match_id, "companies_trends": trends}

# =============================================================================
# 赔率公司管理API
# =============================================================================

@router.get(
    "/companies",
    response_model=List[OddsCompanyResponse],
    summary="获取赔率公司列表",
    description="获取所有启用的赔率公司"
)
async def get_odds_companies(
    active_only: bool = Query(True, description="仅返回启用的公司"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取赔率公司列表"""
    return service.get_odds_companies(active_only)

@router.get(
    "/companies/all",
    response_model=List[OddsCompanyResponse],
    summary="获取所有赔率公司",
    description="获取所有赔率公司（包括禁用的）"
)
async def get_all_odds_companies(
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可见
):
    """获取所有赔率公司"""
    return service.get_odds_companies(active_only=False)

@router.get(
    "/companies/{company_id}",
    response_model=OddsCompanyResponse,
    summary="获取赔率公司详情",
    description="根据ID获取赔率公司详细信息"
)
async def get_odds_company(
    company_id: int,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取单个赔率公司"""
    return service.get_odds_company(company_id)

@router.post(
    "/companies",
    response_model=OddsCompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建赔率公司",
    description="创建新的赔率公司"
)
async def create_odds_company(
    company_data: OddsCompanyCreate,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可创建
):
    """创建赔率公司"""
    return service.create_odds_company(company_data)

@router.put(
    "/companies/{company_id}",
    response_model=OddsCompanyResponse,
    summary="更新赔率公司",
    description="更新赔率公司信息"
)
async def update_odds_company(
    company_id: int,
    company_data: OddsCompanyUpdate,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可更新
):
    """更新赔率公司"""
    return service.update_odds_company(company_id, company_data)

# =============================================================================
# SP值管理API
# =============================================================================

@router.get(
    "/sp-records",
    response_model=PaginatedResponse[SPRecordResponse],
    summary="获取SP值记录",
    description="获取SP值记录列表，支持分页和筛选"
)
async def get_sp_records(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    match_id: Optional[int] = Query(None, description="比赛ID筛选"),
    company_id: Optional[int] = Query(None, description="公司ID筛选"),
    handicap_type: Optional[str] = Query(None, description="盘口类型筛选"),
    date_from: Optional[datetime] = Query(None, description="开始日期"),
    date_to: Optional[datetime] = Query(None, description="结束日期"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取SP值记录"""
    params = SPRecordFilterParams(
        page=page,
        size=size,
        match_id=match_id,
        company_id=company_id,
        handicap_type=handicap_type,
        date_from=date_from,
        date_to=date_to
    )
    return service.get_sp_records(params)

@router.post(
    "/sp-records",
    response_model=SPRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="录入SP值",
    description="手动录入SP值记录"
)
async def create_sp_record(
    record_data: SPRecordCreate,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """创建SP值记录"""
    return service.create_sp_record(record_data, current_user.id)

@router.put(
    "/sp-records/{record_id}",
    response_model=SPRecordResponse,
    summary="修改SP值",
    description="修改SP值记录（需记录修改日志）"
)
async def update_sp_record(
    record_id: int,
    update_data: SPRecordUpdate,
    reason: Optional[str] = Query(None, description="修改原因"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """修改SP值记录"""
    return service.update_sp_record(record_id, update_data, current_user.id, reason)

@router.get(
    "/sp-records/{record_id}/modifications",
    response_model=List[SPModificationLogResponse],
    summary="获取SP值修改日志",
    description="获取SP值记录的修改历史"
)
async def get_sp_modification_logs(
    record_id: int,
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取SP值修改日志"""
    return service.get_sp_modification_logs(record_id)

# =============================================================================
# 文件导入API
# =============================================================================

@router.post(
    "/matches/import/csv",
    summary="导入比赛数据",
    description="从CSV文件批量导入比赛数据"
)
async def import_matches_csv(
    file: UploadFile = File(..., description="CSV文件"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可导入
):
    """从CSV文件导入比赛数据"""
    # 验证文件类型
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持CSV文件格式"
        )
    
    return await service.import_matches_from_csv(file, current_user.id)

@router.post(
    "/sp-records/import/csv",
    summary="导入SP值数据",
    description="从CSV文件批量导入SP值数据"
)
async def import_sp_data_csv(
    file: UploadFile = File(..., description="CSV文件"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可导入
):
    """从CSV文件导入SP值数据"""
    # 验证文件类型
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持CSV文件格式"
        )
    
    return await service.import_sp_data_from_csv(file, current_user.id)

@router.post(
    "/data-sources/file/upload-template",
    summary="上传文件导入模板",
    description="上传文件导入模板"
)
async def upload_file_template(
    file: UploadFile = File(..., description="模板文件"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可上传
):
    """上传文件导入模板"""
    # 这里实现模板文件处理逻辑
    return {
        "success": True,
        "message": "模板上传成功",
        "filename": file.filename
    }

# =============================================================================
# 统计分析API
# =============================================================================

@router.get(
    "/analysis/distribution",
    summary="SP值分布统计",
    description="获取SP值分布统计分析"
)
async def get_sp_distribution_analysis(
    league: Optional[str] = Query(None, description="联赛筛选"),
    company_id: Optional[int] = Query(None, description="公司ID筛选"),
    handicap_type: Optional[str] = Query(None, description="盘口类型筛选"),
    date_from: Optional[datetime] = Query(None, description="开始日期"),
    date_to: Optional[datetime] = Query(None, description="结束日期"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """SP值分布统计分析"""
    # TODO: 实现详细的统计分析逻辑
    return {
        "distribution_data": {},
        "statistics": {},
        "filters_applied": {
            "league": league,
            "company_id": company_id,
            "handicap_type": handicap_type,
            "date_range": f"{date_from} to {date_to}" if date_from and date_to else None
        }
    }

@router.get(
    "/analysis/volatility",
    summary="SP值变动分析",
    description="获取SP值临场变动分析"
)
async def get_sp_volatility_analysis(
    time_before_match: int = Query(30, description="赛前多少分钟分析"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """SP值临场变动分析"""
    # TODO: 实现变动分析逻辑
    return {
        "volatility_data": {},
        "analysis_period": f"赛前{time_before_match}分钟",
        "insights": []
    }

@router.get(
    "/analysis/company-comparison",
    summary="赔率公司对比分析",
    description="不同赔率公司的SP值对比分析"
)
async def get_company_comparison_analysis(
    match_ids: List[int] = Query(..., description="比赛ID列表"),
    service: SPManagementService = Depends(get_sp_management_service),
    current_user: User = Depends(get_current_active_user)
):
    """赔率公司对比分析"""
    # TODO: 实现公司对比分析逻辑
    return {
        "comparison_data": {},
        "matches_analyzed": match_ids,
        "companies_involved": []
    }