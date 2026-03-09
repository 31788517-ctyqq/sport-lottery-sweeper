#!/usr/bin/env python3
"""
平局预测智能体
基于LangChain构建的平局预测智能体，用于分析比赛数据并预测平局概率
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio

from .base_agent import BaseAgent
from ..services.prediction_service import DrawPredictionService
from ..services.langchain_service import LangChainService, create_preset_chain
from ..services.llm_service import LLMService
from ..database import get_db

logger = logging.getLogger(__name__)


class DrawPredictionAgent(BaseAgent):
    """平局预测智能体"""
    
    def __init__(
        self, 
        name: str, 
        config: Dict[str, Any],
        langchain_service: Optional[LangChainService] = None,
        prediction_service: Optional[DrawPredictionService] = None
    ):
        super().__init__(name, config)
        
        # 初始化服务
        self.langchain_service = langchain_service or self._create_langchain_service()
        self.prediction_service = prediction_service or self._create_prediction_service()
        
        # 创建预测链
        self._setup_prediction_chains()
        
        logger.info(f"平局预测智能体 '{name}' 初始化完成")
    
    def _create_langchain_service(self) -> LangChainService:
        """创建LangChain服务"""
        # 创建LLM服务
        llm_service = LLMService()
        
        # 从配置或环境变量中获取API密钥
        openai_api_key = self.config.get("openai_api_key")
        gemini_api_key = self.config.get("gemini_api_key")
        qwen_api_key = self.config.get("qwen_api_key")
        
        # 注册提供商（至少需要一个）
        if openai_api_key and openai_api_key != "your-openai-api-key-here":
            llm_service.register_provider("openai", openai_api_key)
            llm_service.set_default_provider("openai")
        elif qwen_api_key and qwen_api_key != "your-qwen-api-key-here":
            llm_service.register_provider("qwen", qwen_api_key)
            llm_service.set_default_provider("qwen")
        elif gemini_api_key and gemini_api_key != "your-gemini-api-key-here":
            llm_service.register_provider("gemini", gemini_api_key)
            llm_service.set_default_provider("gemini")
        else:
            # 如果没有配置，尝试使用环境变量
            import os
            if os.getenv("OPENAI_API_KEY"):
                llm_service.register_provider("openai", os.getenv("OPENAI_API_KEY"))
                llm_service.set_default_provider("openai")
            elif os.getenv("QWEN_API_KEY"):
                llm_service.register_provider("qwen", os.getenv("QWEN_API_KEY"))
                llm_service.set_default_provider("qwen")
            elif os.getenv("GEMINI_API_KEY"):
                llm_service.register_provider("gemini", os.getenv("GEMINI_API_KEY"))
                llm_service.set_default_provider("gemini")
            else:
                logger.warning("没有配置有效的LLM API密钥，智能体功能可能受限")
        
        # 创建LangChain服务
        return LangChainService(llm_service)
    
    def _create_prediction_service(self) -> DrawPredictionService:
        """创建预测服务"""
        from sqlalchemy.orm import Session
        db = next(get_db())
        return DrawPredictionService(db)
    
    def _setup_prediction_chains(self):
        """设置预测链"""
        try:
            # 创建平局预测链
            self.prediction_chain = create_preset_chain(
                self.langchain_service, 
                "prediction_analysis", 
                "draw_prediction_chain"
            )
            logger.info("平局预测链创建成功")
        except Exception as e:
            logger.warning(f"创建预设链失败，使用自定义链: {e}")
            # 创建自定义链
            template = """基于以下比赛数据，分析平局概率：

比赛信息：{match_info}
历史数据：{historical_data}
赔率信息：{odds_data}

请提供详细的概率分析和理由："""
            
            self.prediction_chain = self.langchain_service.create_simple_chain(
                chain_name="draw_prediction_custom",
                template=template,
                input_variables=["match_info", "historical_data", "odds_data"]
            )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行平局预测任务"""
        match_id = context.get("match_id")
        
        if not match_id:
            return {
                "success": False,
                "error": "缺少比赛ID参数"
            }
        
        logger.info(f"开始平局预测分析，比赛ID: {match_id}")
        
        try:
            # 1. 收集比赛数据
            match_data = await self._collect_match_data(match_id)
            
            # 2. 使用统计学方法计算平局概率
            statistical_result = self.prediction_service.calculate_draw_probability_statistical(match_id)
            
            # 3. 使用LangChain链进行深入分析
            llm_analysis = await self._run_llm_analysis(match_data, statistical_result)
            
            # 4. 综合结果
            combined_result = self._combine_results(statistical_result, llm_analysis)
            
            # 5. 生成建议
            recommendation = self._generate_recommendation(combined_result)
            
            logger.info(f"平局预测完成，比赛ID: {match_id}")
            
            return {
                "success": True,
                "match_id": match_id,
                "statistical_analysis": statistical_result,
                "llm_analysis": llm_analysis,
                "combined_result": combined_result,
                "recommendation": recommendation,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"平局预测失败，比赛ID {match_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "match_id": match_id
            }
    
    async def _collect_match_data(self, match_id: int) -> Dict[str, Any]:
        """收集比赛相关数据"""
        from sqlalchemy.orm import Session
        db = next(get_db())
        
        # 获取比赛基本信息
        from ..models.match import Match
        match = db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            raise ValueError(f"比赛ID {match_id} 不存在")
        
        # 获取历史交锋数据
        historical_data = self._get_head_to_head_data(match.home_team_id, match.away_team_id)
        
        # 获取赔率数据
        from ..models.odds import Odds
        odds = db.query(Odds).filter(Odds.match_id == match_id).all()
        
        return {
            "match_info": {
                "home_team": match.home_team.name if match.home_team else "未知",
                "away_team": match.away_team.name if match.away_team else "未知",
                "league": match.league.name if match.league else "未知",
                "match_date": match.match_date.isoformat() if match.match_date else "未知",
                "importance": match.importance.value if match.importance else "未知"
            },
            "historical_data": historical_data,
            "odds_data": [
                {
                    "bookmaker": o.bookmaker,
                    "home_win": o.home_win,
                    "draw": o.draw,
                    "away_win": o.away_win,
                    "timestamp": o.created_at.isoformat() if o.created_at else "未知"
                }
                for o in odds
            ]
        }
    
    def _get_head_to_head_data(self, home_team_id: int, away_team_id: int) -> Dict[str, Any]:
        """获取两队历史交锋数据"""
        from sqlalchemy.orm import Session
        db = next(get_db())
        
        from ..models.match import Match, MatchStatusEnum
        from datetime import datetime
        
        # 查询两队历史交锋
        matches = db.query(Match).filter(
            Match.status == MatchStatusEnum.FINISHED,
            Match.home_team_id.in_([home_team_id, away_team_id]),
            Match.away_team_id.in_([home_team_id, away_team_id])
        ).order_by(Match.match_date.desc()).limit(10).all()
        
        if not matches:
            return {"message": "无历史交锋数据"}
        
        # 统计交锋结果
        home_wins = draws = away_wins = 0
        total_goals = 0
        
        for match in matches:
            if match.home_score is None or match.away_score is None:
                continue
                
            total_goals += match.home_score + match.away_score
            
            if match.home_score == match.away_score:
                draws += 1
            elif (match.home_team_id == home_team_id and match.home_score > match.away_score) or \
                 (match.away_team_id == home_team_id and match.away_score > match.home_score):
                home_wins += 1
            else:
                away_wins += 1
        
        return {
            "total_matches": len(matches),
            "home_wins": home_wins,
            "draws": draws,
            "away_wins": away_wins,
            "home_win_rate": home_wins / len(matches) if matches else 0,
            "draw_rate": draws / len(matches) if matches else 0,
            "avg_goals_per_match": total_goals / len(matches) if matches else 0,
            "recent_matches": [
                {
                    "date": m.match_date.isoformat() if m.match_date else "未知",
                    "home_team": m.home_team.name if m.home_team else "未知",
                    "away_team": m.away_team.name if m.away_team else "未知",
                    "score": f"{m.home_score or '?'}-{m.away_score or '?'}"
                }
                for m in matches[:5]
            ]
        }
    
    async def _run_llm_analysis(self, match_data: Dict[str, Any], statistical_result: Dict[str, Any]) -> Dict[str, Any]:
        """使用LangChain链进行深入分析"""
        try:
            # 准备输入数据
            match_info = str(match_data["match_info"])
            historical_data = str(match_data["historical_data"])
            odds_data = str(match_data["odds_data"])
            
            # 如果有统计结果，也加入上下文
            statistical_summary = f"统计平局概率: {statistical_result.get('probability', 0):.2%}"
            
            inputs = {
                "match_info": match_info,
                "historical_data": historical_data + "\n\n" + statistical_summary,
                "odds_data": odds_data
            }
            
            # 运行链
            result = await self.langchain_service.run_chain("draw_prediction_chain", inputs)
            
            if result["success"]:
                return {
                    "analysis": result["result"],
                    "chain_used": result["chain"]
                }
            else:
                logger.warning(f"LangChain链执行失败: {result.get('error')}")
                return {
                    "analysis": "LangChain分析失败，使用备用分析",
                    "error": result.get("error"),
                    "fallback_analysis": self._generate_fallback_analysis(match_data, statistical_result)
                }
                
        except Exception as e:
            logger.error(f"LangChain分析异常: {e}")
            return {
                "analysis": f"分析异常: {str(e)}",
                "fallback_analysis": self._generate_fallback_analysis(match_data, statistical_result)
            }
    
    def _generate_fallback_analysis(self, match_data: Dict[str, Any], statistical_result: Dict[str, Any]) -> str:
        """生成备用分析（当LangChain失败时）"""
        draw_rate = statistical_result.get('probability', 0)
        historical = match_data["historical_data"]
        
        if isinstance(historical, dict) and "draw_rate" in historical:
            historical_draw_rate = historical["draw_rate"]
        else:
            historical_draw_rate = 0
        
        avg_draw_rate = (draw_rate + historical_draw_rate) / 2
        
        if avg_draw_rate > 0.3:
            confidence = "高"
        elif avg_draw_rate > 0.2:
            confidence = "中"
        else:
            confidence = "低"
        
        return f"基于统计模型和历史数据的综合分析：平局概率约{avg_draw_rate:.1%}（{confidence}置信度）"
    
    def _combine_results(self, statistical_result: Dict[str, Any], llm_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """综合统计结果和LLM分析结果"""
        statistical_prob = statistical_result.get('probability', 0)
        
        # 尝试从LLM分析中提取概率（如果有）
        llm_prob = self._extract_probability_from_llm(llm_analysis.get('analysis', ''))
        
        if llm_prob is not None:
            # 加权平均：统计结果权重0.6，LLM分析权重0.4
            combined_prob = statistical_prob * 0.6 + llm_prob * 0.4
        else:
            combined_prob = statistical_prob
        
        return {
            "combined_probability": combined_prob,
            "statistical_probability": statistical_prob,
            "llm_probability": llm_prob,
            "confidence": "高" if combined_prob > 0.25 else ("中" if combined_prob > 0.15 else "低"),
            "data_sources": ["statistical_model", "llm_analysis"]
        }
    
    def _extract_probability_from_llm(self, analysis_text: str) -> Optional[float]:
        """从LLM分析文本中提取概率值"""
        import re
        
        # 尝试匹配百分比模式，如 "30%", "25.5%", "约30%"
        percent_pattern = r'(\d+(?:\.\d+)?)\s*%'
        percent_matches = re.findall(percent_pattern, analysis_text)
        
        if percent_matches:
            # 取第一个匹配的百分比
            return float(percent_matches[0]) / 100
        
        # 尝试匹配小数模式，如 "0.3", "0.25"
        decimal_pattern = r'\b0?\.\d+\b'
        decimal_matches = re.findall(decimal_pattern, analysis_text)
        
        if decimal_matches:
            return float(decimal_matches[0])
        
        return None
    
    def _generate_recommendation(self, combined_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成投注建议"""
        probability = combined_result.get('combined_probability', 0)
        confidence = combined_result.get('confidence', '低')
        
        if probability > 0.3:
            recommendation = "强烈建议"
            risk_level = "低"
            suggested_stake = "中等偏上"
        elif probability > 0.25:
            recommendation = "建议"
            risk_level = "中"
            suggested_stake = "中等"
        elif probability > 0.2:
            recommendation = "谨慎考虑"
            risk_level = "中高"
            suggested_stake = "小"
        else:
            recommendation = "不建议"
            risk_level = "高"
            suggested_stake = "避免"
        
        return {
            "recommendation": recommendation,
            "probability": probability,
            "confidence": confidence,
            "risk_level": risk_level,
            "suggested_stake": suggested_stake,
            "reasoning": f"基于综合分析的平局概率为{probability:.1%}（{confidence}置信度）"
        }
    
    async def batch_predict(self, match_ids: List[int]) -> List[Dict[str, Any]]:
        """批量预测多场比赛"""
        results = []
        
        for match_id in match_ids:
            try:
                result = await self.execute({"match_id": match_id})
                results.append(result)
            except Exception as e:
                logger.error(f"批量预测失败，比赛ID {match_id}: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "match_id": match_id
                })
        
        return results
    
    async def predict_with_external_data(self, match_id: int, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用外部数据进行预测"""
        # 合并外部数据
        context = {"match_id": match_id, "external_data": external_data}
        
        # 重写数据收集方法以包含外部数据
        original_collect = self._collect_match_data
        
        async def enhanced_collect(match_id: int):
            data = await original_collect(match_id)
            data["external_data"] = external_data
            return data
        
        self._collect_match_data = enhanced_collect
        
        try:
            result = await self.execute(context)
            return result
        finally:
            # 恢复原方法
            self._collect_match_data = original_collect


# 工厂函数
def create_draw_prediction_agent(
    name: str = "draw_prediction_agent",
    config: Optional[Dict[str, Any]] = None
) -> DrawPredictionAgent:
    """创建平局预测智能体"""
    default_config = {
        "agent_type": "business",
        "description": "平局预测智能体，基于统计模型和LLM分析",
        "enabled": True,
        "max_concurrent": 3,
        "timeout": 300,
        "openai_api_key": None,  # 从环境变量获取
        "qwen_api_key": None,
        "gemini_api_key": None
    }
    
    if config:
        default_config.update(config)
    
    return DrawPredictionAgent(name, default_config)