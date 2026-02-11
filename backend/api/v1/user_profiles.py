from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.services.user_profile_service import UserProfileService
from backend.models.admin_user import AdminUser
from backend.core.auth import get_current_admin_user
from pydantic import BaseModel

router = APIRouter(prefix="/user-profiles", tags=["user-profiles"])

# Pydantic模型定义
class UserProfile(BaseModel):
    userId: int
    username: str
    email: str
    riskTolerance: str
    preferredTeams: List[str]
    successRate: float
    bettingFrequency: str
    bettingHabits: str
    totalBettingAmount: float
    totalProfit: float
    profitProbability: float
    tags: List[str]
    lastUpdated: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[UserProfile])
async def get_user_profiles(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100
):
    """
    获取用户画像列表
    """
    try:
        # 获取所有用户
        users = db.query(AdminUser).offset(skip).limit(limit).all()
        
        profiles = []
        profile_service = UserProfileService(db)
        
        for user in users:
            # 获取用户画像
            raw_profile = profile_service.build_profile(user.id)
            
            # 将原始画像数据转换为前端需要的格式
            profile = UserProfile(
                userId=user.id,
                username=user.username,
                email=user.email,
                riskTolerance=_map_risk_tolerance(raw_profile["risk_tolerance"]),
                preferredTeams=raw_profile["preferred_teams"] or [],
                successRate=raw_profile["success_rate"],
                bettingFrequency=_map_betting_frequency(raw_profile["betting_patterns"]["betting_frequency"]),
                bettingHabits=raw_profile["betting_patterns"].get("most_common_bet_type", "未知"),
                totalBettingAmount=raw_profile["betting_patterns"].get("avg_bet_amount", 0) * 10,  # 模拟总投注额
                totalProfit=_calculate_profit(db, user.id),  # 计算总利润
                profitProbability=raw_profile["success_rate"],  # 使用成功率作为盈利概率
                tags=_generate_tags(raw_profile),  # 生成标签
                lastUpdated=raw_profile["last_updated"]
            )
            profiles.append(profile)
        
        return profiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取特定用户的画像
    """
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile_service = UserProfileService(db)
    raw_profile = profile_service.build_profile(user_id)
    
    profile = UserProfile(
        userId=user.id,
        username=user.username,
        email=user.email,
        riskTolerance=_map_risk_tolerance(raw_profile["risk_tolerance"]),
        preferredTeams=raw_profile["preferred_teams"] or [],
        successRate=raw_profile["success_rate"],
        bettingFrequency=_map_betting_frequency(raw_profile["betting_patterns"]["betting_frequency"]),
        bettingHabits=raw_profile["betting_patterns"].get("most_common_bet_type", "未知"),
        totalBettingAmount=raw_profile["betting_patterns"].get("avg_bet_amount", 0) * 10,  # 模拟总投注额
        totalProfit=_calculate_profit(db, user.id),  # 计算总利润
        profitProbability=raw_profile["success_rate"],  # 使用成功率作为盈利概率
        tags=_generate_tags(raw_profile),  # 生成标签
        lastUpdated=raw_profile["last_updated"]
    )
    
    return profile


@router.put("/{user_id}", response_model=UserProfile)
async def update_user_profile(
    user_id: int,
    profile_update: dict,  # 这里应该定义一个专门的更新模型
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    更新用户画像信息
    """
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 这里可以实现更新用户画像的逻辑
    # 目前只是返回现有画像，需要根据实际需求实现更新逻辑
    
    profile_service = UserProfileService(db)
    raw_profile = profile_service.build_profile(user_id)
    
    profile = UserProfile(
        userId=user.id,
        username=user.username,
        email=user.email,
        riskTolerance=profile_update.get("riskTolerance", _map_risk_tolerance(raw_profile["risk_tolerance"])),
        preferredTeams=profile_update.get("preferredTeams", raw_profile["preferred_teams"] or []),
        successRate=profile_update.get("successRate", raw_profile["success_rate"]),
        bettingFrequency=profile_update.get("bettingFrequency", _map_betting_frequency(raw_profile["betting_patterns"]["betting_frequency"])),
        bettingHabits=profile_update.get("bettingHabits", raw_profile["betting_patterns"].get("most_common_bet_type", "未知")),
        totalBettingAmount=profile_update.get("totalBettingAmount", raw_profile["betting_patterns"].get("avg_bet_amount", 0) * 10),
        totalProfit=profile_update.get("totalProfit", _calculate_profit(db, user.id)),
        profitProbability=profile_update.get("profitProbability", raw_profile["success_rate"]),
        tags=profile_update.get("tags", _generate_tags(raw_profile)),
        lastUpdated=profile_update.get("lastUpdated", raw_profile["last_updated"])
    )
    
    return profile


def _map_risk_tolerance(risk_score: float) -> str:
    """将风险评分映射到风险类型"""
    if risk_score < 0.33:
        return "conservative"
    elif risk_score < 0.66:
        return "moderate"
    else:
        return "aggressive"


def _map_betting_frequency(freq_str: str) -> str:
    """将投注频率字符串映射到前端使用的值"""
    mapping = {
        "high": "high",
        "medium": "medium", 
        "low": "low",
        "none": "low"
    }
    return mapping.get(freq_str, "medium")


def _calculate_profit(db: Session, user_id: int) -> float:
    """计算用户总利润（模拟实现）"""
    # 这里需要根据实际的投注记录表计算盈亏
    # 目前返回模拟值
    import random
    return round(random.uniform(-5000, 10000), 2)


def _generate_tags(profile: dict) -> List[str]:
    """根据画像生成标签"""
    tags = []
    
    risk = profile.get("risk_tolerance", 0.5)
    if risk < 0.33:
        tags.append("保守型")
    elif risk < 0.66:
        tags.append("稳健型")
    else:
        tags.append("激进型")
    
    teams = profile.get("preferred_teams", [])
    if teams:
        tags.append(f"{teams[0]}球迷")  # 添加第一个偏好球队作为标签
    
    patterns = profile.get("betting_patterns", {})
    freq = patterns.get("betting_frequency", "medium")
    if freq == "high":
        tags.append("高频投注")
    elif freq == "low":
        tags.append("低频投注")
    
    return tags or ["活跃用户"]