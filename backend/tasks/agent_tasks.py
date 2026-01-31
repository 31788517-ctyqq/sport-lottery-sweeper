from celery import shared_task
from ..agents.odds_monitor_agent import OddsMonitorAgent
from ..services.hedge_service import HedgeService
from ..database import SessionLocal
from ..services.user_profile_service import UserProfileService


@shared_task
def run_odds_monitor_agent():
    """运行赔率监控智能体的任务"""
    # 初始化智能体
    hedge_service = HedgeService()
    agent_config = {
        "interval": 30,  # 30秒检查一次
        "threshold": 0.02  # 2%套利阈值
    }
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        from ..main import llm_service  # 导入已初始化的llm_service
        
        # 由于HedgeService可能需要更多参数，这里简化处理
        agent = OddsMonitorAgent("odds_monitor", agent_config, hedge_service)
        
        # 执行任务
        context = {}
        result = agent.execute(context)
        return result
    finally:
        db.close()


@shared_task
def run_recommendation_agent(user_id: int, upcoming_matches: list = None):
    """运行推荐智能体的任务"""
    if upcoming_matches is None:
        upcoming_matches = []
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        from ..main import llm_service  # 导入已初始化的llm_service
        from ..services.prediction_service import PredictionService  # 假设有此服务
        
        # 初始化服务
        user_profile_service = UserProfileService(db)
        # 这里我们假设PredictionService存在，如果不存在需要创建
        prediction_service = PredictionService(llm_service)  # 假设PredictionService接受llm_service作为参数
        
        # 初始化智能体
        agent_config = {}
        from ..agents.recommendation_agent import RecommendationAgent
        agent = RecommendationAgent(
            "recommendation_agent",
            agent_config,
            user_profile_service,
            prediction_service
        )
        
        # 执行任务
        context = {
            "user_id": user_id,
            "upcoming_matches": upcoming_matches
        }
        result = agent.execute(context)
        return result
    except ImportError:
        # 如果PredictionService不存在，返回错误信息
        return {"error": "PredictionService not implemented yet"}
    finally:
        db.close()