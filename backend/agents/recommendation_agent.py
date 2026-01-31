from typing import Dict, Any
from .base_agent import BaseAgent
from ..services.user_profile_service import UserProfileService
from ..services.prediction_service import PredictionService  # 假设已有预测服务


class RecommendationAgent(BaseAgent):
    def __init__(
        self, 
        name: str, 
        config: Dict[str, Any], 
        user_profile_service: UserProfileService,
        prediction_service: PredictionService
    ):
        super().__init__(name, config)
        self.user_profile_service = user_profile_service
        self.prediction_service = prediction_service
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        user_id = context.get("user_id")
        
        if not user_id:
            return {"error": "Missing user_id in context"}
        
        # 构建用户画像
        profile = self.user_profile_service.build_profile(user_id)
        
        # 获取比赛预测
        upcoming_matches = context.get("upcoming_matches", [])
        recommendations = []
        
        for match in upcoming_matches:
            # 根据用户画像调整推荐权重
            adjusted_prediction = self.adjust_prediction_for_user(profile, match)
            if self.should_recommend(profile, adjusted_prediction):
                recommendations.append({
                    "match_id": match.get("id"),
                    "match_info": f"{match.get('home_team')} vs {match.get('away_team')}",
                    "recommendation": adjusted_prediction,
                    "confidence": adjusted_prediction.get("confidence", 0)
                })
        
        return {
            "user_id": user_id,
            "recommendations": sorted(recommendations, key=lambda x: x["confidence"], reverse=True)[:5]
        }
    
    def adjust_prediction_for_user(self, profile: Dict[str, Any], match: Any) -> Dict[str, Any]:
        # 根据用户画像调整预测结果
        # 这里可以结合用户的偏好和风险承受能力来调整预测
        original_prediction = match.get("prediction", {})
        
        # 如果用户偏好某支球队，增加该队获胜的权重
        preferred_teams = profile.get("preferred_teams", [])
        home_team = match.get("home_team")
        away_team = match.get("away_team")
        
        adjusted_prediction = original_prediction.copy()
        
        if home_team in preferred_teams:
            adjusted_prediction["home_win"] *= 1.1  # 增加10%权重
        elif away_team in preferred_teams:
            adjusted_prediction["away_win"] *= 1.1  # 增加10%权重
        
        # 根据用户风险承受能力调整
        risk_tolerance = profile.get("risk_tolerance", 0.5)
        if risk_tolerance < 0.3:  # 低风险用户
            # 降低高风险投注的推荐权重
            if abs(original_prediction.get("home_win", 0) - original_prediction.get("away_win", 0)) < 0.2:
                # 如果两队实力接近，降低推荐权重
                adjusted_prediction["confidence"] = original_prediction.get("confidence", 0) * 0.7
        
        return adjusted_prediction
    
    def should_recommend(self, profile: Dict[str, Any], prediction: Dict[str, Any]) -> bool:
        # 判断是否应该推荐该投注
        confidence = prediction.get("confidence", 0)
        risk_tolerance = profile.get("risk_tolerance", 0.5)
        
        # 根据用户风险偏好调整推荐阈值
        if risk_tolerance < 0.3:  # 保守型用户
            threshold = 0.7
        elif risk_tolerance > 0.7:  # 激进型用户
            threshold = 0.5
        else:  # 中庸型用户
            threshold = 0.6
        
        return confidence >= threshold