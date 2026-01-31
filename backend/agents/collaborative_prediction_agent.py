from typing import Dict, Any, List
from .base_agent import BaseAgent
from .communication_protocol import CommunicationHub, Message, MessageType
import logging

logger = logging.getLogger(__name__)


class DataCollectionAgent(BaseAgent):
    """数据收集智能体"""
    def __init__(self, name: str, config: Dict[str, Any], comm_hub: CommunicationHub):
        super().__init__(name, config)
        self.comm_hub = comm_hub
        self.comm_hub.register_agent(name, self.receive_message)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        match_id = context.get("match_id")
        
        if not match_id:
            return {"status": "error", "message": "Missing match_id in context"}
        
        # 收集相关数据
        data = await self.collect_data(match_id)
        
        # 发送数据给分析智能体
        message = Message(
            MessageType.REQUEST,
            self.name,
            "analysis_agent",
            {"match_id": match_id, "collected_data": data}
        )
        await self.comm_hub.send_message(message)
        
        return {"status": "data_collected_and_sent", "match_id": match_id}
    
    async def receive_message(self, message: Message):
        """接收消息"""
        if message.type == MessageType.RESPONSE and message.content.get("request_type") == "prediction_result":
            # 接收到预测结果，可以进行后续处理
            logger.info(f"DataCollectionAgent received prediction result: {message.content}")
            # 可以在这里执行后续处理，例如存储结果或通知用户
    
    async def collect_data(self, match_id: int) -> Dict[str, Any]:
        """模拟数据收集逻辑"""
        # 在实际实现中，这里会从数据库或其他数据源收集比赛相关数据
        from sqlalchemy.orm import Session
        from ..database import SessionLocal
        
        db = SessionLocal()
        try:
            # 获取比赛基本信息
            from ..models.match import Match
            match = db.query(Match).filter(Match.id == match_id).first()
            
            # 获取赔率历史
            from ..models.odds import Odds
            odds_history = db.query(Odds).filter(Odds.match_id == match_id).all()
            
            # 获取历史对战数据
            if match:
                from ..models.match import Match as MatchModel
                historical_matches = db.query(MatchModel).filter(
                    ((MatchModel.home_team == match.home_team) & (MatchModel.away_team == match.away_team)) |
                    ((MatchModel.home_team == match.away_team) & (MatchModel.away_team == match.home_team))
                ).limit(5).all()
                
                return {
                    "match_info": {
                        "id": match.id,
                        "home_team": match.home_team,
                        "away_team": match.away_team,
                        "league": match.league,
                        "start_time": str(match.start_time) if match.start_time else None
                    },
                    "odds_history": [
                        {
                            "bookmaker": odds.bookmaker,
                            "home_win": odds.home_win,
                            "draw": odds.draw,
                            "away_win": odds.away_win,
                            "timestamp": str(odds.timestamp) if odds.timestamp else None
                        } for odds in odds_history
                    ],
                    "historical_matches": [
                        {
                            "home_team": m.home_team,
                            "away_team": m.away_team,
                            "score_home": m.score_home,
                            "score_away": m.score_away,
                            "result": "home_win" if m.score_home > m.score_away else 
                                     "away_win" if m.score_home < m.score_away else "draw"
                        } for m in historical_matches
                    ]
                }
            else:
                return {"match_info": {}, "odds_history": [], "historical_matches": []}
        finally:
            db.close()


class AnalysisAgent(BaseAgent):
    """分析智能体"""
    def __init__(self, name: str, config: Dict[str, Any], comm_hub: CommunicationHub):
        super().__init__(name, config)
        self.comm_hub = comm_hub
        self.comm_hub.register_agent(name, self.receive_message)
    
    async def receive_message(self, message: Message):
        """接收来自数据收集智能体的消息"""
        if message.type == MessageType.REQUEST and message.sender == "data_collection_agent":
            logger.info(f"AnalysisAgent received data for match {message.content['match_id']}")
            
            # 执行分析
            analysis_result = await self.perform_analysis(message.content["collected_data"])
            
            # 发送分析结果给预测智能体
            response_msg = Message(
                MessageType.REQUEST,
                self.name,
                "prediction_agent",
                {
                    "match_id": message.content["match_id"],
                    "analysis_result": analysis_result,
                    "previous_data": message.content["collected_data"]
                }
            )
            await self.comm_hub.send_message(response_msg)
            logger.info(f"Analysis result sent to prediction_agent for match {message.content['match_id']}")
    
    async def perform_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据分析"""
        # 分析赔率趋势
        odds_history = data.get("odds_history", [])
        
        if odds_history:
            latest_odds = odds_history[-1]
            avg_home_win = sum(o["home_win"] for o in odds_history) / len(odds_history)
            avg_draw = sum(o["draw"] for o in odds_history) / len(odds_history)
            avg_away_win = sum(o["away_win"] for o in odds_history) / len(odds_history)
            
            # 分析历史对战
            historical_matches = data.get("historical_matches", [])
            home_wins = sum(1 for m in historical_matches if m["result"] == "home_win")
            away_wins = sum(1 for m in historical_matches if m["result"] == "away_win")
            draws = sum(1 for m in historical_matches if m["result"] == "draw")
            
            analysis_result = {
                "odds_trend": {
                    "latest": latest_odds,
                    "average": {
                        "home_win": avg_home_win,
                        "draw": avg_draw,
                        "away_win": avg_away_win
                    }
                },
                "historical_performance": {
                    "home_team_wins": home_wins,
                    "away_team_wins": away_wins,
                    "draws": draws,
                    "total_matches": len(historical_matches)
                },
                "key_factors": [
                    "近期表现",
                    "历史对战记录", 
                    "赔率变化趋势",
                    "主客场优势"
                ]
            }
        else:
            analysis_result = {
                "odds_trend": {},
                "historical_performance": {},
                "key_factors": ["无足够数据进行分析"]
            }
        
        return analysis_result


class PredictionAgent(BaseAgent):
    """预测智能体"""
    def __init__(self, name: str, config: Dict[str, Any], comm_hub: CommunicationHub):
        super().__init__(name, config)
        self.comm_hub = comm_hub
        self.comm_hub.register_agent(name, self.receive_message)
    
    async def receive_message(self, message: Message):
        """接收来自分析智能体的消息"""
        if message.type == MessageType.REQUEST and message.sender == "analysis_agent":
            logger.info(f"PredictionAgent received analysis for match {message.content['match_id']}")
            
            # 执行预测
            prediction_result = await self.make_prediction(
                message.content["analysis_result"],
                message.content["previous_data"]
            )
            
            # 发送最终预测结果给风险控制智能体
            response_msg = Message(
                MessageType.REQUEST,
                self.name,
                "risk_control_agent",
                {
                    "match_id": message.content["match_id"],
                    "prediction_result": prediction_result
                }
            )
            await self.comm_hub.send_message(response_msg)
            logger.info(f"Prediction result sent to risk_control_agent for match {message.content['match_id']}")
    
    async def make_prediction(self, analysis: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """执行预测"""
        # 这里实现预测逻辑
        # 简单示例：基于历史数据和赔率趋势进行预测
        
        # 获取历史对战数据
        historical_perf = analysis.get("historical_performance", {})
        home_wins = historical_perf.get("home_team_wins", 0)
        away_wins = historical_perf.get("away_team_wins", 0)
        total_matches = historical_perf.get("total_matches", 1)
        
        # 获取赔率数据
        odds_trend = analysis.get("odds_trend", {})
        latest_odds = odds_trend.get("latest", {})
        
        # 基于历史数据的预测
        if total_matches > 0:
            home_win_prob = home_wins / total_matches
            away_win_prob = away_wins / total_matches
            draw_prob = 1 - (home_win_prob + away_win_prob)
        else:
            # 如果没有历史数据，基于赔率倒数计算隐含概率
            home_odd = latest_odds.get("home_win", 2.5)
            draw_odd = latest_odds.get("draw", 3.0)
            away_odd = latest_odds.get("away_win", 2.8)
            
            try:
                total_implied_prob = (1/home_odd) + (1/draw_odd) + (1/away_odd)
                home_win_prob = (1/home_odd) / total_implied_prob
                draw_prob = (1/draw_odd) / total_implied_prob
                away_win_prob = (1/away_odd) / total_implied_prob
            except ZeroDivisionError:
                home_win_prob = draw_prob = away_win_prob = 1/3
        
        # 生成预测结果
        prediction_result = {
            "probabilities": {
                "home_win": round(home_win_prob, 3),
                "draw": round(draw_prob, 3),
                "away_win": round(away_win_prob, 3)
            },
            "predicted_outcome": max(
                [("home_win", home_win_prob), ("draw", draw_prob), ("away_win", away_win_prob)], 
                key=lambda x: x[1]
            )[0],
            "confidence": round(max(home_win_prob, draw_prob, away_win_prob), 3),
            "methodology": "Historical performance and odds analysis"
        }
        
        return prediction_result


class RiskControlAgent(BaseAgent):
    """风险控制智能体"""
    def __init__(self, name: str, config: Dict[str, Any], comm_hub: CommunicationHub):
        super().__init__(name, config)
        self.comm_hub = comm_hub
        self.comm_hub.register_agent(name, self.receive_message)
    
    async def receive_message(self, message: Message):
        """接收来自预测智能体的消息"""
        if message.type == MessageType.REQUEST and message.sender == "prediction_agent":
            logger.info(f"RiskControlAgent received prediction for match {message.content['match_id']}")
            
            # 执行风险评估
            risk_assessment = await self.assess_risk(message.content["prediction_result"])
            
            # 发送最终结果给数据收集智能体和其他相关方
            final_result = {
                "prediction": message.content["prediction_result"],
                "risk_assessment": risk_assessment,
                "confidence": risk_assessment.get("confidence", 0.0),
                "recommendation": risk_assessment.get("recommendation", "neutral")
            }
            
            response_msg = Message(
                MessageType.RESPONSE,
                self.name,
                "data_collection_agent",  # 发送回起始智能体
                {
                    "request_type": "prediction_result",
                    "final_result": final_result,
                    "match_id": message.content["match_id"]
                }
            )
            await self.comm_hub.send_message(response_msg)
            logger.info(f"Final result sent to data_collection_agent for match {message.content['match_id']}")
    
    async def assess_risk(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """执行风险评估"""
        # 获取预测结果
        probs = prediction.get("probabilities", {})
        confidence = prediction.get("confidence", 0)
        
        # 计算熵值来评估不确定性
        import math
        entropy = 0
        for prob in probs.values():
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        # 最大熵为log2(3) ≈ 1.58，表示完全随机
        max_entropy = math.log2(3) if len(probs) > 0 else 1
        normalized_uncertainty = entropy / max_entropy
        
        # 风险评估
        if confidence > 0.7 and normalized_uncertainty < 0.5:
            risk_level = "low"
            recommendation = "consider"
        elif confidence > 0.5 and normalized_uncertainty < 0.7:
            risk_level = "medium"
            recommendation = "monitor"
        else:
            risk_level = "high"
            recommendation = "avoid"
        
        return {
            "risk_level": risk_level,
            "confidence": confidence,
            "uncertainty": round(normalized_uncertainty, 3),
            "recommendation": recommendation,
            "factors_considered": [
                "Prediction confidence",
                "Outcome uncertainty",
                "Market odds alignment"
            ]
        }