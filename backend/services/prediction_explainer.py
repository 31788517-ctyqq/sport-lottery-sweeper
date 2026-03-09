from typing import Dict, Any
from sqlalchemy.orm import Session
from ..services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)

class PredictionExplainer:
    """预测结果解释器 - 使用LLM提供人类可理解的解释"""
    
    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.llm_service = llm_service
    
    def explain_prediction(self, match_id: int, prediction_result: Dict[str, Any]) -> str:
        """解释预测结果"""
        try:
            # 获取比赛相关信息
            from ..models.match import Match
            match = self.db.query(Match).filter(Match.id == match_id).first()
            
            if not match:
                return "无法获取比赛信息，无法生成解释"
            
            # 构造解释提示
            prompt = f"""
            请解释以下足球比赛的预测结果，使其易于理解：
            
            比赛信息:
            - 主队: {getattr(match, 'home_team', '未知')}
            - 客队: {getattr(match, 'away_team', '未知')}
            - 联赛: {getattr(match, 'league', '未知')}
            - 比赛时间: {match.match_date if hasattr(match, 'match_date') else '未知'}
            
            预测结果:
            - 主胜概率: {prediction_result.get('probabilities', {}).get('home_win', 0):.2%}
            - 平局概率: {prediction_result.get('probabilities', {}).get('draw', 0):.2%}
            - 客胜概率: {prediction_result.get('probabilities', {}).get('away_win', 0):.2%}
            - 预测信心: {prediction_result.get('confidence', 0):.2%}
            
            请提供以下方面的解释：
            1. 预测的主要依据
            2. 关键影响因素
            3. 预测的可信度分析
            4. 潜在不确定性因素
            5. 对投注策略的建议（如有）
            
            请注意保持客观和科学的态度，强调预测结果的不确定性。
            """
            
            explanation = self.llm_service.generate_response(
                prompt,
                provider="openai",  # 使用OpenAI作为默认解释提供商
                temperature=0.5,
                max_tokens=500
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"预测解释生成失败: {e}")
            return "预测结果解释生成失败，请稍后重试"