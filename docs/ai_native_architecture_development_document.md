# 体育彩票业务AI原生架构融合技术开发文档

## 1. 项目概述

### 1.1 项目背景
本项目旨在将AI原生架构理念融入现有体育彩票业务系统，通过人工智能技术提升数据采集、预测分析、对冲策略等核心业务模块的智能化水平，从而提高业务效率和盈利能力。

### 1.2 目标架构
- **智能数据采集层**：AI驱动的多源数据采集与反爬虫对抗
- **智能预测分析层**：机器学习驱动的比赛结果预测
- **智能情报分析层**：自然语言处理驱动的情报分析
- **智能对冲策略层**：AI优化的对冲机会识别与资源配置

## 2. 系统架构设计

### 2.1 整体架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面层     │    │   API网关层     │    │   业务逻辑层     │
│  (Vue3 + TS)   │◄──►│  (FastAPI)     │◄──►│   AI服务层      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   数据存储层     │    │   任务调度层     │    │   ML模型层      │
│ (PostgreSQL/    │◄──►│  (Celery/RQ)   │◄──►│  (TensorFlow/   │
│   SQLite)      │    │                 │    │   Scikit-Learn) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 AI原生架构特点
- **自适应学习**：模型根据市场变化持续学习优化
- **智能决策**：基于数据驱动的自动化决策机制
- **风险控制**：AI驱动的风险评估与控制体系
- **资源优化**：智能化的计算与网络资源分配

## 3. 数据采集模块AI融合

### 3.1 智能爬虫引擎

在`backend/scrapers/core/enhanced_engine.py`中实现AI优化的数据采集：

```python
import asyncio
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
import time
from datetime import datetime
import aiohttp
from aiohttp import ClientTimeout, ClientSession

class AICrawlerEngine:
    """
    AI增强型爬虫引擎
    集成智能采集策略优化
    """
    
    def __init__(self, 
                 max_connections: int = 100,
                 timeout: int = 15,
                 max_retries: int = 3,
                 enable_ai_optimization: bool = True):
        self.max_connections = max_connections
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.enable_ai_optimization = enable_ai_optimization
        
        # AI优化组件
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=3, random_state=42)
        self.collection_patterns = {}  # 存储采集模式
        self.performance_history = []  # 性能历史记录
        
        # 连接池
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
    
    async def optimize_crawling_strategy(self, url: str, response_time: float, success_rate: float):
        """AI优化爬取策略"""
        if not self.enable_ai_optimization:
            return {"delay": 1.0, "concurrency": 5}  # 默认策略
        
        # 收集特征数据
        features = np.array([[response_time, success_rate, time.time()]])
        scaled_features = self.scaler.fit_transform(features)
        
        # 聚类分析确定最佳采集策略
        cluster = self.kmeans.fit_predict(scaled_features)[0]
        
        # 根据聚类结果调整策略
        strategy_map = {
            0: {"delay": 2.0, "concurrency": 3, "rate_limit": 2},  # 保守策略
            1: {"delay": 1.0, "concurrency": 5, "rate_limit": 5},  # 平衡策略
            2: {"delay": 0.5, "concurrency": 8, "rate_limit": 8}   # 激进策略
        }
        
        return strategy_map[cluster]
    
    async def ai_adaptive_request(self, url: str, **kwargs):
        """AI自适应请求方法"""
        start_time = time.time()
        
        try:
            async with ClientSession(timeout=self.timeout, connector=self.connector) as session:
                response = await session.get(url, **kwargs)
                response_time = time.time() - start_time
                
                # 记录性能数据
                success = response.status == 200
                success_rate = 1.0 if success else 0.0
                
                # AI优化策略
                if self.enable_ai_optimization:
                    strategy = await self.optimize_crawling_strategy(url, response_time, success_rate)
                    if strategy:
                        # 根据AI建议调整后续请求参数
                        await asyncio.sleep(strategy["delay"])
                
                return response
        except Exception as e:
            response_time = time.time() - start_time
            if self.enable_ai_optimization:
                await self.optimize_crawling_strategy(url, response_time, 0.0)
            raise e
```

### 3.2 智能代理池管理

```python
class IntelligentProxyManager:
    """
    智能代理池管理器
    基于AI的代理选择和质量评估
    """
    
    def __init__(self):
        self.proxy_quality_scores = {}  # 代理质量评分
        self.usage_statistics = {}      # 使用统计
        self.performance_model = None   # 性能预测模型
    
    def evaluate_proxy_quality(self, proxy_info: dict) -> float:
        """
        评估代理质量
        返回0-1之间的质量分数
        """
        # 综合考虑多个指标
        speed_score = self._evaluate_speed(proxy_info)
        stability_score = self._evaluate_stability(proxy_info)
        anonymity_score = self._evaluate_anonymity(proxy_info)
        
        # 加权计算最终分数
        final_score = (speed_score * 0.4 + 
                      stability_score * 0.4 + 
                      anonymity_score * 0.2)
        
        return min(1.0, max(0.0, final_score))
    
    def select_best_proxy(self, target_domain: str) -> str:
        """
        AI选择最佳代理
        """
        # 根据目标域名和历史性能选择最佳代理
        available_proxies = self.get_available_proxies()
        
        # 使用AI模型预测每个代理在目标域名上的表现
        best_proxy = self._predict_best_proxy(available_proxies, target_domain)
        return best_proxy
```

## 4. 预测分析模块AI融合

### 4.1 智能预测服务

在`backend/services/prediction_service.py`中实现：

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam

class AIPredictionService:
    """AI增强型预测服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ml_models = {}
        self.nn_model = None
        self.feature_columns = []
        self.is_trained = False
        self.performance_tracker = PerformanceTracker()
    
    def prepare_match_features(self, match_id: int) -> Dict[str, Any]:
        """准备比赛特征数据"""
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            return {}
        
        # 获取历史数据
        home_team_id = match.home_team_id
        away_team_id = match.away_team_id
        league_id = match.league_id
        
        # 计算双方历史数据
        home_historical = self.calculate_team_historical_data(home_team_id, league_id)
        away_historical = self.calculate_team_historical_data(away_team_id, league_id)
        
        # 计算两队历史交锋
        head_to_head = self.calculate_head_to_head_data(home_team_id, away_team_id)
        
        # 组合特征
        features = {
            # 比赛基本信息
            'match_date': match.match_date.timestamp() if match.match_date else 0,
            'league_id': league_id or 0,
            
            # 主队特征
            'home_draw_rate': home_historical['draw_rate'],
            'home_form_score': home_historical['form_score'],
            'home_avg_goals_scored': home_historical['avg_goals_scored'],
            'home_avg_goals_conceded': home_historical['avg_goals_conceded'],
            'home_recent_draws': home_historical['recent_draws'],
            
            # 客队特征
            'away_draw_rate': away_historical['draw_rate'],
            'away_form_score': away_historical['form_score'],
            'away_avg_goals_scored': away_historical['avg_goals_scored'],
            'away_avg_goals_conceded': away_historical['avg_goals_conceded'],
            'away_recent_draws': away_historical['recent_draws'],
            
            # 历史交锋
            'h2h_draw_rate': head_to_head['draw_rate'],
            'h2h_matches_count': head_to_head['matches_count'],
            
            # 赔率信息（如果有）
            'home_odds': match.odds_home if hasattr(match, 'odds_home') else 2.5,
            'draw_odds': match.odds_draw if hasattr(match, 'odds_draw') else 3.2,
            'away_odds': match.odds_away if hasattr(match, 'odds_away') else 2.8,
        }
        
        return features
    
    def train_ml_models(self):
        """训练机器学习模型"""
        try:
            # 获取所有已完成的比赛数据
            matches = self.db.query(Match).filter(
                and_(
                    Match.status == MatchStatusEnum.FINISHED,
                    Match.home_score.isnot(None),
                    Match.away_score.isnot(None)
                )
            ).all()
            
            if len(matches) < 100:
                logger.warning("训练数据不足，跳过模型训练")
                return False
            
            # 准备特征和标签
            features = []
            labels = []
            
            for match in matches:
                feature_dict = self.prepare_match_features(match.id)
                if feature_dict:
                    features.append(list(feature_dict.values()))
                    # 标签：比赛结果（主胜=0，平=1，客胜=2）
                    if match.home_score > match.away_score:
                        result = 0
                    elif match.home_score == match.away_score:
                        result = 1
                    else:
                        result = 2
                    labels.append(result)
            
            if not features:
                logger.warning("无法提取特征，跳过模型训练")
                return False
            
            # 转换为DataFrame便于处理
            df = pd.DataFrame(features)
            df.columns = [f'feature_{i}' for i in range(len(df.columns))]
            y = np.array(labels)
            
            # 分割训练测试集
            X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=42)
            
            # 训练随机森林模型
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(X_train, y_train)
            rf_pred = rf_model.predict(X_test)
            rf_accuracy = accuracy_score(y_test, rf_pred)
            
            # 训练梯度提升模型
            gb_model = GradientBoostingRegressor(random_state=42)
            gb_model.fit(X_train, y_train)
            gb_pred = gb_model.predict(X_test)
            gb_mse = mean_squared_error(y_test, gb_pred)
            
            # 保存模型
            self.ml_models = {
                'random_forest': rf_model,
                'gradient_boosting': gb_model,
                'feature_columns': list(df.columns),
                'accuracy_scores': {
                    'random_forest': rf_accuracy,
                    'gradient_boosting': 1 - gb_mse
                }
            }
            
            logger.info(f"模型训练完成 - RF准确率: {rf_accuracy:.3f}")
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"模型训练失败: {e}")
            return False
    
    def predict_match_outcome_with_ml(self, match_id: int) -> Dict[str, Any]:
        """使用机器学习模型预测比赛结果"""
        if not self.is_trained:
            logger.warning("模型尚未训练，使用统计学方法")
            return self.calculate_draw_probability_statistical(match_id)
        
        try:
            # 获取比赛特征
            features = self.prepare_match_features(match_id)
            if not features:
                return self.calculate_draw_probability_statistical(match_id)
            
            # 准备特征向量
            feature_vector = np.array([list(features.values())])
            
            # 使用多个模型预测
            rf_pred_proba = self.ml_models['random_forest'].predict_proba(feature_vector)[0]
            rf_pred = self.ml_models['random_forest'].predict(feature_vector)[0]
            
            # 返回预测结果
            result = {
                'probabilities': {
                    'home_win': float(rf_pred_proba[0]),
                    'draw': float(rf_pred_proba[1]),
                    'away_win': float(rf_pred_proba[2])
                },
                'predicted_outcome': rf_pred,
                'confidence': float(max(rf_pred_proba)),
                'method_used': 'ml_ensemble',
                'model_performance': self.ml_models['accuracy_scores']
            }
            
            # 更新性能跟踪
            self.performance_tracker.log_prediction(result)
            
            return result
            
        except Exception as e:
            logger.error(f"ML预测失败，回退到统计方法: {e}")
            return self.calculate_draw_probability_statistical(match_id)
```

### 4.2 模型性能监控

```python
class PerformanceTracker:
    """
    模型性能跟踪器
    用于监控和优化AI模型表现
    """
    
    def __init__(self):
        self.prediction_history = []
        self.performance_metrics = {}
    
    def log_prediction(self, prediction_result: Dict[str, Any]):
        """记录预测结果"""
        self.prediction_history.append({
            'timestamp': datetime.now(),
            'prediction': prediction_result,
            'accuracy': None  # 等待实际结果确认
        })
    
    def update_accuracy(self, prediction_id: int, actual_result: int):
        """更新预测准确性"""
        if prediction_id < len(self.prediction_history):
            self.prediction_history[prediction_id]['accuracy'] = (
                self.prediction_history[prediction_id]['prediction']['predicted_outcome'] == actual_result
            )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        accurate_predictions = [p for p in self.prediction_history if p['accuracy'] is not None]
        total_predictions = len(accurate_predictions)
        
        if total_predictions == 0:
            return {'accuracy': 0.0, 'total_predictions': 0}
        
        correct_predictions = sum(1 for p in accurate_predictions if p['accuracy'])
        accuracy = correct_predictions / total_predictions
        
        return {
            'accuracy': accuracy,
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions,
            'recent_performance': self._get_recent_performance()
        }
    
    def _get_recent_performance(self) -> Dict[str, float]:
        """获取近期性能"""
        recent_predictions = [p for p in self.prediction_history 
                            if (datetime.now() - p['timestamp']).days <= 7]
        recent_accurate = [p for p in recent_predictions if p['accuracy'] is not None]
        
        if not recent_accurate:
            return {'accuracy': 0.0, 'count': 0}
        
        correct = sum(1 for p in recent_accurate if p['accuracy'])
        return {
            'accuracy': correct / len(recent_accurate),
            'count': len(recent_accurate)
        }
```

## 5. 智能情报分析模块

### 5.1 情报内容分析

在`backend/services/intelligence_service.py`中增强：

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import jieba
import re

class AIIntelligenceService:
    """AI增强型数据情报服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.text_pipeline = self._initialize_text_analyzer()
    
    def _initialize_text_analyzer(self):
        """初始化文本分析器"""
        try:
            # 创建文本分类管道
            pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(tokenizer=self._chinese_tokenize, ngram_range=(1, 2))),
                ('classifier', MultinomialNB())
            ])
            return pipeline
        except Exception as e:
            logger.error(f"文本分析器初始化失败: {e}")
            return None
    
    def _chinese_tokenize(self, text):
        """中文分词"""
        # 清理文本
        cleaned_text = re.sub(r'[^\w\s]', '', text)
        tokens = jieba.lcut(cleaned_text)
        # 过滤短词
        return [token for token in tokens if len(token) > 1]
    
    def classify_intelligence_content(self, content: str, title: str = "") -> str:
        """AI自动分类情报内容"""
        if not content:
            return "other"
        
        # 结合标题和内容进行分析
        full_text = f"{title} {content}".strip()
        
        # 基于关键词的初步分类
        keywords = {
            "injury": ["伤", "受伤", "缺阵", "伤病", "不能出场", "受伤病困扰"],
            "suspension": ["停赛", "红牌停赛", "累计黄牌", "禁赛"],
            "lineup": ["首发", "阵容", "阵型", "排兵布阵", "预计阵容"],
            "odds": ["赔率", "指数", "让球", "水位", "博彩"],
            "weather": ["天气", "雨", "雪", "场地", "草皮"],
            "motivation": ["战意", "争夺", "保级", "争冠", "欧战资格"],
            "history": ["交锋", "历史战绩", "往绩", "对战"],
            "form": ["状态", "走势", "近况", "近期表现"]
        }
        
        # 统计各类型关键词出现次数
        scores = {}
        for category, words in keywords.items():
            score = sum(1 for word in words if word in full_text)
            scores[category] = score
        
        # 返回得分最高的类别
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return "other"
    
    def analyze_intelligence_impact(self, intelligence_item: Intelligence) -> Dict[str, Any]:
        """分析情报对比赛的影响程度"""
        impact_score = 0.0
        factors = {}
        
        # 分析情报类型影响
        type_impacts = {
            "injury": 0.8,      # 伤病影响较大
            "suspension": 0.7,  # 停赛影响较大
            "lineup": 0.3,      # 阵容影响中等
            "odds": 0.4,        # 赔率影响中等
            "weather": 0.2,     # 天气影响较小
            "motivation": 0.6,  # 战意影响较大
            "history": 0.1,     # 历史交锋影响较小
            "form": 0.5         # 状态影响中等
        }
        
        type_factor = type_impacts.get(intelligence_item.type, 0.1)
        impact_score += type_factor
        factors['type_factor'] = type_factor
        
        # 分析情报置信度影响
        confidence_factors = {
            "confirmed": 1.0,
            "very_high": 0.9,
            "high": 0.7,
            "medium": 0.5,
            "low": 0.3,
            "very_low": 0.1
        }
        
        confidence_factor = confidence_factors.get(intelligence_item.confidence.value, 0.5)
        impact_score *= confidence_factor
        factors['confidence_factor'] = confidence_factor
        
        # 分析时效性影响
        if intelligence_item.match_id and intelligence_item.created_at:
            from ..models.match import Match
            match = self.db.query(Match).filter(Match.id == intelligence_item.match_id).first()
            if match and match.match_date:
                hours_before_match = (match.match_date - intelligence_item.created_at).total_seconds() / 3600
                # 距离比赛时间越近，影响越大（但不会超过24小时）
                time_factor = min(max(0.5, 1.0 - hours_before_match / 72), 1.5)
                impact_score *= time_factor
                factors['time_factor'] = time_factor
        
        # 最终影响分数限制在0-1之间
        final_impact = max(0.0, min(1.0, impact_score))
        
        return {
            "impact_score": final_impact,
            "factors": factors,
            "significance_level": self._get_significance_level(final_impact)
        }
    
    def _get_significance_level(self, impact_score: float) -> str:
        """获取显著性级别"""
        if impact_score >= 0.8:
            return "critical"
        elif impact_score >= 0.6:
            return "high"
        elif impact_score >= 0.4:
            return "medium"
        elif impact_score >= 0.2:
            return "low"
        else:
            return "minimal"
    
    def generate_intelligence_insights(self, match_id: int) -> Dict[str, Any]:
        """为指定比赛生成AI驱动的情报洞察"""
        # 获取相关情报
        insights = self.db.query(Intelligence).filter(
            Intelligence.match_id == match_id
        ).all()
        
        if not insights:
            return {
                "has_intelligence": False,
                "summary": "暂无相关情报信息",
                "key_points": [],
                "impact_assessment": "neutral"
            }
        
        # 分析每条情报的影响
        analyzed_insights = []
        total_impact = 0.0
        
        for insight in insights:
            analysis = self.analyze_intelligence_impact(insight)
            analyzed_insights.append({
                "id": insight.id,
                "type": insight.type,
                "content": insight.content,
                "impact_score": analysis["impact_score"],
                "significance_level": analysis["significance_level"],
                "factors": analysis["factors"]
            })
            total_impact += analysis["impact_score"]
        
        # 生成综合评估
        avg_impact = total_impact / len(analyzed_insights) if analyzed_insights else 0.0
        
        # 确定影响倾向
        impact_direction = "neutral"
        if avg_impact > 0.6:
            impact_direction = "high_impact"
        elif avg_impact > 0.3:
            impact_direction = "moderate_impact"
        
        # 提取关键要点
        key_points = []
        high_impact_items = [item for item in analyzed_insights if item["impact_score"] > 0.5]
        
        for item in sorted(high_impact_items, key=lambda x: x["impact_score"], reverse=True)[:3]:
            key_points.append({
                "type": item["type"],
                "summary": item["content"][:100] + ("..." if len(item["content"]) > 100 else ""),
                "impact": item["significance_level"]
            })
        
        return {
            "has_intelligence": True,
            "summary": f"共发现{len(analyzed_insights)}条相关情报，平均影响分数{avg_impact:.2f}",
            "key_points": key_points,
            "impact_assessment": impact_direction,
            "detailed_analysis": analyzed_insights
        }
```

## 6. 对冲策略AI融合

### 6.1 AI增强的对冲服务

在`backend/services/hedging_service.py`中实现：

```python
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta

class AIEnhancedHedgingService:
    """AI增强的对冲服务"""
    
    def __init__(self, db: Session):
        self.db = db
        try:
            self.config = get_default_hedging_config(db)
        except Exception:
            class MockConfig:
                min_profit_rate = 0.02
                commission_rate = 0.8
                cost_factor = 0.2
            self.config = MockConfig()
        
        # AI组件初始化
        self.risk_analyzer = IsolationForest(contamination=0.1, random_state=42)
        self.profit_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_risk_model_trained = False
        self.is_profit_model_trained = False
    
    def extract_risk_features(self, match1_data, match2_data, hedge_calculation) -> np.ndarray:
        """提取风险评估特征"""
        features = [
            # 基础对冲参数
            hedge_calculation['investment'],
            hedge_calculation['revenue'],
            hedge_calculation['profit'],
            hedge_calculation['profit_rate'],
            hedge_calculation['is_profitable'],
            
            # 赔率相关特征
            match1_data.get('sp_value', 2.5),
            match1_data.get('european_odd', 2.5),
            match2_data.get('sp_value', 2.5),
            match2_data.get('european_odd', 2.5),
            
            # 时间特征
            (match2_data.get('start_time') - match1_data.get('start_time')).total_seconds() / 3600,
            
            # 组合赔率特征
            match1_data.get('sp_value', 2.5) * match2_data.get('sp_value', 2.5),
            match1_data.get('european_odd', 2.5) * match2_data.get('european_odd', 2.5),
        ]
        
        return np.array(features).reshape(1, -1)

    def assess_hedge_risk(self, match1_data, match2_data, hedge_calculation) -> Dict[str, float]:
        """AI风险评估"""
        if not self.is_risk_model_trained:
            return self._rule_based_risk_assessment(hedge_calculation)
        
        try:
            features = self.extract_risk_features(match1_data, match2_data, hedge_calculation)
            features_scaled = self.scaler.transform(features)
            
            # 预测是否为异常（高风险）情况
            anomaly_score = self.risk_analyzer.decision_function(features_scaled)[0]
            is_anomaly = self.risk_analyzer.predict(features_scaled)[0] == -1
            
            # 风险评分（0-1，越高风险越大）
            risk_score = max(0, min(1, (anomaly_score + 0.5) / 1.0))
            
            return {
                "risk_score": risk_score,
                "is_anomaly": bool(is_anomaly),
                "anomaly_score": float(anomaly_score),
                "risk_level": self._get_risk_level(risk_score)
            }
        except Exception as e:
            logger.error(f"AI风险评估失败: {e}")
            return self._rule_based_risk_assessment(hedge_calculation)

    def predict_profit_with_ai(self, match1_data, match2_data, hedge_calculation) -> Dict[str, float]:
        """AI利润预测"""
        if not self.is_profit_model_trained:
            return {
                "predicted_profit": hedge_calculation.get("profit", 0),
                "confidence": 0.5,
                "variance": 0.1
            }
        
        try:
            features = self.extract_profit_features(match1_data, match2_data, hedge_calculation)
            predicted_profit = self.profit_predictor.predict(features)[0]
            
            # 计算预测置信度
            confidence = 0.8  # 假设模型训练良好
            
            return {
                "predicted_profit": float(predicted_profit),
                "confidence": confidence,
                "original_calculation": hedge_calculation.get("profit", 0)
            }
        except Exception as e:
            logger.error(f"AI利润预测失败: {e}")
            return {
                "predicted_profit": hedge_calculation.get("profit", 0),
                "confidence": 0.3,
                "original_calculation": hedge_calculation.get("profit", 0)
            }
    
    def extract_profit_features(self, match1_data, match2_data, hedge_calculation) -> np.ndarray:
        """提取利润预测特征"""
        features = [
            # 基础参数
            match1_data.get('sp_value', 2.5),
            match1_data.get('european_odd', 2.5),
            match2_data.get('sp_value', 2.5),
            match2_data.get('european_odd', 2.5),
            (match2_data.get('start_time') - match1_data.get('start_time')).total_seconds() / 3600,
            
            # 组合参数
            match1_data.get('sp_value', 2.5) * match2_data.get('sp_value', 2.5),
            match1_data.get('european_odd', 2.5) * match2_data.get('european_odd', 2.5),
            
            # 历史成功率特征
            getattr(self.config, 'historical_success_rate', 0.75),
            getattr(self.config, 'volatility_factor', 0.1),
        ]
        
        return np.array(features).reshape(1, -1)
```

### 6.2 AI驱动的投资组合优化

```python
class AIHedgingOptimizer:
    """
    AI驱动的对冲策略优化器
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.investment_allocator = RandomForestRegressor(n_estimators=100, random_state=42)
        self.timing_optimizer = GradientBoostingRegressor(n_estimators=50, random_state=42)
        self.portfolio_balancer = RandomForestRegressor(n_estimators=80, random_state=42)
        
        self.is_investment_trained = False
        self.is_timing_trained = False
        self.is_portfolio_trained = False
    
    def suggest_investment_amount(self, opportunity: Dict[str, Any], available_capital: float) -> Dict[str, float]:
        """AI建议投资金额"""
        if not self.is_investment_trained:
            return self._rule_based_investment_suggestion(opportunity, available_capital)
        
        try:
            features = self.extract_investment_features(opportunity)
            suggested_ratio = self.investment_allocator.predict(features)[0]
            
            # 确保建议比例在合理范围内
            suggested_ratio = max(0.01, min(0.2, suggested_ratio))
            
            suggested_amount = min(available_capital * suggested_ratio, 
                                 opportunity.get('investment_amount', available_capital * 0.1))
            
            return {
                "suggested_amount": suggested_amount,
                "allocation_ratio": suggested_ratio,
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"AI投资金额建议失败: {e}")
            return self._rule_based_investment_suggestion(opportunity, available_capital)
    
    def optimize_portfolio_allocation(self, opportunities: List[Dict[str, Any]], total_capital: float) -> Dict[str, Any]:
        """AI优化投资组合分配"""
        if not self.is_portfolio_trained:
            return self._rule_based_portfolio_optimization(opportunities, total_capital)
        
        try:
            features = self.extract_portfolio_features(opportunities)
            diversification_score = self.portfolio_balancer.predict(features)[0]
            
            # 基于分散化得分调整分配策略
            allocation_strategy = "diversified" if diversification_score > 0.5 else "concentrated"
            
            # 按质量和风险排序机会
            sorted_opportunities = sorted(opportunities, 
                                        key=lambda x: x.get('profit_rate', 0) / (1 + x.get('risk_score', 0.5)), 
                                        reverse=True)
            
            allocations = []
            remaining_capital = total_capital
            
            for i, opp in enumerate(sorted_opportunities):
                if remaining_capital <= 0:
                    break
                
                suggested_allocation = self.suggest_investment_amount(opp, remaining_capital)
                
                allocation = {
                    "opportunity_id": opp.get('match1_id', 'unknown') + '-' + str(opp.get('match2_id', 'unknown')),
                    "allocated_amount": min(suggested_allocation["suggested_amount"], remaining_capital),
                    "opportunity": opp
                }
                
                allocations.append(allocation)
                remaining_capital -= allocation["allocated_amount"]
            
            return {
                "strategy": allocation_strategy,
                "total_allocated": total_capital - remaining_capital,
                "allocations": allocations,
                "remaining_capital": remaining_capital,
                "confidence": 0.75
            }
        except Exception as e:
            logger.error(f"AI投资组合优化失败: {e}")
            return self._rule_based_portfolio_optimization(opportunities, total_capital)
```

## 7. 模型训练与部署

### 7.1 自动化训练管道

```python
class AutoTrainingPipeline:
    """
    自动化模型训练管道
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.training_data_service = HedgingTrainingDataService(db)
        self.scheduler = BackgroundScheduler()
    
    def setup_automatic_training(self):
        """设置自动训练任务"""
        # 每周训练一次预测模型
        self.scheduler.add_job(
            self.train_prediction_models,
            'cron',
            day_of_week='mon',
            hour=2,
            id='weekly_prediction_training'
        )
        
        # 每日训练风险评估模型
        self.scheduler.add_job(
            self.train_risk_models,
            'cron',
            hour=3,
            id='daily_risk_training'
        )
        
        self.scheduler.start()
    
    def train_prediction_models(self):
        """训练预测模型"""
        try:
            # 收集最新数据
            training_data = self.training_data_service.collect_historical_data(days_back=90)
            
            # 重新训练预测服务
            prediction_service = AIPredictionService(self.db)
            success = prediction_service.train_ml_models()
            
            if success:
                # 保存训练好的模型
                model_path = f"models/prediction_model_{datetime.now().strftime('%Y%m%d')}.joblib"
                prediction_service.save_model(model_path)
                
                # 更新活跃模型
                self._update_active_model('prediction', model_path)
                
                logger.info("预测模型训练完成并已部署")
            else:
                logger.warning("预测模型训练失败")
                
        except Exception as e:
            logger.error(f"预测模型训练过程出错: {e}")
    
    def train_risk_models(self):
        """训练风险评估模型"""
        try:
            # 收集对冲机会数据
            hedging_data = self.training_data_service.collect_historical_data(days_back=30)
            
            # 训练风险模型
            hedging_service = AIEnhancedHedgingService(self.db)
            success = hedging_service.train_risk_model(hedging_data)
            
            if success:
                model_path = f"models/risk_model_{datetime.now().strftime('%Y%m%d')}.joblib"
                hedging_service.save_risk_model(model_path)
                self._update_active_model('risk', model_path)
                
                logger.info("风险模型训练完成并已部署")
            else:
                logger.warning("风险模型训练失败")
                
        except Exception as e:
            logger.error(f"风险模型训练过程出错: {e}")
    
    def _update_active_model(self, model_type: str, model_path: str):
        """更新活跃模型"""
        # 在数据库中记录最新模型路径
        from ..models.system_config import SystemConfig
        config = self.db.query(SystemConfig).filter(
            SystemConfig.key == f'{model_type}_model_path'
        ).first()
        
        if config:
            config.value = model_path
            config.updated_at = datetime.utcnow()
        else:
            config = SystemConfig(
                key=f'{model_type}_model_path',
                value=model_path,
                description=f'{model_type}模型路径'
            )
            self.db.add(config)
        
        self.db.commit()
```

### 7.2 模型版本管理

```python
class ModelVersionManager:
    """
    模型版本管理器
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_model_version(self, model_name: str, model_path: str, 
                             performance_metrics: Dict[str, float], 
                             description: str = "") -> int:
        """注册新模型版本"""
        from ..models.model_version import ModelVersion
        
        model_version = ModelVersion(
            model_name=model_name,
            version_number=self._get_next_version(model_name),
            model_path=model_path,
            performance_metrics=performance_metrics,
            description=description,
            is_active=False,
            trained_at=datetime.utcnow()
        )
        
        self.db.add(model_version)
        self.db.commit()
        
        return model_version.id
    
    def activate_model_version(self, version_id: int):
        """激活模型版本"""
        # 先停用同名模型的其他版本
        from ..models.model_version import ModelVersion
        self.db.query(ModelVersion).filter(
            ModelVersion.model_name == (
                self.db.query(ModelVersion).filter(ModelVersion.id == version_id).first().model_name
            ),
            ModelVersion.is_active == True
        ).update({ModelVersion.is_active: False})
        
        # 激活指定版本
        model_version = self.db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
        model_version.is_active = True
        model_version.activated_at = datetime.utcnow()
        
        self.db.commit()
    
    def _get_next_version(self, model_name: str) -> str:
        """获取下一个版本号"""
        from ..models.model_version import ModelVersion
        latest_version = self.db.query(ModelVersion).filter(
            ModelVersion.model_name == model_name
        ).order_by(ModelVersion.version_number.desc()).first()
        
        if latest_version:
            # 假设版本号格式为 v1.0.0
            parts = latest_version.version_number.split('.')
            parts[-1] = str(int(parts[-1]) + 1)
            return '.'.join(parts)
        else:
            return "1.0.0"
```

## 8. API接口设计

### 8.1 预测服务API

```python
@router.get("/ai/predictions/{match_id}")
def get_ai_prediction(
    match_id: int,
    db: Session = Depends(get_db)
):
    """获取AI预测结果"""
    try:
        prediction_service = AIPredictionService(db)
        result = prediction_service.predict_match_outcome_with_ml(match_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI预测失败: {str(e)}")

@router.get("/ai/predictions/{match_id}/insights")
def get_prediction_insights(
    match_id: int,
    db: Session = Depends(get_db)
):
    """获取预测洞察分析"""
    try:
        prediction_service = AIPredictionService(db)
        insights = prediction_service.generate_prediction_insights(match_id)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预测洞察失败: {str(e)}")
```

### 8.2 对冲服务API

```python
@router.post("/ai/hedging/optimize-investment")
def ai_optimize_investment(
    opportunity_id: str,
    available_capital: float,
    db: Session = Depends(get_db)
):
    """AI优化单个对冲机会的投资金额"""
    try:
        ai_optimizer = AIHedgingOptimizer(db)
        # 实现具体的优化逻辑
        suggestion = ai_optimizer.suggest_investment_amount(
            opportunity_id, available_capital
        )
        return suggestion
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI投资优化失败: {str(e)}")

@router.post("/ai/hedging/optimize-portfolio")
def ai_optimize_portfolio(
    date: str,
    total_capital: float,
    db: Session = Depends(get_db)
):
    """AI优化整个投资组合的分配"""
    try:
        # 获取当天所有对冲机会
        hedging_service = AIEnhancedHedgingService(db)
        opportunities_result = hedging_service.find_parlay_combinations(date)
        
        ai_optimizer = AIHedgingOptimizer(db)
        optimization_result = ai_optimizer.optimize_portfolio_allocation(
            opportunities_result.opportunities, 
            total_capital
        )
        
        return optimization_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI投资组合优化失败: {str(e)}")
```

## 9. 监控与运维

### 9.1 性能监控

```python
class AIPerformanceMonitor:
    """
    AI性能监控器
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
    
    def monitor_prediction_accuracy(self):
        """监控预测准确性"""
        tracker = PerformanceTracker()
        report = tracker.get_performance_report()
        
        # 如果准确率低于阈值，发送警报
        if report['accuracy'] < 0.65:  # 65%阈值
            self.alert_manager.send_alert(
                "prediction_accuracy_low",
                f"预测准确率下降至 {report['accuracy']:.2%}",
                severity="warning"
            )
    
    def monitor_model_drift(self):
        """监控模型漂移"""
        # 实现模型漂移检测逻辑
        pass
    
    def collect_system_metrics(self):
        """收集系统指标"""
        metrics = {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'active_connections': len(active_connections),
            'request_rate': self.get_request_rate(),
            'error_rate': self.get_error_rate()
        }
        
        self.metrics_collector.record_metrics(metrics)
```

### 9.2 模型重训练触发

```python
class ModelRetrainingTrigger:
    """
    模型重训练触发器
    基于性能指标自动触发重训练
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.performance_thresholds = {
            'prediction_accuracy': 0.65,
            'risk_precision': 0.80,
            'profit_variance': 0.15
        }
    
    def check_retraining_conditions(self):
        """检查是否需要重训练"""
        # 检查各个模型的性能指标
        performance_data = self._collect_performance_data()
        
        retraining_needed = {}
        
        for model_type, threshold in self.performance_thresholds.items():
            current_value = performance_data.get(model_type, 0)
            
            if current_value < threshold:
                retraining_needed[model_type] = {
                    'current': current_value,
                    'threshold': threshold,
                    'reason': 'Performance below threshold'
                }
        
        # 检查数据新鲜度
        last_training = self._get_last_training_time()
        if datetime.utcnow() - last_training > timedelta(days=30):
            retraining_needed['data_freshness'] = {
                'reason': 'Models too old, need retraining'
            }
        
        return retraining_needed
    
    def trigger_retraining(self, model_types: List[str]):
        """触发模型重训练"""
        for model_type in model_types:
            if model_type == 'prediction':
                self._retrain_prediction_model()
            elif model_type == 'risk':
                self._retrain_risk_model()
            # 添加其他模型类型的重训练逻辑
    
    def _collect_performance_data(self) -> Dict[str, float]:
        """收集性能数据"""
        # 实现性能数据收集逻辑
        return {}
```

## 10. 部署与配置

### 10.1 Docker配置

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 安装机器学习相关依赖
RUN pip install --no-cache-dir scikit-learn tensorflow pandas numpy

# 复制应用代码
COPY . .

# 创建模型目录
RUN mkdir -p models

# 设置权限
RUN chmod +x /app/scripts/start-backend.sh

EXPOSE 8000

CMD ["sh", "-c", "/app/scripts/start-backend.sh"]
```

### 10.2 环境配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - DATABASE_URL=postgresql://user:pass@db:5432/sport_lottery
      - REDIS_URL=redis://redis:6379/0
      - ENABLE_AI_OPTIMIZATION=true
      - AI_MODEL_PATH=/app/models
      - ML_TRAINING_ENABLED=true
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
        reservations:
          memory: 2G
          cpus: '1'

  ml-training-worker:
    build: .
    command: python -m backend.tasks.ml_training_worker
    environment:
      - PYTHONPATH=/app
      - DATABASE_URL=postgresql://user:pass@db:5432/sport_lottery
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./models:/app/models
    depends_on:
      - db
      - redis
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 4G
          cpus: '2'
```

## 11. 测试策略

### 11.1 单元测试

```python
# tests/test_ai_prediction_service.py
import pytest
from unittest.mock import Mock, patch
from backend.services.prediction_service import AIPredictionService

class TestAIPredictionService:
    
    def test_prepare_match_features(self, db_session):
        """测试比赛特征准备"""
        service = AIPredictionService(db_session)
        
        # 模拟比赛数据
        match_id = 1
        features = service.prepare_match_features(match_id)
        
        assert isinstance(features, dict)
        assert 'home_draw_rate' in features
        assert 'away_form_score' in features
    
    @patch('backend.services.prediction_service.RandomForestClassifier')
    def test_predict_with_ml_model(self, mock_rf_class, db_session):
        """测试ML模型预测"""
        # 模拟模型
        mock_model = Mock()
        mock_model.predict_proba.return_value = [[0.3, 0.4, 0.3]]
        mock_model.predict.return_value = [1]
        
        service = AIPredictionService(db_session)
        service.ml_models = {'random_forest': mock_model}
        service.is_trained = True
        
        result = service.predict_match_outcome_with_ml(1)
        
        assert 'probabilities' in result
        assert 'confidence' in result
        assert result['confidence'] > 0
```

### 11.2 集成测试

```python
# tests/test_ai_hedging_integration.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_ai_hedging_optimization(client):
    """测试AI对冲优化API"""
    response = client.post(
        "/api/v1/ai/hedging/optimize-investment",
        params={
            "opportunity_id": "test_opp_1",
            "available_capital": 10000.0
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "suggested_amount" in data
    assert "confidence" in data
    assert data["confidence"] >= 0 and data["confidence"] <= 1

def test_ai_prediction_endpoint(client):
    """测试AI预测API"""
    response = client.get("/api/v1/ai/predictions/1")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "probabilities" in data
    assert "confidence" in data
    assert "home_win" in data["probabilities"]
```

## 12. 总结

本技术开发文档详细阐述了将AI原生架构融入体育彩票业务的完整方案，包括：

1. **数据采集层**：智能爬虫和代理管理
2. **预测分析层**：机器学习驱动的预测模型
3. **情报分析层**：NLP驱动的情报理解和分类
4. **对冲策略层**：AI优化的投资组合管理

通过实施这套AI原生架构，系统将具备更高的智能化水平、更强的自适应能力和更好的决策效率，从而在竞争激烈的体育彩票市场中获得显著优势。