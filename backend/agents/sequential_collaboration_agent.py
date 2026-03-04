"""
基于LangChain SequentialChain的智能体协作机制
将平局预测智能体与对冲策略智能体串联执行
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain.chains import SequentialChain
from langchain.prompts import PromptTemplate

from .enhanced_base_agent import EnhancedBaseAgent, AgentCapability
from ..services.langchain_service import LangChainService

logger = logging.getLogger(__name__)


class SequentialCollaborationAgent(EnhancedBaseAgent):
    """顺序协作智能体"""
    
    def __init__(
        self,
        name: str,
        description: str,
        langchain_service: LangChainService,
        config: Optional[Dict[str, Any]] = None
    ):
        capabilities = [
            AgentCapability.DATA_PROCESSING,
            AgentCapability.PREDICTION,
            AgentCapability.ANALYSIS,
            AgentCapability.RECOMMENDATION,
            AgentCapability.COLLABORATION
        ]
        
        super().__init__(
            name=name,
            description=description,
            capabilities=capabilities,
            langchain_service=langchain_service,
            config=config
        )
        
        # 协作链名称
        self.collaboration_chain_name = "draw_hedging_collaboration"
        
        # 初始化协作链
        self._initialize_collaboration_chain()
    
    def _initialize_collaboration_chain(self):
        """初始化协作顺序链"""
        if not self.langchain_service:
            logger.warning("LangChain服务未配置，无法创建协作链")
            return
        
        # 定义平局预测链配置
        draw_prediction_chain_config = {
            "name": "draw_prediction",
            "template": """你是一位专业的足球比赛分析师。基于以下比赛数据，分析平局概率：

比赛信息：{match_info}
历史交锋：{historical_data}
当前赔率：{current_odds}

请按以下格式提供分析：
1. 平局概率分析：根据历史交锋、球队状态、赔率等因素，给出平局的概率（0-1之间）
2. 关键因素：列出影响平局概率的关键因素
3. 预测结果：给出最终的平局概率和置信度
4. 建议：基于分析给出投资建议

分析结果：""",
            "input_variables": ["match_info", "historical_data", "current_odds"],
            "output_key": "draw_prediction"
        }
        
        # 定义对冲策略链配置（基于平局预测结果）
        hedging_strategy_chain_config = {
            "name": "hedging_strategy",
            "template": """你是一位专业的风险管理和对冲策略分析师。基于以下平局预测结果，分析对冲机会：

平局预测结果：{draw_prediction}
市场条件：{market_conditions}
可用资金：{available_capital}

请按以下格式提供分析：
1. 对冲必要性评估：基于平局概率和风险水平，评估是否需要对冲
2. 对冲策略建议：给出具体的对冲策略（如比例对冲、期权对冲等）
3. 风险收益分析：分析对冲策略的潜在风险和回报
4. 执行计划：给出具体的执行步骤和时间安排

分析结果：""",
            "input_variables": ["draw_prediction", "market_conditions", "available_capital"],
            "output_key": "hedging_strategy"
        }
        
        # 创建顺序链
        try:
            sequential_chain = self.langchain_service.create_sequential_chain(
                chain_name=self.collaboration_chain_name,
                chains_config=[draw_prediction_chain_config, hedging_strategy_chain_config]
            )
            
            # 存储到链字典
            self._chains[self.collaboration_chain_name] = sequential_chain
            logger.info(f"协作顺序链 '{self.collaboration_chain_name}' 创建成功")
            
        except Exception as e:
            logger.error(f"创建协作顺序链失败: {e}")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行协作分析"""
        if self.collaboration_chain_name not in self._chains:
            return {
                "success": False,
                "error": "协作链未初始化",
                "timestamp": datetime.now().isoformat()
            }
        
        # 准备输入数据
        inputs = self._prepare_collaboration_inputs(context)
        
        # 验证必需字段
        required_fields = ["match_info", "historical_data", "current_odds", 
                          "market_conditions", "available_capital"]
        for field in required_fields:
            if field not in inputs:
                return {
                    "success": False,
                    "error": f"缺少必需字段: {field}",
                    "timestamp": datetime.now().isoformat()
                }
        
        start_time = datetime.now()
        
        try:
            # 执行协作链
            result = await self.langchain_service.run_chain(
                self.collaboration_chain_name,
                inputs
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if result.get("success"):
                # 解析结果
                collaboration_result = self._parse_collaboration_result(result["result"])
                
                # 更新执行状态
                self._execution_count += 1
                self._last_execution = datetime.now()
                
                return {
                    "success": True,
                    "result": collaboration_result,
                    "execution_time": execution_time,
                    "chain_used": self.collaboration_chain_name,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                self._error_count += 1
                return {
                    "success": False,
                    "error": result.get("error", "协作链执行失败"),
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._error_count += 1
            
            logger.error(f"协作智能体执行失败: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def _prepare_collaboration_inputs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """准备协作链输入数据"""
        # 从上下文中提取或使用默认值
        inputs = {
            "match_info": context.get("match_info", ""),
            "historical_data": context.get("historical_data", ""),
            "current_odds": context.get("current_odds", ""),
            "market_conditions": context.get("market_conditions", "正常"),
            "available_capital": context.get("available_capital", "10000")
        }
        
        # 如果提供了比赛ID，尝试从数据库获取数据
        match_id = context.get("match_id")
        if match_id:
            try:
                # 导入数据库会话
                from ..core.database import SessionLocal
                
                # 创建数据库会话
                db = SessionLocal()
                try:
                    # 导入模型
                    from ..models.match import Match
                    from ..models.odds import Odds
                    from ..models.team import Team
                    from ..models.league import League
                    
                    # 查询比赛信息
                    match = db.query(Match).filter(Match.id == match_id).first()
                    
                    if match:
                        # 构建比赛信息
                        match_info = f"{match.home_team.name} vs {match.away_team.name} - {match.league.name if match.league else '未知联赛'}"
                        match_info += f"\n比赛时间: {match.match_date} {match.match_time}"
                        match_info += f"\n状态: {match.status.value}"
                        
                        if match.home_score is not None and match.away_score is not None:
                            match_info += f"\n当前比分: {match.home_score}-{match.away_score}"
                        
                        # 构建历史交锋信息（简化版本）
                        historical_data = f"比赛ID: {match.id}, 联赛: {match.league.name if match.league else '未知'}"
                        
                        # 查询赔率信息
                        odds_list = db.query(Odds).filter(Odds.match_id == match_id).all()
                        if odds_list:
                            # 使用最新的赔率
                            latest_odds = max(odds_list, key=lambda x: x.last_updated if x.last_updated else datetime.min)
                            current_odds = f"胜: {latest_odds.home_win_odds}, 平: {latest_odds.draw_odds}, 负: {latest_odds.away_win_odds}"
                            
                            if latest_odds.asian_handicap_home:
                                current_odds += f"\n亚洲盘口: 主队让{latest_odds.handicap_line}球, 赔率: {latest_odds.asian_handicap_home}"
                            
                            if latest_odds.over_under_line:
                                current_odds += f"\n大小球: {latest_odds.over_under_line}球, 大球: {latest_odds.over_odds}, 小球: {latest_odds.under_odds}"
                        else:
                            current_odds = "暂无赔率数据"
                        
                        # 更新输入数据
                        inputs["match_info"] = match_info
                        inputs["historical_data"] = historical_data
                        inputs["current_odds"] = current_odds
                        
                        logger.info(f"从数据库获取比赛数据成功: match_id={match_id}")
                    else:
                        logger.warning(f"未找到比赛数据: match_id={match_id}")
                        
                except ImportError as e:
                    logger.warning(f"导入数据库模型失败: {e}, 使用默认数据")
                except Exception as e:
                    logger.error(f"从数据库获取数据失败: {e}, 使用默认数据")
                finally:
                    db.close()
                    
            except ImportError as e:
                logger.warning(f"导入数据库会话失败: {e}, 使用默认数据")
        
        return inputs
    
    def _parse_collaboration_result(self, raw_result: Any) -> Dict[str, Any]:
        """解析协作链的原始结果"""
        try:
            # 根据链的输出结构解析
            # SequentialChain通常返回字典，包含各子链的输出
            if isinstance(raw_result, dict):
                # 假设链返回了draw_prediction和hedging_strategy
                draw_prediction = raw_result.get("draw_prediction", "")
                hedging_strategy = raw_result.get("hedging_strategy", "")
                
                # 提取关键信息
                collaboration_summary = {
                    "draw_analysis": self._extract_draw_analysis(draw_prediction),
                    "hedging_recommendation": self._extract_hedging_recommendation(hedging_strategy),
                    "overall_risk_level": self._assess_overall_risk(draw_prediction, hedging_strategy),
                    "recommended_action": self._determine_recommended_action(draw_prediction, hedging_strategy),
                    "raw_predictions": {
                        "draw_prediction": draw_prediction[:500] + "..." if len(draw_prediction) > 500 else draw_prediction,
                        "hedging_strategy": hedging_strategy[:500] + "..." if len(hedging_strategy) > 500 else hedging_strategy
                    }
                }
                
                return collaboration_summary
            else:
                # 如果是字符串结果，尝试解析
                return {
                    "raw_output": str(raw_result)[:1000],
                    "parsing_method": "raw_string"
                }
                
        except Exception as e:
            logger.error(f"解析协作结果失败: {e}")
            return {
                "raw_output": str(raw_result),
                "parsing_error": str(e)
            }
    
    def _extract_draw_analysis(self, prediction_text: str) -> Dict[str, Any]:
        """从预测文本中提取平局分析"""
        # 简单的文本分析逻辑
        # 在实际应用中可能需要更复杂的NLP处理
        
        analysis = {
            "draw_probability": 0.5,  # 默认值
            "confidence": 0.7,
            "key_factors": [],
            "recommendation": "neutral"
        }
        
        # 尝试提取概率
        import re
        prob_patterns = [
            r'平局概率[：:]\s*([0-9]*\.?[0-9]+)',
            r'概率[：:]\s*([0-9]*\.?[0-9]+)',
            r'([0-9]*\.?[0-9]+)%'
        ]
        
        for pattern in prob_patterns:
            match = re.search(pattern, prediction_text)
            if match:
                try:
                    prob = float(match.group(1))
                    if prob > 1 and prob <= 100:
                        prob = prob / 100
                    analysis["draw_probability"] = min(max(prob, 0), 1)
                    break
                except ValueError:
                    continue
        
        # 尝试提取置信度
        confidence_patterns = [
            r'置信度[：:]\s*([0-9]*\.?[0-9]+)',
            r'置信水平[：:]\s*([0-9]*\.?[0-9]+)'
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, prediction_text)
            if match:
                try:
                    confidence = float(match.group(1))
                    if confidence > 1 and confidence <= 100:
                        confidence = confidence / 100
                    analysis["confidence"] = min(max(confidence, 0), 1)
                    break
                except ValueError:
                    continue
        
        # 提取关键因素（简单版本）
        lines = prediction_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['因素', '关键', '影响', 'reason', 'factor']):
                analysis["key_factors"].append(line.strip())
        
        # 提取建议
        for line in lines:
            if any(keyword in line.lower() for keyword in ['建议', '推荐', '建议', 'recommendation']):
                analysis["recommendation"] = line.strip()
                break
        
        return analysis
    
    def _extract_hedging_recommendation(self, strategy_text: str) -> Dict[str, Any]:
        """从策略文本中提取对冲建议"""
        recommendation = {
            "hedging_needed": True,
            "strategy_type": "比例对冲",
            "hedge_ratio": 0.5,
            "risk_level": "medium",
            "expected_return": 0.1,
            "execution_steps": []
        }
        
        # 简单的文本分析
        text_lower = strategy_text.lower()
        
        if "不需要对冲" in text_lower or "无需对冲" in text_lower:
            recommendation["hedging_needed"] = False
        
        # 识别策略类型
        if "比例对冲" in text_lower or "proportional" in text_lower:
            recommendation["strategy_type"] = "比例对冲"
        elif "期权" in text_lower or "option" in text_lower:
            recommendation["strategy_type"] = "期权对冲"
        elif "跨市场" in text_lower or "cross-market" in text_lower:
            recommendation["strategy_type"] = "跨市场对冲"
        
        # 提取对冲比例
        import re
        ratio_pattern = r'对冲比例[：:]\s*([0-9]*\.?[0-9]+)'
        match = re.search(ratio_pattern, strategy_text)
        if match:
            try:
                ratio = float(match.group(1))
                if ratio > 1 and ratio <= 100:
                    ratio = ratio / 100
                recommendation["hedge_ratio"] = min(max(ratio, 0), 1)
            except ValueError:
                pass
        
        # 提取风险级别
        if "高风险" in text_lower or "high risk" in text_lower:
            recommendation["risk_level"] = "high"
        elif "低风险" in text_lower or "low risk" in text_lower:
            recommendation["risk_level"] = "low"
        
        # 提取执行步骤
        lines = strategy_text.split('\n')
        for line in lines:
            if any(marker in line for marker in ['1.', '2.', '3.', '第一步', '第二步', '第三步', '步骤']):
                recommendation["execution_steps"].append(line.strip())
        
        return recommendation
    
    def _assess_overall_risk(self, draw_prediction: str, hedging_strategy: str) -> str:
        """评估整体风险水平"""
        # 简单的风险评估逻辑
        draw_text = draw_prediction.lower()
        hedge_text = hedging_strategy.lower()
        
        risk_keywords = {
            "high": ["高风险", "high risk", "危险", "不建议", "避免"],
            "low": ["低风险", "low risk", "安全", "推荐", "建议"],
            "medium": ["中等风险", "medium risk", "适中", "监控"]
        }
        
        for risk_level, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword in draw_text or keyword in hedge_text:
                    return risk_level
        
        return "medium"  # 默认中等风险
    
    def _determine_recommended_action(self, draw_prediction: str, hedging_strategy: str) -> str:
        """确定推荐行动"""
        # 基于分析和风险的综合决策
        overall_risk = self._assess_overall_risk(draw_prediction, hedging_strategy)
        
        if overall_risk == "high":
            return "avoid"  # 避免投资
        elif overall_risk == "low":
            return "invest"  # 建议投资
        else:
            return "monitor"  # 监控市场