#!/usr/bin/env python3
"""
预测算法业务逻辑服务
实现平局预测和其他预测算法
"""

import logging
import statistics
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict
import numpy as np

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from database import get_db
from models.match import Match, MatchStatusEnum, MatchImportanceEnum
from models.predictions import Prediction, PredictionTypeEnum, PredictionAccuracyEnum
from models.draw_prediction_result import DrawPredictionResult, ModelTypeEnum, PredictionConfidenceEnum
from models.intelligence import Intelligence, IntelligenceTypeEnum
from models.odds import Odds, OddsTypeEnum
from core.exceptions import ValidationException, NotFoundException, BusinessException

logger = logging.getLogger(__name__)

class DrawPredictionService:
    """平局预测服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_historical_draw_rate(self, team_id: int, league_id: int, 
                                    lookback_days: int = 365) -> float:
        """计算历史平局率"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=lookback_days)
            
            # 获取该队伍的历史比赛
            matches = self.db.query(Match).filter(
                and_(
                    Match.match_date >= start_date,
                    Match.match_date <= end_date,
                    Match.status == MatchStatusEnum.FINISHED,
                    or_(
                        Match.home_team_id == team_id,
                        Match.away_team_id == team_id
                    )
                )
            ).all()
            
            if not matches:
                return 0.0
            
            # 计算平局场次
            draw_count = 0
            for match in matches:
                if match.home_score is not None and match.away_score is not None:
                    if match.home_score == match.away_score:
                        draw_count += 1
            
            return draw_count / len(matches) if matches else 0.0
            
        except Exception as e:
            logger.error(f"计算历史平局率失败: {e}")
            return 0.0
    
    def analyze_team_form(self, team_id: int, lookback_matches: int = 10) -> Dict[str, Any]:
        """分析队伍近期状态"""
        try:
            # 获取近期比赛
            matches = self.db.query(Match).filter(
                and_(
                    Match.status == MatchStatusEnum.FINISHED,
                    or_(
                        Match.home_team_id == team_id,
                        Match.away_team_id == team_id
                    )
                )
            ).order_by(Match.match_date.desc()).limit(lookback_matches).all()
            
            if not matches:
                return {
                    "form_score": 0.5,
                    "recent_draws": 0,
                    "recent_wins": 0,
                    "recent_losses": 0,
                    "avg_goals_scored": 0.0,
                    "avg_goals_conceded": 0.0
                }
            
            # 计算战绩
            wins = draws = losses = 0
            goals_scored = goals_conceded = 0
            
            for match in matches:
                if match.home_score is None or match.away_score is None:
                    continue
                
                if match.home_team_id == team_id:
                    team_score = match.home_score
                    opponent_score = match.away_score
                else:
                    team_score = match.away_score
                    opponent_score = match.home_score
                
                goals_scored += team_score
                goals_conceded += opponent_score
                
                if team_score > opponent_score:
                    wins += 1
                elif team_score == opponent_score:
                    draws += 1
                else:
                    losses += 1
            
            total_matches = len([m for m in matches if m.home_score is not None])
            if total_matches == 0:
                total_matches = 1
            
            form_score = (wins * 3 + draws) / (total_matches * 3)  # 标准化到0-1
            
            return {
                "form_score": min(max(form_score, 0.0), 1.0),
                "recent_draws": draws,
                "recent_wins": wins,
                "recent_losses": losses,
                "avg_goals_scored": goals_scored / total_matches,
                "avg_goals_conceded": goals_conceded / total_matches,
                "total_recent_matches": total_matches
            }
            
        except Exception as e:
            logger.error(f"分析队伍状态失败: {e}")
            return {"form_score": 0.5, "recent_draws": 0, "recent_wins": 0, "recent_losses": 0}
    
    def calculate_draw_probability_statistical(self, match_id: int) -> Dict[str, Any]:
        """基于统计学方法计算平局概率"""
        try:
            match = self.db.query(Match).filter(Match.id == match_id).first()
            if not match:
                raise NotFoundException("比赛")
            
            # 获取联赛历史平局率
            league_matches = self.db.query(Match).filter(
                and_(
                    Match.league_id == match.league_id,
                    Match.status == MatchStatusEnum.FINISHED,
                    Match.match_date >= datetime.utcnow() - timedelta(days=730)  # 2年数据
                )
            ).all()
            
            if not league_matches:
                base_probability = 0.25  # 默认平局概率
            else:
                draw_count = sum(1 for m in league_matches 
                               if m.home_score is not None and m.home_score == m.away_score)
                base_probability = draw_count / len(league_matches)
            
            # 分析主队和客队的历史平局率
            home_draw_rate = self.calculate_historical_draw_rate(match.home_team_id, match.league_id)
            away_draw_rate = self.calculate_historical_draw_rate(match.away_team_id, match.league_id)
            
            # 分析两队近期状态
            home_form = self.analyze_team_form(match.home_team_id)
            away_form = self.analyze_team_form(match.away_team_id)
            
            # 计算综合概率（加权平均）
            weights = {
                'league_base': 0.3,
                'home_history': 0.25,
                'away_history': 0.25,
                'home_form': 0.1,
                'away_form': 0.1
            }
            
            # 形式分数转换为平局倾向（形式平衡的队伍更容易平局）
            home_draw_tendency = 1.0 - abs(home_form['form_score'] - 0.5) * 2
            away_draw_tendency = 1.0 - abs(away_form['form_score'] - 0.5) * 2
            
            statistical_probability = (
                base_probability * weights['league_base'] +
                home_draw_rate * weights['home_history'] +
                away_draw_rate * weights['away_history'] +
                home_draw_tendency * weights['home_form'] +
                away_draw_tendency * weights['away_form']
            )
            
            # 确保概率在合理范围内
            statistical_probability = min(max(statistical_probability, 0.05), 0.8)
            
            confidence_score = self._calculate_confidence_score(
                len(league_matches), 
                home_form['total_recent_matches'],
                away_form['total_recent_matches']
            )
            
            return {
                "probability": round(statistical_probability, 4),
                "confidence_score": confidence_score,
                "factors": {
                    "league_base_rate": round(base_probability, 4),
                    "home_team_draw_rate": round(home_draw_rate, 4),
                    "away_team_draw_rate": round(away_draw_rate, 4),
                    "home_form_factor": round(home_draw_tendency, 4),
                    "away_form_factor": round(away_draw_tendency, 4)
                },
                "model_type": "statistical"
            }
            
        except Exception as e:
            logger.error(f"统计学平局预测失败: {e}")
            raise BusinessException(f"平局预测计算失败: {str(e)}")
    
    def _calculate_confidence_score(self, league_matches: int, home_matches: int, 
                                  away_matches: int) -> float:
        """计算预测置信度分数"""
        # 基于数据量计算置信度
        data_confidence = min((league_matches + home_matches + away_matches) / 100.0, 1.0)
        
        # 最小置信度保证
        confidence = max(data_confidence, 0.3)
        return round(confidence, 3)
    
    def predict_match_draw(self, match_id: int, model_version: str = "v1.0") -> DrawPredictionResult:
        """预测单场比赛平局概率"""
        try:
            # 计算统计学概率
            prediction_result = self.calculate_draw_probability_statistical(match_id)
            
            # 确定置信度等级
            confidence_score = prediction_result['confidence_score']
            if confidence_score >= 0.8:
                confidence_level = PredictionConfidenceEnum.HIGH
            elif confidence_score >= 0.6:
                confidence_level = PredictionConfidenceEnum.MEDIUM
            elif confidence_score >= 0.4:
                confidence_level = PredictionConfidenceEnum.LOW
            else:
                confidence_level = PredictionConfidenceEnum.VERY_LOW
            
            # 创建预测结果记录
            prediction = DrawPredictionResult(
                match_id=match_id,
                model_version=model_version,
                model_type=ModelTypeEnum.STATISTICAL,
                predicted_draw_probability=prediction_result['probability'],
                confidence_score=confidence_score,
                confidence_level=confidence_level,
                factors=prediction_result['factors'],
                recommendation=self._generate_recommendation(prediction_result['probability']),
                risk_factors=self._identify_risk_factors(match_id),
                valid_until=datetime.utcnow() + timedelta(hours=24)  # 24小时有效期
            )
            
            self.db.add(prediction)
            self.db.commit()
            self.db.refresh(prediction)
            
            logger.info(f"平局预测完成: 比赛{match_id}, 概率{prediction_result['probability']:.2%}")
            return prediction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"平局预测失败: {e}")
            raise
    
    def _generate_recommendation(self, probability: float) -> str:
        """生成投注建议"""
        if probability >= 0.4:
            return "高平局概率，建议关注平局选项"
        elif probability >= 0.25:
            return "中等平局概率，可考虑小额投注平局"
        elif probability >= 0.15:
            return "较低平局概率，不建议投注平局"
        else:
            return "极低平局概率，避免投注平局"
    
    def _identify_risk_factors(self, match_id: int) -> List[str]:
        """识别风险因素"""
        risk_factors = []
        
        try:
            match = self.db.query(Match).filter(Match.id == match_id).first()
            if not match:
                return ["比赛信息不完整"]
            
            # 检查比赛重要性
            if match.importance_level in [MatchImportanceEnum.VERY_HIGH, MatchImportanceEnum.HIGH]:
                risk_factors.append("重要比赛，变数较大")
            
            # 检查队伍实力差距（简化判断）
            home_form = self.analyze_team_form(match.home_team_id)
            away_form = self.analyze_team_form(match.away_team_id)
            
            form_diff = abs(home_form['form_score'] - away_form['form_score'])
            if form_diff > 0.3:
                risk_factors.append("队伍实力差距较大")
            
            # 检查数据充足性
            if home_form['total_recent_matches'] < 5 or away_form['total_recent_matches'] < 5:
                risk_factors.append("历史数据不足")
            
            if not risk_factors:
                risk_factors.append("无明显风险因素")
                
        except Exception as e:
            logger.error(f"识别风险因素失败: {e}")
            risk_factors.append("风险评估失败")
        
        return risk_factors
    
    def batch_predict_upcoming_matches(self, days_ahead: int = 7) -> List[DrawPredictionResult]:
        """批量预测即将到来的比赛"""
        try:
            upcoming_matches = self.get_upcoming_matches_for_prediction(days_ahead)
            predictions = []
            
            for match in upcoming_matches:
                try:
                    prediction = self.predict_match_draw(match.id)
                    predictions.append(prediction)
                except Exception as e:
                    logger.error(f"批量预测中单场预测失败 比赛{match.id}: {e}")
                    continue
            
            logger.info(f"批量预测完成: {len(predictions)}/{len(upcoming_matches)} 场比赛")
            return predictions
            
        except Exception as e:
            logger.error(f"批量预测失败: {e}")
            raise
    
    def get_upcoming_matches_for_prediction(self, days_ahead: int = 7) -> List[Match]:
        """获取适合预测的即将到来的比赛"""
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        matches = self.db.query(Match).filter(
            and_(
                Match.match_date >= datetime.utcnow(),
                Match.match_date <= end_date,
                Match.status == MatchStatusEnum.SCHEDULED,
                Match.allow_draw_prediction == True
            )
        ).order_by(Match.match_date.asc()).all()
        
        return matches
    
    def evaluate_prediction_accuracy(self, days_back: int = 30) -> Dict[str, Any]:
        """评估预测准确率"""
        try:
            # 获取最近的预测结果
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            predictions = self.db.query(DrawPredictionResult).filter(
                DrawPredictionResult.created_at >= cutoff_date
            ).all()
            
            if not predictions:
                return {"accuracy": 0.0, "total_predictions": 0, "evaluated_predictions": 0}
            
            correct_predictions = 0
            evaluated_predictions = 0
            
            for prediction in predictions:
                # 检查比赛是否已经结束
                match = self.db.query(Match).filter(Match.id == prediction.match_id).first()
                if not match or match.status != MatchStatusEnum.FINISHED:
                    continue
                
                if match.home_score is None or match.away_score is None:
                    continue
                
                # 判断是否平局
                is_draw = match.home_score == match.away_score
                predicted_draw = prediction.predicted_draw_probability >= 0.3  # 阈值
                
                if is_draw == predicted_draw:
                    correct_predictions += 1
                
                evaluated_predictions += 1
            
            accuracy = correct_predictions / evaluated_predictions if evaluated_predictions > 0 else 0.0
            
            return {
                "accuracy": round(accuracy, 4),
                "total_predictions": len(predictions),
                "evaluated_predictions": evaluated_predictions,
                "correct_predictions": correct_predictions,
                "evaluation_period_days": days_back
            }
            
        except Exception as e:
            logger.error(f"评估预测准确率失败: {e}")
            return {"accuracy": 0.0, "error": str(e)}

# 全局服务实例
def get_draw_prediction_service():
    """获取平局预测服务实例"""
    db = next(get_db())
    return DrawPredictionService(db)