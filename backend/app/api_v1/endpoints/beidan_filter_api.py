from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import csv
import json
import io

from backend.core.auth_service import oauth2_scheme, verify_token
from backend.database import get_db
from backend.models.beidan_strategy import BeidanStrategy
from backend.services.beidan_data_service import BeidanDataService

logger = logging.getLogger(__name__)

# 定义响应模型
class RealTimeCountResponse(BaseModel):
    matchCount: int = Field(..., description="实时匹配场次数")
    timestamp: str = Field(..., description="时间戳")

class DateTimeOptionsResponse(BaseModel):
    dateTimeOptions: List[Dict[str, str]] = Field(..., description="日期时间选项列表")
    latestPeriod: str = Field(..., description="最新一期期号")

class LeagueOptionsResponse(BaseModel):
    leagueOptions: List[Dict[str, str]] = Field(..., description="联赛选项列表")

class StrengthOptionsResponse(BaseModel):
    strengthOptions: List[Dict[str, str]] = Field(..., description="强度等级选项列表")

class WinPanDiffOptionsResponse(BaseModel):
    winPanDiffOptions: List[Dict[str, Any]] = Field(..., description="胜平差选项列表")

class MatchItem(BaseModel):
    id: int = Field(..., description="比赛ID")
    matchTime: str = Field(..., description="比赛时间")
    league: str = Field(..., description="联赛名称")
    homeTeam: str = Field(..., description="主队名称")
    guestTeam: str = Field(..., description="客队名称")
    handicap: str = Field(..., description="让球数")
    odds: Dict[str, float] = Field(..., description="赔率信息")
    strengthAnalysis: Dict[str, str] = Field(..., description="实力分析")
    predictScore: str = Field(..., description="预测比分")
    recommendation: str = Field(..., description="推荐等级")

class StatisticsInfo(BaseModel):
    totalMatches: int = Field(..., description="总场次数")
    filteredMatches: int = Field(..., description="筛选后场次数")
    matchRate: str = Field(..., description="匹配率")
    avgOdds: float = Field(..., description="平均赔率")
    highValueCount: int = Field(..., description="高价值场次数量")

class PaginationInfo(BaseModel):
    currentPage: int = Field(..., description="当前页码")
    pageSize: int = Field(..., description="每页数量")
    totalPages: int = Field(..., description="总页数")
    totalItems: int = Field(..., description="总条目数")

class AdvancedFilterResponse(BaseModel):
    matches: List[MatchItem] = Field(..., description="比赛列表")
    statistics: StatisticsInfo = Field(..., description="统计信息")
    pagination: PaginationInfo = Field(..., description="分页信息")

class StrategyItem(BaseModel):
    id: int = Field(..., description="策略ID")
    name: str = Field(..., description="策略名称")
    description: str = Field(..., description="策略描述")
    threeDimensional: Dict[str, Any] = Field(..., description="三维条件配置")
    otherConditions: Dict[str, Any] = Field(..., description="其他条件配置")
    sort: Dict[str, str] = Field(..., description="排序配置")
    createdAt: str = Field(..., description="创建时间")
    updatedAt: str = Field(..., description="更新时间")

class StrategyListResponse(BaseModel):
    strategies: List[StrategyItem] = Field(..., description="策略列表")

class ExampleStrategyItem(BaseModel):
    name: str = Field(..., description="示例策略名称")
    description: str = Field(..., description="示例策略描述")
    threeDimensional: Dict[str, Any] = Field(..., description="三维条件配置")
    otherConditions: Dict[str, Any] = Field(..., description="其他条件配置")
    sort: Dict[str, str] = Field(..., description="排序配置")

class ExampleStrategiesResponse(BaseModel):
    exampleStrategies: List[ExampleStrategyItem] = Field(..., description="示例策略列表")

# 定义请求模型
class ThreeDimensionalCondition(BaseModel):
    powerDifference: Dict[str, bool] = Field(..., description="实力差配置")
    winPanDifference: int = Field(..., description="赢盘差配置")
    sizeBallDifference: int = Field(..., description="大小球差配置")

class OtherConditions(BaseModel):
    leagues: List[str] = Field(default_factory=list, description="联赛筛选")
    dateTime: Optional[str] = Field(None, description="特定日期时间")
    dateRange: Dict[str, str] = Field(default_factory=dict, description="日期范围")
    strength: Optional[str] = Field(None, description="强度筛选")

class SortCondition(BaseModel):
    field: str = Field(..., description="排序字段")
    order: str = Field(..., description="排序方向")

class AdvancedFilterRequest(BaseModel):
    threeDimensional: ThreeDimensionalCondition = Field(..., description="三维条件")
    otherConditions: OtherConditions = Field(..., description="其他条件")
    sort: SortCondition = Field(..., description="排序条件")
    page: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=20, ge=1, le=100, description="每页数量")

# 注意：不要在这里定义prefix，因为外部已经添加了
router = APIRouter(tags=["beidan-filter"])

# 模拟数据库存储（实际项目中应使用真实的数据库）
strategies_db = []
strategy_id_counter = 1

# 示例策略数据
EXAMPLE_STRATEGIES = [
    {
        "name": "稳健型策略",
        "description": "适合保守投资者，注重基本面分析",
        "threeDimensional": {
            "powerDifference": {
                "homeWeak": True,
                "homeBalanced": True,
                "homeStrong": False,
                "guestWeak": True,
                "guestBalanced": True,
                "guestStrong": False
            },
            "winPanDifference": 0,
            "sizeBallDifference": 0
        },
        "otherConditions": {
            "leagues": ["premier_league", "la_liga", "bundesliga"],
            "dateTime": "",
            "dateRange": {
                "startDate": "",
                "endDate": ""
            },
            "strength": "balanced"
        },
        "sort": {
            "field": "match_time",
            "order": "asc"
        }
    },
    {
        "name": "进取型策略",
        "description": "适合激进投资者，追求高收益",
        "threeDimensional": {
            "powerDifference": {
                "homeWeak": True,
                "homeBalanced": True,
                "homeStrong": True,
                "guestWeak": True,
                "guestBalanced": True,
                "guestStrong": True
            },
            "winPanDifference": 1,
            "sizeBallDifference": 0
        },
        "otherConditions": {
            "leagues": ["champions_league"],
            "dateTime": "",
            "dateRange": {
                "startDate": "",
                "endDate": ""
            },
            "strength": "strong"
        },
        "sort": {
            "field": "match_time",
            "order": "desc"
        }
    }
]

# 辅助函数
async def get_mock_match_data() -> List[Dict]:
    """获取模拟比赛数据"""
    return [
        {
            "id": 1001,
            "matchTime": "2025-01-15 20:00",
            "league": "英超",
            "homeTeam": "曼城",
            "guestTeam": "阿森纳",
            "handicap": "-1.5",
            "odds": {
                "homeWin": 1.85,
                "draw": 3.40,
                "guestWin": 4.20
            },
            "strengthAnalysis": {
                "homeStrength": "偏强",
                "guestStrength": "均衡",
                "powerDifference": "主队占优"
            },
            "predictScore": "2:1",
            "recommendation": "重点关注"
        },
        {
            "id": 1002,
            "matchTime": "2025-01-15 22:00",
            "league": "西甲",
            "homeTeam": "巴塞罗那",
            "guestTeam": "皇家马德里",
            "handicap": "0",
            "odds": {
                "homeWin": 2.10,
                "draw": 3.20,
                "guestWin": 3.50
            },
            "strengthAnalysis": {
                "homeStrength": "均衡",
                "guestStrength": "均衡",
                "powerDifference": "势均力敌"
            },
            "predictScore": "1:1",
            "recommendation": "观望"
        },
        {
            "id": 1003,
            "matchTime": "2025-01-16 00:00",
            "league": "德甲",
            "homeTeam": "拜仁慕尼黑",
            "guestTeam": "多特蒙德",
            "handicap": "-2.0",
            "odds": {
                "homeWin": 1.65,
                "draw": 3.80,
                "guestWin": 5.00
            },
            "strengthAnalysis": {
                "homeStrength": "偏强",
                "guestStrength": "偏弱",
                "powerDifference": "主队大优"
            },
            "predictScore": "3:0",
            "recommendation": "重点关注"
        }
    ]

# ==================== 实时数据接口 ====================

@router.get("/real-time-count", response_model=RealTimeCountResponse)
async def get_real_time_count():
    """获取当前场次数（无参数）"""
    try:
        # 获取模拟数据
        mock_data = await get_mock_match_data()
        match_count = len(mock_data)
        
        return RealTimeCountResponse(
            matchCount=match_count,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"获取实时场次数失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取实时场次数失败: {str(e)}")

# ==================== 选项数据接口 ====================

@router.get("/date-time-options", response_model=DateTimeOptionsResponse)
async def get_date_time_options():
    """获取日期时间选项（无参数）"""
    try:
        # 模拟从数据库获取日期时间选项
        date_time_options = [
            {"value": "26011", "label": "第26011期 (今日)"},
            {"value": "26010", "label": "第26010期 (昨日)"},
            {"value": "26009", "label": "第26009期 (前日)"},
            {"value": "custom", "label": "自定义日期"}
        ]
        
        return DateTimeOptionsResponse(
            dateTimeOptions=date_time_options,
            latestPeriod="26011"
        )
    except Exception as e:
        logger.error(f"获取日期时间选项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取日期时间选项失败: {str(e)}")

@router.get("/league-options", response_model=LeagueOptionsResponse)
async def get_league_options():
    """获取联赛选项（无参数）"""
    try:
        # 模拟从数据库获取联赛选项
        league_options = [
            {"value": "premier_league", "label": "英超"},
            {"value": "la_liga", "label": "西甲"},
            {"value": "bundesliga", "label": "德甲"},
            {"value": "serie_a", "label": "意甲"},
            {"value": "ligue_1", "label": "法甲"},
            {"value": "champions_league", "label": "欧冠"},
            {"value": "world_cup", "label": "世界杯"}
        ]
        
        return LeagueOptionsResponse(leagueOptions=league_options)
    except Exception as e:
        logger.error(f"获取联赛选项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取联赛选项失败: {str(e)}")

@router.get("/strength-options", response_model=StrengthOptionsResponse)
async def get_strength_options():
    """获取强度等级选项（无参数）"""
    try:
        # 模拟从数据库获取强度等级选项
        strength_options = [
            {"value": "weak", "label": "偏弱"},
            {"value": "balanced", "label": "均衡"},
            {"value": "strong", "label": "偏强"},
            {"value": "very_strong", "label": "很强"}
        ]
        
        return StrengthOptionsResponse(strengthOptions=strength_options)
    except Exception as e:
        logger.error(f"获取强度等级选项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取强度等级选项失败: {str(e)}")

@router.get("/win-pan-diff-options", response_model=WinPanDiffOptionsResponse)
async def get_win_pan_diff_options():
    """获取胜平差选项（无参数）"""
    try:
        # 模拟从数据库获取胜平差选项
        win_pan_diff_options = [
            {"value": -3, "label": "-3"},
            {"value": -2, "label": "-2"},
            {"value": -1, "label": "-1"},
            {"value": 0, "label": "0"},
            {"value": 1, "label": "1"},
            {"value": 2, "label": "2"},
            {"value": 3, "label": "3"}
        ]
        
        return WinPanDiffOptionsResponse(winPanDiffOptions=win_pan_diff_options)
    except Exception as e:
        logger.error(f"获取胜平差选项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取胜平差选项失败: {str(e)}")

# ==================== 高级筛选接口 ====================

@router.post("/advanced-filter", response_model=AdvancedFilterResponse)
async def advanced_filter(
    filter_request: AdvancedFilterRequest,
    db: Session = Depends(get_db)
):
    """高级筛选接口（核心接口）- 使用真实数据源"""
    try:
        # 初始化北单数据服务
        beidan_service = BeidanDataService(db)
        
        # 构建筛选参数字典
        filter_params = {
            "threeDimensional": filter_request.threeDimensional.model_dump(),
            "otherConditions": filter_request.otherConditions.model_dump(),
            "dateTime": filter_request.otherConditions.dateTime or "26011"
        }
        
        # 获取筛选后的比赛数据
        filtered_matches = await beidan_service.get_filtered_matches(filter_params)
        
        # 应用排序
        sort_field = filter_request.sort.field
        sort_order = filter_request.sort.order
        
        if sort_field == "match_time":
            filtered_matches.sort(key=lambda x: x["matchTime"], reverse=(sort_order == "desc"))
        elif sort_field == "league":
            filtered_matches.sort(key=lambda x: x["league"], reverse=(sort_order == "desc"))
        elif sort_field == "recommendation":
            # 按推荐等级排序
            rec_order = {"重点关注": 0, "值得关注": 1, "观望": 2}
            filtered_matches.sort(key=lambda x: rec_order.get(x["recommendation"], 3), reverse=(sort_order == "desc"))
        
        # 分页处理
        total_items = len(filtered_matches)
        total_pages = (total_items + filter_request.pageSize - 1) // filter_request.pageSize
        start_idx = (filter_request.page - 1) * filter_request.pageSize
        end_idx = start_idx + filter_request.pageSize
        paginated_matches = filtered_matches[start_idx:end_idx]
        
        # 转换为响应格式
        match_items = [MatchItem(**match) for match in paginated_matches]
        
        # 计算统计信息
        match_rate = f"{(len(filtered_matches)/max(len(filtered_matches), 1)*100):.1f}%"
        avg_odds = sum(sum(match["odds"].values()) for match in paginated_matches) / len(paginated_matches) if paginated_matches else 0
        high_value_count = len([m for m in paginated_matches if m["recommendation"] == "重点关注"])
        
        statistics = StatisticsInfo(
            totalMatches=total_items,  # 使用筛选后的总数作为总场次
            filteredMatches=total_items,
            matchRate=match_rate,
            avgOdds=round(avg_odds, 2),
            highValueCount=high_value_count
        )
        
        pagination = PaginationInfo(
            currentPage=filter_request.page,
            pageSize=filter_request.pageSize,
            totalPages=total_pages,
            totalItems=total_items
        )
        
        # 记录策略执行日志（可选）
        try:
            from backend.models.beidan_strategy import BeidanStrategyExecutionLog
            log_entry = BeidanStrategyExecutionLog(
                strategy_id=None,  # 这里可以记录使用的策略ID
                user_id="anonymous",  # 可以从token中获取
                execution_params=filter_params,
                result_stats={
                    "total_matches": total_items,
                    "filtered_matches": total_items,
                    "high_value_count": high_value_count
                },
                status="success",
                executed_at=datetime.now(datetime.timezone.utc)
            )
            db.add(log_entry)
            db.commit()
        except Exception as log_error:
            logger.warning(f"记录执行日志失败: {log_error}")
            # 不影响主要业务逻辑
        
        return AdvancedFilterResponse(
            matches=match_items,
            statistics=statistics,
            pagination=pagination
        )
        
    except Exception as e:
        logger.error(f"高级筛选失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"高级筛选失败: {str(e)}")

# ==================== 策略管理接口 ====================

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户（从JWT token）"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username = verify_token(token)
        if username is None:
            raise credentials_exception
        return {"username": username}
    except Exception:
        raise credentials_exception

@router.get("/strategies", response_model=StrategyListResponse)
async def get_strategies(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户保存的策略列表"""
    try:
        # 从数据库获取用户的策略
        user_strategies = db.query(BeidanStrategy).filter(
            BeidanStrategy.user_id == current_user["username"],
            BeidanStrategy.is_active == True
        ).all()
        
        # 转换为响应格式
        strategies = [strategy.to_dict() for strategy in user_strategies]
        
        # 如果没有策略，返回空列表（不再使用全局变量）
        return StrategyListResponse(strategies=strategies)
    except Exception as e:
        logger.error(f"获取策略列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取策略列表失败: {str(e)}")

@router.post("/strategies", response_model=StrategyItem)
async def save_strategy(
    strategy: StrategyItem,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存新策略或更新现有策略"""
    try:
        # 检查是否已存在同名策略
        existing_strategy = db.query(BeidanStrategy).filter(
            BeidanStrategy.name == strategy.name,
            BeidanStrategy.user_id == current_user["username"]
        ).first()
        
        current_time = datetime.now(datetime.timezone.utc)
        
        if existing_strategy:
            # 更新现有策略
            existing_strategy.description = strategy.description
            existing_strategy.three_dimensional = strategy.threeDimensional
            existing_strategy.other_conditions = strategy.otherConditions
            existing_strategy.sort_config = strategy.sort
            existing_strategy.updated_at = current_time
            
            db.commit()
            db.refresh(existing_strategy)
            
            return StrategyItem(**existing_strategy.to_dict())
        else:
            # 创建新策略
            new_strategy = BeidanStrategy(
                name=strategy.name,
                description=strategy.description,
                three_dimensional=strategy.threeDimensional,
                other_conditions=strategy.otherConditions,
                sort_config=strategy.sort,
                user_id=current_user["username"],
                created_at=current_time,
                updated_at=current_time
            )
            
            db.add(new_strategy)
            db.commit()
            db.refresh(new_strategy)
            
            return StrategyItem(**new_strategy.to_dict())
    except Exception as e:
        logger.error(f"保存策略失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存策略失败: {str(e)}")

@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除指定策略"""
    try:
        # 查找策略并验证所有权
        strategy = db.query(BeidanStrategy).filter(
            BeidanStrategy.id == strategy_id,
            BeidanStrategy.user_id == current_user["username"]
        ).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在或无权限删除")
        
        # 软删除（设置is_active为False）
        strategy.is_active = False
        strategy.updated_at = datetime.now(datetime.timezone.utc)
        
        db.commit()
        
        return {"message": "策略删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除策略失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除策略失败: {str(e)}")

@router.get("/strategies/examples", response_model=ExampleStrategiesResponse)
async def get_example_strategies():
    """获取系统预设的示例策略"""
    try:
        return ExampleStrategiesResponse(exampleStrategies=EXAMPLE_STRATEGIES)
    except Exception as e:
        logger.error(f"获取示例策略失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取示例策略失败: {str(e)}")

# ==================== 数据导出接口 ====================

@router.post("/export/csv")
async def export_csv(filter_request: AdvancedFilterRequest):
    """导出CSV格式数据"""
    try:
        # 先执行筛选获取结果
        filter_response = await advanced_filter(filter_request)
        
        # 创建CSV内容
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        headers = ["比赛ID", "比赛时间", "联赛", "主队", "客队", "让球数", "主胜赔率", "平局赔率", "客胜赔率", "实力分析", "预测比分", "推荐等级"]
        writer.writerow(headers)
        
        # 写入数据行
        for match in filter_response.matches:
            row = [
                match.id,
                match.matchTime,
                match.league,
                match.homeTeam,
                match.guestTeam,
                match.handicap,
                match.odds.get("homeWin", ""),
                match.odds.get("draw", ""),
                match.odds.get("guestWin", ""),
                f"{match.strengthAnalysis.get('homeStrength', '')}/{match.strengthAnalysis.get('guestStrength', '')}/{match.strengthAnalysis.get('powerDifference', '')}",
                match.predictScore,
                match.recommendation
            ]
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        return {
            "filename": f"beidan_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "content": csv_content,
            "content_type": "text/csv"
        }
    except Exception as e:
        logger.error(f"CSV导出失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV导出失败: {str(e)}")

@router.post("/export/json")
async def export_json(filter_request: AdvancedFilterRequest):
    """导出JSON格式数据"""
    try:
        # 先执行筛选获取结果
        filter_response = await advanced_filter(filter_request)
        
        # 准备导出数据
        export_data = {
            "exportTime": datetime.now().isoformat(),
            "statistics": filter_response.statistics.model_dump(),
            "matches": [match.model_dump() for match in filter_response.matches],
            "pagination": filter_response.pagination.model_dump()
        }
        
        json_content = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        return {
            "filename": f"beidan_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "content": json_content,
            "content_type": "application/json"
        }
    except Exception as e:
        logger.error(f"JSON导出失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"JSON导出失败: {str(e)}")

@router.post("/export/excel")
async def export_excel(filter_request: AdvancedFilterRequest):
    """导出Excel格式数据（简化版，实际项目中可使用pandas/openpyxl）"""
    try:
        # 先执行筛选获取结果
        filter_response = await advanced_filter(filter_request)
        
        # 由于无法直接生成Excel文件，这里返回CSV格式作为替代
        # 实际项目中可以使用pandas: df.to_excel()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        headers = ["比赛ID", "比赛时间", "联赛", "主队", "客队", "让球数", "主胜赔率", "平局赔率", "客胜赔率", "实力分析", "预测比分", "推荐等级"]
        writer.writerow(headers)
        
        # 写入数据行
        for match in filter_response.matches:
            row = [
                match.id,
                match.matchTime,
                match.league,
                match.homeTeam,
                match.guestTeam,
                match.handicap,
                match.odds.get("homeWin", ""),
                match.odds.get("draw", ""),
                match.odds.get("guestWin", ""),
                f"{match.strengthAnalysis.get('homeStrength', '')}/{match.strengthAnalysis.get('guestStrength', '')}/{match.strengthAnalysis.get('powerDifference', '')}",
                match.predictScore,
                match.recommendation
            ]
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        return {
            "filename": f"beidan_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "content": csv_content,
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "note": "实际项目中应使用pandas/openpyxl生成真正的Excel文件"
        }
    except Exception as e:
        logger.error(f"Excel导出失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Excel导出失败: {str(e)}")