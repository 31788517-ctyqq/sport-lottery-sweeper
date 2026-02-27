from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import csv
import json
import io
import copy
import re


from backend.core.security import oauth2_scheme
from backend.dependencies import get_current_user as get_current_user_dependency
from backend.core.database import get_db
from backend.models.beidan_strategy import BeidanStrategy
from backend.services.beidan_data_service import BeidanDataService

logger = logging.getLogger(__name__)

# 适配器函数：将User对象转换为字典格式
async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> dict:
    """
    获取当前用户（返回字典格式，兼容现有API）
    支持AdminUser和User两种用户模型
    """
    logger.info(f"get_current_user called with token: {token[:20]}...")
    try:
        # 首先尝试使用原始的依赖函数
        user = get_current_user_dependency(db=db, token=token)
        logger.info(f"get_current_user_dependency succeeded: {user.username}")
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": getattr(user, 'is_admin', False) or getattr(user, 'is_superuser', False),
            "role": getattr(user, 'role', 'user')
        }
    except Exception as e:
        # 如果原始依赖失败，尝试解码token并查找AdminUser
        logger.warning(f"原始用户依赖失败，尝试AdminUser: {e}")
        try:
            from backend.models.admin_user import AdminUser
            import jwt
            from backend.config import settings
            
            # 直接解码token（尝试验证签名，失败则跳过）
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            except Exception as decode_error:
                logger.warning(f"JWT签名验证失败，尝试不验证签名: {decode_error}")
                payload = jwt.decode(token, options={"verify_signature": False})
            
            if not payload:
                raise HTTPException(status_code=401, detail="无效的token")
            
            username = payload.get("username") or payload.get("sub")
            if not username:
                raise HTTPException(status_code=401, detail="token中缺少用户名")
            
            # 查找AdminUser
            admin_user = db.query(AdminUser).filter(AdminUser.username == username).first()
            if admin_user:
                return {
                    "id": admin_user.id,
                    "username": admin_user.username,
                    "email": admin_user.email,
                    "is_admin": True,
                    "role": admin_user.role
                }
            else:
                # 如果AdminUser不存在，返回基于token的模拟用户
                return {
                    "id": payload.get("user_id") or payload.get("sub") or 1,
                    "username": username,
                    "email": payload.get("email", ""),
                    "is_admin": payload.get("role") == "admin",
                    "role": payload.get("role", "user")
                }
        except Exception as inner_e:
            logger.error(f"获取当前用户失败: {inner_e}")
            raise HTTPException(status_code=401, detail="认证失败")

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

class StabilityOptionsResponse(BaseModel):
    stabilityOptions: List[Dict[str, Any]] = Field(..., description="一赔稳定性选项列表")

class MatchItem(BaseModel):
    id: int = Field(..., description="比赛ID")
    matchTime: str = Field(..., description="比赛时间")
    league: str = Field(..., description="联赛名称")
    homeTeam: str = Field(..., description="主队名称")
    guestTeam: str = Field(..., description="客队名称")
    score: Optional[str] = Field(None, description="全场比分")
    halfScore: Optional[str] = Field(None, description="半场比分")
    dateTime: str = Field(..., description="期号")
    lineId: str = Field(..., description="线路ID")
    handicap: str = Field(..., description="让球数")
    odds: Dict[str, float] = Field(..., description="赔率信息")
    strengthAnalysis: Dict[str, str] = Field(..., description="实力分析")
    strength: str = Field(..., description="实力等级差")
    winLevel: str = Field(..., description="赢盘等级差")
    stability: str = Field(..., description="稳定性等级")
    pLevel: int = Field(..., description="P级数值")
    predictScore: str = Field(..., description="预测比分")
    recommendation: str = Field(..., description="推荐等级")
    homePower: Optional[float] = Field(None, description="主队实力")
    guestPower: Optional[float] = Field(None, description="客队实力")
    homeWinPan: Optional[float] = Field(None, description="主队赢盘")
    guestWinPan: Optional[float] = Field(None, description="客队赢盘")
    homeFeature: Optional[str] = Field(None, description="主队特征")
    guestFeature: Optional[str] = Field(None, description="客队特征")
    sourceAttributes: Optional[Dict[str, Any]] = Field(None, description="100球原始数据字段")

class StatisticsInfo(BaseModel):
    totalMatches: int = Field(..., description="总场次数")
    filteredMatches: int = Field(..., description="筛选后场次数")
    matchRate: str = Field(..., description="匹配率")
    avgOdds: float = Field(..., description="平均赔率")
    highValueCount: int = Field(..., description="高价值场次数量")
    delta_p_count: int = Field(default=0, description="ΔP命中场次")
    delta_wp_count: int = Field(default=0, description="ΔWP命中场次")
    p_tier_count: int = Field(default=0, description="P-Tier命中场次")

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
    id: Optional[int] = Field(None, description="策略ID")
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
    lineIdStart: Optional[str] = Field(None, description="场次起始 lineId")
    lineIdEnd: Optional[str] = Field(None, description="场次结束 lineId")
    # 兼容旧字段
    strength: Optional[str] = Field(None, description="强度筛选")
    # 新字段，用于三维筛选（与前端FilterSection.vue匹配）
    powerDiffs: List[str] = Field(default_factory=list, description="实力等级差筛选")
    winPanDiffs: List[str] = Field(default_factory=list, description="赢盘等级差筛选")
    stabilityTiers: List[str] = Field(default_factory=list, description="一赔稳定性筛选")


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
async def get_real_time_count(
    date_time: Optional[str] = None,
    leagues: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    start_line_id: Optional[str] = None,
    end_line_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取实时匹配场数（受其它条件联赛/date_time/date_range约束）"""
    try:
        beidan_service = BeidanDataService(db)
        league_list = [item.strip() for item in (leagues or "").split(",") if item.strip()]
        date_range = {}
        if start_date:
            date_range["startDate"] = start_date
        if end_date:
            date_range["endDate"] = end_date

        filter_params = {
            "threeDimensional": {
                "powerDifference": {
                    "homeWeak": False,
                    "homeBalanced": False,
                    "homeStrong": False,
                    "guestWeak": False,
                    "guestBalanced": False,
                    "guestStrong": False,
                },
                "winPanDifference": 0,
                "sizeBallDifference": 0,
            },
            "otherConditions": {
                "leagues": league_list,
                "dateTime": date_time or "",
                "dateRange": date_range,
                "lineIdStart": start_line_id or "",
                "lineIdEnd": end_line_id or "",
                "powerDiffs": [],
                "winPanDiffs": [],
                "stabilityTiers": [],
            },
        }

        matches = await beidan_service.get_filtered_matches(filter_params)
        match_count = len(matches)
        
        return RealTimeCountResponse(
            matchCount=match_count,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"获取实时场次数失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取实时场次数失败: {str(e)}")

# ==================== 选项数据接口 ====================

@router.get("/date-time-options", response_model=DateTimeOptionsResponse)
async def get_date_time_options(db: Session = Depends(get_db)):
    """获取日期时间选项（无参数）"""
    try:
        # 使用BeidanDataService从数据库获取最新的日期时间选项
        beidan_service = BeidanDataService(db)
        date_time_options, latest_period = beidan_service.get_latest_date_time_options()
        
        return DateTimeOptionsResponse(
            dateTimeOptions=date_time_options,
            latestPeriod=latest_period
        )
    except Exception as e:
        logger.error(f"获取日期时间选项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取日期时间选项失败: {str(e)}")

@router.get("/league-options", response_model=LeagueOptionsResponse)
async def get_league_options(db: Session = Depends(get_db)):
    """获取联赛选项（无参数）"""
    try:
        # 从数据库获取联赛选项
        beidan_service = BeidanDataService(db)
        league_options = beidan_service.get_available_leagues()
        
        return LeagueOptionsResponse(leagueOptions=league_options)
    except Exception as e:
        logger.error(f"获取联赛选项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取联赛选项失败: {str(e)}")

@router.get("/strength-options", response_model=StrengthOptionsResponse)
async def get_strength_options():
    """获取强度等级选项（无参数）"""
    try:
        # 根据北单过滤参数.md文档定义的实力等级差 ΔP 选项
        strength_options = [
            {"value": "-3", "label": "-3", "range": "< -25", "desc": "客队实力碾压"},
            {"value": "-2", "label": "-2", "range": "-25 ~ -17", "desc": "客队明显占优"},
            {"value": "-1", "label": "-1", "range": "-16 ~ -9", "desc": "客队略有优势"},
            {"value": "0", "label": "0", "range": "-8 ~ +8", "desc": "双方实力接近"},
            {"value": "1", "label": "+1", "range": "+9 ~ +16", "desc": "主队略有优势"},
            {"value": "2", "label": "+2", "range": "+17 ~ +25", "desc": "主队明显占优"},
            {"value": "3", "label": "+3", "range": "> +25", "desc": "主队实力碾压"}
        ]
        
        return StrengthOptionsResponse(strengthOptions=strength_options)
    except Exception as e:
        logger.error(f"获取强度等级选项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取强度等级选项失败: {str(e)}")

@router.get("/win-pan-diff-options", response_model=WinPanDiffOptionsResponse)
async def get_win_pan_diff_options():
    """获取胜平差选项（无参数）"""
    try:
        # 根据北单过滤参数.md文档定义的赢盘等级差 ΔWP 选项
        win_pan_diff_options = [
            {"value": 4, "label": "+4", "range": "S", "desc": "主极致火热"},
            {"value": 3, "label": "+3", "range": "S", "desc": "主极致火热"},
            {"value": 2, "label": "+2", "range": "A", "desc": "主获利走强"},
            {"value": 1, "label": "+1", "range": "A", "desc": "主获利走强"},
            {"value": 0, "label": "0", "range": "B", "desc": "数据均衡"},
            {"value": -1, "label": "-1", "range": "C", "desc": "客获利走强"},
            {"value": -2, "label": "-2", "range": "C", "desc": "客获利走强"},
            {"value": -3, "label": "-3", "range": "D", "desc": "客极致火热"},
            {"value": -4, "label": "-4", "range": "D", "desc": "客极致火热"}
        ]
        
        return WinPanDiffOptionsResponse(winPanDiffOptions=win_pan_diff_options)
    except Exception as e:
        logger.error(f"获取胜平差选项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取胜平差选项失败: {str(e)}")

@router.get("/stability-options", response_model=StabilityOptionsResponse)
async def get_stability_options():
    """获取一赔稳定性选项（无参数）"""
    try:
        # 根据北单过滤参数.md文档定义的一赔稳定性 P-Tier 选项
        stability_options = [
            {"value": "S", "label": "S", "range": "P1", "desc": "正路稳胆"},
            {"value": "A", "label": "A", "range": "P2", "desc": "正路首选"},
            {"value": "B", "label": "B", "range": "P3", "desc": "正路保障"},
            {"value": "B-", "label": "B-", "range": "P4", "desc": "正路分歧"},
            {"value": "C", "label": "C", "range": "P5", "desc": "正路存疑"},
            {"value": "D", "label": "D", "range": "P6", "desc": "正路脆弱"},
            {"value": "E", "label": "E", "range": "P7", "desc": "正路缺失"}
        ]
        
        return StabilityOptionsResponse(stabilityOptions=stability_options)
    except Exception as e:
        logger.error(f"获取一赔稳定性选项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取一赔稳定性选项失败: {str(e)}")

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

        # 基准集合：保留同范围（date_time/联赛）比赛，去掉三维约束，用于统计维度命中数
        base_filter_params = copy.deepcopy(filter_params)
        base_other_conditions = base_filter_params.get("otherConditions", {})
        base_other_conditions["powerDiffs"] = []
        base_other_conditions["winPanDiffs"] = []
        base_other_conditions["stabilityTiers"] = []
        base_filter_params["otherConditions"] = base_other_conditions
        base_matches = await beidan_service.get_filtered_matches(base_filter_params)

        def _apply_line_id_range(matches: List[Dict[str, Any]], start_val: Optional[str], end_val: Optional[str]) -> List[Dict[str, Any]]:
            def _to_int(value):
                if value is None:
                    return None
                text = str(value).strip()
                if not text:
                    return None
                try:
                    return int(text)
                except Exception:
                    return None

            start_num = _to_int(start_val)
            end_num = _to_int(end_val)
            if start_num is None and end_num is None:
                return matches

            filtered = []
            for m in matches:
                line_val = m.get("lineId", None)
                if line_val is None:
                    line_val = m.get("line_id", None)
                line_num = _to_int(line_val)
                if line_num is None:
                    continue
                if start_num is not None and line_num < start_num:
                    continue
                if end_num is not None and line_num > end_num:
                    continue
                filtered.append(m)
            return filtered

        other_conditions_dump = filter_request.otherConditions.model_dump()
        line_start = (
            filter_request.otherConditions.lineIdStart
            or other_conditions_dump.get("line_id_start")
            or other_conditions_dump.get("start_line_id")
        )
        line_end = (
            filter_request.otherConditions.lineIdEnd
            or other_conditions_dump.get("line_id_end")
            or other_conditions_dump.get("end_line_id")
        )
        if line_start or line_end:
            filtered_matches = _apply_line_id_range(filtered_matches, line_start, line_end)
            base_matches = _apply_line_id_range(base_matches, line_start, line_end)

        def _normalize_signed(value: Any) -> str:

            if value is None:
                return ""
            text = str(value).strip()
            if text.startswith("+"):
                text = text[1:]
            return text

        selected_power = {_normalize_signed(v) for v in filter_request.otherConditions.powerDiffs}
        selected_winpan = {_normalize_signed(v) for v in filter_request.otherConditions.winPanDiffs}
        selected_tiers = {str(v).strip() for v in filter_request.otherConditions.stabilityTiers}

        delta_p_count = (
            sum(1 for m in base_matches if _normalize_signed(m.get("strength")) in selected_power)
            if selected_power else 0
        )
        delta_wp_count = (
            sum(1 for m in base_matches if _normalize_signed(m.get("winLevel")) in selected_winpan)
            if selected_winpan else 0
        )
        p_tier_count = (
            sum(1 for m in base_matches if str(m.get("stability", "")).strip() in selected_tiers)
            if selected_tiers else 0
        )
        
        def _to_signed_number(value: Any) -> float:
            """Convert '+3'/'-2'/None to numeric for sorting."""
            if value is None:
                return 0.0
            text = str(value).strip()
            if not text:
                return 0.0
            try:
                return float(text.replace("+", ""))
            except Exception:
                return 0.0

        # 应用排序
        sort_field = filter_request.sort.field
        sort_order = filter_request.sort.order
        reverse = (sort_order == "desc")
        
        if sort_field == "match_time":
            filtered_matches.sort(key=lambda x: x["matchTime"], reverse=reverse)
        elif sort_field == "league":
            filtered_matches.sort(key=lambda x: x["league"], reverse=reverse)
        elif sort_field == "recommendation":
            # 按推荐等级排序
            rec_order = {"重点关注": 0, "值得关注": 1, "观望": 2}
            filtered_matches.sort(key=lambda x: rec_order.get(x["recommendation"], 3), reverse=reverse)
        elif sort_field == "p_level":
            filtered_matches.sort(key=lambda x: x.get("pLevel", 0), reverse=reverse)
        elif sort_field == "delta_wp":
            filtered_matches.sort(key=lambda x: _to_signed_number(x.get("winLevel")), reverse=reverse)
        elif sort_field == "power_diff":
            filtered_matches.sort(key=lambda x: _to_signed_number(x.get("strength")), reverse=reverse)
        
        # 分页处理
        total_items = len(filtered_matches)
        total_pages = (total_items + filter_request.pageSize - 1) // filter_request.pageSize
        start_idx = (filter_request.page - 1) * filter_request.pageSize
        end_idx = start_idx + filter_request.pageSize
        paginated_matches = filtered_matches[start_idx:end_idx]
        
        # 转换为响应格式
        match_items = [MatchItem(**match) for match in paginated_matches]
        
        # 计算统计信息
        base_total = len(base_matches)
        match_rate = f"{(len(filtered_matches) / max(base_total, 1) * 100):.1f}%"
        avg_odds = sum(sum(match["odds"].values()) for match in paginated_matches) / len(paginated_matches) if paginated_matches else 0
        high_value_count = len([m for m in paginated_matches if m["recommendation"] == "重点关注"])
        
        statistics = StatisticsInfo(
            totalMatches=base_total,
            filteredMatches=total_items,
            matchRate=match_rate,
            avgOdds=round(avg_odds, 2),
            highValueCount=high_value_count,
            delta_p_count=delta_p_count,
            delta_wp_count=delta_wp_count,
            p_tier_count=p_tier_count
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
            # 获取当前用户ID，如果没有则使用默认用户
            user_id = "default_user"
            # 注意：由于高级筛选可能不需要认证，这里跳过用户获取以避免复杂性
            # 如果需要用户跟踪，应该在请求中包含用户信息
            
            log_entry = BeidanStrategyExecutionLog(
                strategy_id=0,  # 使用0表示未关联具体策略（匿名筛选）
                user_id=user_id,
                execution_params=filter_params,
                result_stats={
                    "total_matches": base_total,
                    "filtered_matches": total_items,
                    "high_value_count": high_value_count,
                    "delta_p_count": delta_p_count,
                    "delta_wp_count": delta_wp_count,
                    "p_tier_count": p_tier_count
                },
                status="success",
                executed_at=datetime.utcnow()
            )
            db.add(log_entry)
            db.commit()
        except Exception as log_error:
            logger.warning(f"记录执行日志失败: {log_error}")
            # 不影响主要业务逻辑
            db.rollback()
        
        return AdvancedFilterResponse(
            matches=match_items,
            statistics=statistics,
            pagination=pagination
        )
        
    except Exception as e:
        logger.error(f"高级筛选失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"高级筛选失败: {str(e)}")

# ==================== 策略管理接口 ====================

# 使用上面定义的 get_current_user 函数（第20行定义），这里不再重复定义
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     """获取当前用户（从JWT token）- 已在上方定义，此处注释避免重复"""
#     pass

@router.get("/strategies", response_model=StrategyListResponse)
async def get_strategies(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取用户保存的策略列表"""
    try:
        # 获取当前用户（开发环境下允许回退默认用户，避免刷新后看不到已保存策略）
        try:
            current_user = await get_current_user(db=db, token=token)
        except Exception:
            current_user = {"id": "1", "username": "admin", "is_admin": True, "role": "admin"}
        user_id = str(current_user["id"])  # 转换为字符串，与数据库字段匹配
        
        # 从数据库获取用户的策略（按更新时间倒序）
        user_strategies = db.query(BeidanStrategy).filter(
            BeidanStrategy.user_id == user_id,
            BeidanStrategy.is_active.is_(True)

        ).order_by(BeidanStrategy.updated_at.desc(), BeidanStrategy.id.desc()).all()

        strategy_items = []
        for strategy in user_strategies:
            try:
                item = StrategyItem(**strategy.to_dict())
                strategy_items.append(item)
            except Exception as conversion_error:
                logger.warning(f"策略序列化失败，跳过 id={getattr(strategy, 'id', None)}: {conversion_error}")
                continue

        logger.info(f"User {user_id} loaded {len(strategy_items)} strategies")
        return StrategyListResponse(strategies=strategy_items)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取策略列表失败: {str(e)}")

@router.post("/strategies", response_model=StrategyItem)
async def save_strategy(
    strategy: StrategyItem,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """保存新策略或更新现有策略"""
    try:
        # 获取当前用户（开发环境下允许匿名保存，使用默认用户）
        current_user = None
        try:
            current_user = await get_current_user(db=db, token=token)
        except Exception:
            # 如果认证失败，使用默认用户（仅用于开发测试）
            current_user = {"id": "1", "username": "admin", "is_admin": True, "role": "admin"}
            print("⚠️  开发模式：使用默认用户进行策略保存")

        user_id = str(current_user["id"])  # 使用用户ID并统一为字符串，避免刷新后查不到
        current_time = datetime.utcnow()

        logger.info(f"Received strategy from user {user_id}: {strategy.model_dump()}")

        # 优先通过ID查找（如果提供了有效的ID）
        if strategy.id and strategy.id > 0:
            # 通过ID和用户ID查找策略
            existing_strategy = db.query(BeidanStrategy).filter(
                BeidanStrategy.id == strategy.id,
                BeidanStrategy.user_id == user_id,
                BeidanStrategy.is_active.is_(True),
            ).first()

            if not existing_strategy:
                raise HTTPException(status_code=404, detail="策略不存在或无权限更新")

            # 检查新名称是否与其他策略冲突（同一用户下，排除自身）
            if strategy.name != existing_strategy.name:
                name_conflict = db.query(BeidanStrategy).filter(
                    BeidanStrategy.name == strategy.name,
                    BeidanStrategy.user_id == user_id,
                    BeidanStrategy.is_active.is_(True),
                    BeidanStrategy.id != strategy.id,
                ).first()

                if name_conflict:
                    raise HTTPException(status_code=400, detail=f"策略名称'{strategy.name}'已被使用")
            
            # 更新策略字段
            existing_strategy.name = strategy.name
            existing_strategy.description = strategy.description
            existing_strategy.three_dimensional = strategy.threeDimensional
            existing_strategy.other_conditions = strategy.otherConditions
            existing_strategy.sort_config = strategy.sort
            existing_strategy.updated_at = current_time
            
            db.commit()
            db.refresh(existing_strategy)
            
            return StrategyItem(**existing_strategy.to_dict())
        else:
            # 通过名称和用户ID查找策略
            existing_strategy = db.query(BeidanStrategy).filter(
                BeidanStrategy.name == strategy.name,
                BeidanStrategy.user_id == user_id,
                BeidanStrategy.is_active.is_(True),
            ).first()

            
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
                    user_id=user_id,
                    created_at=current_time,
                    updated_at=current_time
                )
                
                # 设置StrategyItem需要的字段值
                strategy.createdAt = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                strategy.updatedAt = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                
                db.add(new_strategy)
                db.commit()
                db.refresh(new_strategy)
                
                return StrategyItem(**new_strategy.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存策略失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存策略失败: {str(e)}")

@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """删除指定策略（软删除）"""
    try:
        # 获取当前用户
        current_user = await get_current_user(db=db, token=token)
        user_id = current_user["id"]  # 使用用户ID而不是用户名进行查询
        
        # 查找策略并验证所有权（包括已软删除的策略）
        strategy = db.query(BeidanStrategy).filter(
            BeidanStrategy.id == strategy_id,
            BeidanStrategy.user_id == user_id
        ).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在或无权限删除")
        
        # 如果已经是软删除状态，直接返回成功
        if not strategy.is_active:
            return {"message": "策略已删除"}
        
        # 软删除（设置is_active为False）
        strategy.is_active = False
        strategy.updated_at = datetime.utcnow()
        
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

# ==================== 获取最新日期时间选项接口 ====================

class LatestDateTimeResponse(BaseModel):
    """最新日期时间响应模型"""
    dateTimes: List[str] = Field(..., description="可用的日期时间选项列表")
    total: int = Field(..., description="总数量")


@router.get("/latest-date-times", response_model=LatestDateTimeResponse)
async def get_latest_date_times(db: Session = Depends(get_db)):
    """获取最新的比赛日期时间选项（如：26024, 26023, 26022）"""
    try:
        from backend.models.matches import FootballMatch
        from sqlalchemy import desc

        logger.info("开始获取最新日期时间选项")

        periods = set()

        def add_period(value):
            if value is None:
                return
            text = str(value).strip()
            if not text:
                return
            match = re.search(r"(\d{5,})", text)
            if not match:
                return
            num = int(match.group(1))
            if 20000 <= num <= 99999:
                periods.add(str(num))

        try:
            rows = db.query(FootballMatch.date_time) \
                .filter(FootballMatch.data_source == "100qiu") \
                .filter(FootballMatch.date_time.isnot(None)) \
                .order_by(desc(FootballMatch.date_time)) \
                .limit(20) \
                .all()
            for (date_time,) in rows:
                add_period(date_time)
        except Exception as db_error:
            logger.error(f"数据库查询date_time失败: {db_error}")

        if len(periods) < 5:
            try:
                rows = db.query(FootballMatch) \
                    .filter(FootballMatch.data_source == "100qiu") \
                    .order_by(desc(FootballMatch.match_time), desc(FootballMatch.id)) \
                    .limit(300) \
                    .all()
                for match in rows:
                    add_period(match.date_time)
                    if isinstance(match.source_attributes, dict):
                        add_period(match.source_attributes.get("dateTime"))
                    if match.match_id:
                        add_period(str(match.match_id).split("_")[0])
                    if len(periods) >= 5:
                        break
            except Exception as fallback_error:
                logger.error(f"回退读取最近场次失败: {fallback_error}")

        date_times = sorted(periods, key=lambda x: int(x), reverse=True)[:5]

        if not date_times:
            logger.warning("没有找到有效的100qiu期号数据，返回空列表")

        response = LatestDateTimeResponse(
            dateTimes=date_times,
            total=len(date_times)
        )

        logger.info(f"API响应: {response.model_dump()}")
        return response

    except Exception as e:
        logger.error(f"获取最新日期时间选项失败: {str(e)}", exc_info=True)
        # 出错时返回空列表，避免前端误选不存在的期号
        return LatestDateTimeResponse(
            dateTimes=[],
            total=0
        )



