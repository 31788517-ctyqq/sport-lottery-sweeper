# 体育彩票业务综合AI原生架构方案

## 1. 项目概述

### 1.1 项目背景
本项目旨在将AI原生架构理念深度融合到体育彩票业务系统中，通过人工智能技术和大型语言模型（LLM）技术，全面提升数据采集、预测分析、对冲策略等核心业务模块的智能化水平，从而提高业务效率和盈利能力。

### 1.2 目标架构
- **智能数据采集层**：AI驱动的多源数据采集与反爬虫对抗
- **智能预测分析层**：机器学习驱动的比赛结果预测
- **智能情报分析层**：NLP驱动的情报分析
- **智能对冲策略层**：AI优化的对冲机会识别与资源配置
- **LLM服务层**：集成主流大语言模型，提供高级推理和对话能力

## 2. 系统架构设计

### 2.1 整体架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面层     │    │   API网关层     │    │   业务逻辑层     │
│  (Vue3 + TS)   │◄──►│  (FastAPI)     │◄──►│   AI服务层      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   数据存储层     │    │   任务调度层     │    │   LLM服务层     │
│ (PostgreSQL/    │◄──►│  (Celery/RQ)   │◄──►│  (OpenAI API/   │
│   SQLite)      │    │                 │    │   Gemini API/   │
└─────────────────┘    └─────────────────┘    │   Qwen API等)   │
                                              └─────────────────┘
```

### 2.2 AI原生架构特点
- **自适应学习**：模型根据市场变化持续学习优化
- **智能决策**：基于数据驱动的自动化决策机制
- **风险控制**：AI驱动的风险评估与控制体系
- **资源优化**：智能化的计算与网络资源分配
- **自然交互**：LLM驱动的智能对话与内容生成能力

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

## 7. LLM集成架构

### 7.1 LLM抽象服务层

创建`backend/services/llm_service.py`：

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import logging
import time
import openai
import google.generativeai as genai
from zhipuai import ZhipuAI
import requests

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """LLM供应商抽象基类"""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成响应"""
        pass
    
    @abstractmethod
    def get_embeddings(self, text: str) -> List[float]:
        """获取嵌入向量"""
        pass

class OpenAILLM(LLMProvider):
    """OpenAI GPT系列模型"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            return ""
    
    def get_embeddings(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embeddings调用失败: {e}")
            return []

class GeminiLLM(LLMProvider):
    """Google Gemini模型"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API调用失败: {e}")
            return ""
    
    def get_embeddings(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="semantic_similarity"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Gemini embeddings调用失败: {e}")
            return []

class QwenLLM(LLMProvider):
    """阿里云通义千问模型"""
    
    def __init__(self, api_key: str, model: str = "qwen-max"):
        self.api_key = api_key
        self.model = model
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "input": {
                    "prompt": prompt
                },
                "parameters": kwargs
            }
            
            response = requests.post(self.url, headers=headers, json=payload)
            result = response.json()
            
            if response.status_code == 200:
                return result['output']['text']
            else:
                logger.error(f"Qwen API调用失败: {result}")
                return ""
        except Exception as e:
            logger.error(f"Qwen API调用异常: {e}")
            return ""
    
    def get_embeddings(self, text: str) -> List[float]:
        # 通义千问Embedding API调用实现
        try:
            url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "text-embedding-v1",
                "input": {
                    "texts": [text]
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()
            
            if response.status_code == 200:
                return result['output']['embeddings'][0]['embedding']
            else:
                logger.error(f"Qwen embeddings调用失败: {result}")
                return []
        except Exception as e:
            logger.error(f"Qwen embeddings调用异常: {e}")
            return []

class DeepSeekLLM(LLMProvider):
    """DeepSeek模型"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            result = response.json()
            
            if response.status_code == 200:
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"DeepSeek API调用失败: {result}")
                return ""
        except Exception as e:
            logger.error(f"DeepSeek API调用异常: {e}")
            return ""
    
    def get_embeddings(self, text: str) -> List[float]:
        # DeepSeek目前可能不支持embeddings，返回空列表
        logger.warning("DeepSeek目前可能不支持embeddings功能")
        return []

class LLMService:
    """LLM服务统一接口"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self.request_cost = 0  # 跟踪API调用成本
    
    def register_provider(self, name: str, provider: LLMProvider):
        """注册LLM供应商"""
        self.providers[name] = provider
        if self.default_provider is None:
            self.default_provider = name
    
    def set_default_provider(self, name: str):
        """设置默认供应商"""
        if name in self.providers:
            self.default_provider = name
    
    def generate_response(
        self, 
        prompt: str, 
        provider: Optional[str] = None, 
        **kwargs
    ) -> str:
        """生成响应"""
        provider_name = provider or self.default_provider
        if provider_name not in self.providers:
            raise ValueError(f"未找到供应商: {provider_name}")
        
        start_time = time.time()
        response = self.providers[provider_name].generate_response(prompt, **kwargs)
        elapsed_time = time.time() - start_time
        
        # 记录成本和性能指标
        self._log_request(provider_name, len(prompt), len(response), elapsed_time)
        
        return response
    
    def get_embeddings(self, text: str, provider: Optional[str] = None) -> List[float]:
        """获取嵌入向量"""
        provider_name = provider or self.default_provider
        if provider_name not in self.providers:
            raise ValueError(f"未找到供应商: {provider_name}")
        
        return self.providers[provider_name].get_embeddings(text)
    
    def _log_request(self, provider: str, input_tokens: int, output_tokens: int, elapsed_time: float):
        """记录请求信息用于成本跟踪"""
        # 简化的成本计算（实际应根据各服务商定价模型调整）
        cost_estimate = (input_tokens + output_tokens) * 0.00001  # 示例计算
        self.request_cost += cost_estimate
        logger.info(f"LLM请求 - Provider: {provider}, "
                   f"Input: {input_tokens} tokens, Output: {output_tokens} tokens, "
                   f"Time: {elapsed_time:.2f}s, Cost estimate: ${cost_estimate:.4f}")
```

### 7.2 智能情报分析集成LLM能力

在`backend/services/intelligence_service.py`中增强LLM能力：

```python
from ..services.llm_service import LLMService

class AIIntelligenceService:
    """AI增强型数据情报服务类（集成LLM能力）"""
    
    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.text_pipeline = self._initialize_text_analyzer()
        self.llm_service = llm_service  # 集成LLM服务
    
    def analyze_intelligence_with_llm(self, intelligence_item: Intelligence) -> Dict[str, Any]:
        """使用LLM分析情报内容"""
        try:
            # 构造分析提示
            prompt = f"""
            请分析以下体育情报信息，评估其对相关比赛的影响程度：
            
            情报类型: {intelligence_item.type}
            情报内容: {intelligence_item.content}
            情报来源: {intelligence_item.source}
            情报置信度: {intelligence_item.confidence.value}
            
            请从以下几个方面进行分析：
            1. 对比赛结果的可能影响
            2. 影响的可信度评估
            3. 关键影响因素
            4. 潜在风险提示
            
            请以JSON格式返回分析结果，包含以下字段：
            - impact_level: 影响级别 (critical/high/medium/low/minimal)
            - impact_reasoning: 影响推理
            - credibility_score: 可信度分数 (0-1)
            - key_factors: 关键因素列表
            - risk_warnings: 风险提示列表
            - overall_assessment: 总体评估
            """
            
            # 调用LLM获取分析结果
            response_text = self.llm_service.generate_response(
                prompt, 
                provider="openai",  # 可根据需要选择不同的提供商
                temperature=0.3,
                max_tokens=800
            )
            
            # 解析LLM返回的JSON
            import json
            try:
                analysis_result = json.loads(response_text)
            except json.JSONDecodeError:
                # 如果LLM未返回有效JSON，使用备用分析
                analysis_result = {
                    "impact_level": "medium",
                    "impact_reasoning": "LLM分析结果解析失败，使用备用评估",
                    "credibility_score": 0.5,
                    "key_factors": ["解析失败"],
                    "risk_warnings": ["需人工核实"],
                    "overall_assessment": "需进一步验证"
                }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"LLM情报分析失败: {e}")
            # 返回基于规则的分析作为备选
            return self._rule_based_intelligence_analysis(intelligence_item)
    
    def summarize_intelligence_trends(self, days: int = 7) -> str:
        """使用LLM总结情报趋势"""
        try:
            # 获取最近几天的情报数据
            from datetime import datetime, timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            intelligence_list = self.db.query(Intelligence).filter(
                Intelligence.created_at >= start_date
            ).all()
            
            if not intelligence_list:
                return "近期无情报数据"
            
            # 构造总结提示
            intelligence_summary = "\n".join([
                f"- 类型: {item.type}, 内容: {item.content[:100]}..."
                for item in intelligence_list[:10]  # 限制数量避免提示太长
            ])
            
            prompt = f"""
            以下是过去{days}天的体育情报汇总，请分析其中的趋势和模式：
            
            {intelligence_summary}
            
            请提供以下方面的总结：
            1. 主要情报类型分布
            2. 显著趋势或模式
            3. 潜在影响较大的情报
            4. 需要关注的风险点
            5. 对未来比赛的预测意义
            
            请以简洁明了的方式呈现分析结果。
            """
            
            response = self.llm_service.generate_response(
                prompt,
                provider="gemini",
                temperature=0.4,
                max_tokens=600
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM情报趋势总结失败: {e}")
            return f"情报趋势总结失败: {e}"
    
    def _rule_based_intelligence_analysis(self, intelligence_item: Intelligence) -> Dict[str, Any]:
        """基于规则的情报分析（备选方案）"""
        # 使用之前的分析逻辑
        basic_analysis = self.analyze_intelligence_impact(intelligence_item)
        
        return {
            "impact_level": basic_analysis["significance_level"],
            "impact_reasoning": f"基于{intelligence_item.type}类型的规则分析",
            "credibility_score": 0.6,  # 默认可信度
            "key_factors": [intelligence_item.type],
            "risk_warnings": ["建议结合其他信息验证"],
            "overall_assessment": "需要进一步分析"
        }
```

### 7.3 智能预测解释器集成LLM

创建`backend/services/prediction_explainer.py`：

```python
from typing import Dict, Any
from sqlalchemy.orm import Session
from ..services.llm_service import LLMService

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
                provider="openai",
                temperature=0.5,
                max_tokens=500
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"预测解释生成失败: {e}")
            return "预测结果解释生成失败，请稍后重试"
    
    def compare_models_explanation(self, match_id: int, model_results: Dict[str, Any]) -> str:
        """比较不同模型的预测结果并解释差异"""
        try:
            prompt = f"""
            以下是针对同一场比赛的不同AI模型的预测结果，请分析它们的差异和原因：
            
            模型预测结果:
            {str(model_results)}
            
            请提供以下方面的分析：
            1. 各模型预测结果的异同点
            2. 可能导致差异的因素
            3. 各模型的优势和局限性
            4. 综合判断和建议
            
            请以专业且易懂的语言进行分析。
            """
            
            explanation = self.llm_service.generate_response(
                prompt,
                provider="gemini",
                temperature=0.4,
                max_tokens=600
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"模型比较解释生成失败: {e}")
            return "模型比较解释生成失败"
```

### 7.4 智能对话助手

创建`backend/services/conversation_agent.py`：

```python
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..services.llm_service import LLMService
from datetime import datetime

class ConversationAgent:
    """智能对话助手 - 为用户提供自然语言交互"""
    
    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.llm_service = llm_service
        self.context_history = {}  # 存储对话历史
    
    def respond_to_user(self, user_input: str, user_id: str = "default") -> str:
        """响应用户输入"""
        try:
            # 获取用户对话历史
            history = self.context_history.get(user_id, [])
            
            # 构造提示，包含上下文信息
            context_prompt = f"""
            你是体育彩票智能助手，专门协助用户了解彩票数据、分析和预测。
            请根据用户的问题提供专业、准确的回答。
            
            当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            请遵循以下原则：
            1. 提供准确的信息
            2. 对于预测结果，强调不确定性
            3. 鼓励理性购彩
            4. 如涉及具体数据，请说明数据来源和时效性
            
            历史对话:
            {self._format_history(history)}
            
            用户问题: {user_input}
            
            请提供专业、友好且信息丰富的回复。
            """
            
            response = self.llm_service.generate_response(
                context_prompt,
                provider="qwen",  # 对话场景使用通义千问
                temperature=0.7,
                max_tokens=400
            )
            
            # 更新对话历史
            self._update_history(user_id, user_input, response)
            
            return response
            
        except Exception as e:
            logger.error(f"对话助手响应失败: {e}")
            return "抱歉，我现在遇到了一些技术问题，请稍后再试。"
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史"""
        if not history:
            return "无历史对话"
        
        formatted = []
        for item in history[-5:]:  # 只保留最近5次对话
            formatted.append(f"用户: {item['user_input']}")
            formatted.append(f"助手: {item['response']}")
        
        return "\n".join(formatted)
    
    def _update_history(self, user_id: str, user_input: str, response: str):
        """更新对话历史"""
        if user_id not in self.context_history:
            self.context_history[user_id] = []
        
        self.context_history[user_id].append({
            "user_input": user_input,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史记录长度
        if len(self.context_history[user_id]) > 10:
            self.context_history[user_id] = self.context_history[user_id][-10:]
    
    def get_match_analysis(self, team1: str, team2: str) -> str:
        """获取比赛分析"""
        try:
            prompt = f"""
            请对 {team1} vs {team2} 的比赛进行专业分析，包括：
            1. 两队实力对比
            2. 历史交锋记录
            3. 近期状态分析
            4. 关键球员情况
            5. 战术风格对比
            6. 比赛预测（强调不确定性）
            
            请提供专业且平衡的分析。
            """
            
            response = self.llm_service.generate_response(
                prompt,
                provider="openai",
                temperature=0.6,
                max_tokens=800
            )
            
            return response
            
        except Exception as e:
            logger.error(f"比赛分析生成失败: {e}")
            return f"无法生成 {team1} vs {team2} 的分析，请稍后重试"
```

## 8. LLM集成API设计

### 8.1 LLM服务API

在`backend/api/v1/llm.py`中创建API：

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from ...database import get_db
from ...services.llm_service import LLMService
from ...services.conversation_agent import ConversationAgent
from ...services.prediction_explainer import PredictionExplainer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm", tags=["llm"])

# 全局LLM服务实例（在实际应用中应通过依赖注入管理）
llm_service = LLMService()

# 初始化各种LLM提供商（从环境变量获取API密钥）
import os
api_keys = {
    'openai': os.getenv('OPENAI_API_KEY'),
    'gemini': os.getenv('GEMINI_API_KEY'),
    'qwen': os.getenv('QWEN_API_KEY'),
    'deepseek': os.getenv('DEEPSEEK_API_KEY'),
}

# 注册提供商
if api_keys['openai']:
    from ...services.llm_service import OpenAILLM
    llm_service.register_provider('openai', OpenAILLM(api_keys['openai']))
    
if api_keys['gemini']:
    from ...services.llm_service import GeminiLLM
    llm_service.register_provider('gemini', GeminiLLM(api_keys['gemini']))
    
if api_keys['qwen']:
    from ...services.llm_service import QwenLLM
    llm_service.register_provider('qwen', QwenLLM(api_keys['qwen']))

@router.post("/chat")
async def chat_with_assistant(
    request: Request,
    user_input: str,
    user_id: str = "default",
    provider: str = "qwen",
    db: Session = Depends(get_db)
):
    """与智能助手对话"""
    try:
        agent = ConversationAgent(db, llm_service)
        response = agent.respond_to_user(user_input, user_id)
        return {"response": response, "provider": provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")

@router.post("/explain-prediction")
async def explain_prediction(
    match_id: int,
    prediction_data: Dict[str, Any],
    provider: str = "openai",
    db: Session = Depends(get_db)
):
    """解释预测结果"""
    try:
        explainer = PredictionExplainer(db, llm_service)
        explanation = explainer.explain_prediction(match_id, prediction_data)
        return {"explanation": explanation, "provider": provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测解释失败: {str(e)}")

@router.post("/analyze-intelligence")
async def analyze_intelligence_with_llm(
    intelligence_id: int,
    provider: str = "gemini",
    db: Session = Depends(get_db)
):
    """使用LLM分析情报"""
    try:
        from ...models.intelligence import Intelligence
        intelligence_item = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
        
        if not intelligence_item:
            raise HTTPException(status_code=404, detail="情报项未找到")
        
        from ...services.intelligence_service import AIIntelligenceService
        service = AIIntelligenceService(db, llm_service)
        analysis = service.analyze_intelligence_with_llm(intelligence_item)
        
        return {"analysis": analysis, "provider": provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情报分析失败: {str(e)}")

@router.get("/providers")
async def get_available_providers():
    """获取可用的LLM提供商"""
    providers = list(llm_service.providers.keys())
    return {"providers": providers, "default": llm_service.default_provider}
```

## 9. 模型训练与部署

### 9.1 自动化训练管道

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
        
        # 每日训练LLM模型性能监控
        self.scheduler.add_job(
            self.update_llm_performance_metrics,
            'cron',
            hour=4,
            id='daily_llm_performance'
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
    
    def update_llm_performance_metrics(self):
        """更新LLM性能指标"""
        # 监控LLM调用频率、响应时间和成本
        logger.info(f"LLM累计调用成本: ${llm_service.request_cost:.4f}")
        
        # 可以在此处添加更详细的性能分析
        pass
```

## 10. 监控与运维

### 10.1 性能监控

```python
class AIPerformanceMonitor:
    """
    AI性能监控器
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.llm_monitor = LLMUsageMonitor()  # LLM使用监控
    
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
    
    def monitor_llm_usage(self):
        """监控LLM使用情况"""
        # 检查是否超出使用限制
        for provider in llm_service.providers.keys():
            if not self.llm_monitor.is_within_daily_limit(provider):
                self.alert_manager.send_alert(
                    "llm_usage_limit_exceeded",
                    f"LLM提供商 {provider} 超出每日使用限额",
                    severity="warning"
                )
    
    def collect_system_metrics(self):
        """收集系统指标"""
        metrics = {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'active_connections': len(active_connections),
            'request_rate': self.get_request_rate(),
            'error_rate': self.get_error_rate(),
            'llm_request_cost': llm_service.request_cost,
            'llm_request_count': len(llm_service.requests_log) if hasattr(llm_service, 'requests_log') else 0
        }
        
        self.metrics_collector.record_metrics(metrics)
```

## 11. 部署与配置

### 11.1 Docker配置增强

在`docker-compose.yml`中添加LLM相关配置：

```yaml
version: '3.8'

services:
  backend-llm:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./sport_lottery.db}
      - REDIS_URL=${REDIS_URL:-redis://redis:6379/0}
      
      # LLM API Keys
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - QWEN_API_KEY=${QWEN_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      
      # LLM Settings
      - DEFAULT_LLM_PROVIDER=${DEFAULT_LLM_PROVIDER:-qwen}
      - LLM_REQUEST_TIMEOUT=${LLM_REQUEST_TIMEOUT:-30}
      - LLM_MAX_RETRIES=${LLM_MAX_RETRIES:-3}
      - LLM_CACHE_ENABLED=${LLM_CACHE_ENABLED:-true}
      - LLM_CACHE_TTL=${LLM_CACHE_TTL:-3600}
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
```

## 12. 测试策略

### 12.1 综合测试

```python
# tests/integration/test_ai_integration.py
import pytest
from unittest.mock import Mock, patch
from backend.services.llm_service import LLMService
from backend.services.prediction_service import AIPredictionService

class TestAIIntegration:
    
    def test_end_to_end_prediction_with_llm_explanation(self, db_session):
        """测试端到端预测及LLM解释"""
        # 初始化LLM服务
        llm_service = LLMService()
        mock_provider = Mock()
        mock_provider.generate_response.return_value = '{"impact_level": "high", "credibility_score": 0.8}'
        llm_service.register_provider("mock_provider", mock_provider)
        
        # 测试预测服务
        prediction_service = AIPredictionService(db_session)
        result = prediction_service.predict_match_outcome_with_ml(1)
        
        # 测试解释服务
        explainer = PredictionExplainer(db_session, llm_service)
        explanation = explainer.explain_prediction(1, result)
        
        assert "预测的主要依据" in explanation
        assert result['confidence'] > 0
    
    @patch('backend.services.llm_service.OpenAILLM')
    def test_llm_intelligence_analysis(self, mock_llm_class, db_session):
        """测试LLM情报分析"""
        # 模拟LLM响应
        mock_llm_instance = Mock()
        mock_llm_instance.generate_response.return_value = '''
        {
            "impact_level": "high",
            "impact_reasoning": "关键球员伤病严重影响球队实力",
            "credibility_score": 0.85,
            "key_factors": ["主力前锋受伤", "替补实力不足"],
            "risk_warnings": ["伤病情况可能恶化"],
            "overall_assessment": "对比赛结果有重大影响"
        }
        '''
        mock_llm_class.return_value = mock_llm_instance
        
        # 初始化LLM服务
        llm_service = LLMService()
        llm_service.register_provider("openai", mock_llm_instance)
        
        # 测试情报分析
        from backend.models.intelligence import Intelligence
        from backend.services.intelligence_service import AIIntelligenceService
        
        intelligence_item = Intelligence(
            type="injury",
            content="球队主力前锋因肌肉拉伤将缺席本场比赛",
            source="official",
            confidence="high"
        )
        
        service = AIIntelligenceService(db_session, llm_service)
        analysis = service.analyze_intelligence_with_llm(intelligence_item)
        
        assert analysis["impact_level"] == "high"
        assert analysis["credibility_score"] == 0.85
```

## 13. 总结

本综合AI原生架构方案将传统的机器学习能力与最新的大型语言模型技术有机结合，形成了一个完整的智能化体育彩票业务系统：

1. **基础AI能力**：包括智能数据采集、预测分析、情报分析和对冲策略
2. **LLM增强能力**：通过集成主流大语言模型，提供自然语言交互、高级推理和内容生成能力
3. **统一接口层**：抽象不同AI技术的实现细节，为业务逻辑提供一致的API
4. **成本控制机制**：监控和优化AI服务使用成本
5. **性能监控**：全面的系统性能和AI模型效果监控

这套架构不仅提升了系统的智能化水平，还增强了用户体验和业务效率，为体育彩票业务在AI时代的竞争力提供了坚实的技术基础。