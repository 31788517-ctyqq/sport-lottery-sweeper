from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import models
from backend.config import settings


def process_data(data):
    """处理数据"""
    print(f"使用配置: {settings.PROJECT_NAME}")
    # 处理逻辑...
    return data


class DataProcessor:
    """数据处理类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_intelligence(self, match_id: str, intelligence_list: List[Dict]) -> List[models.Intelligence]:
        """处理原始情报数据"""
        processed_intelligence = []
        
        for intel in intelligence_list:
            # 检查是否已存在相同的情报
            existing = self.db.query(models.Intelligence).filter(
                models.Intelligence.match_id == match_id,
                models.Intelligence.summary == intel.get('summary')
            ).first()
            
            if existing:
                # 更新现有情报的权重和时间
                existing.weight = self._calculate_weight(intel)
                existing.updated_at = datetime.utcnow()
                existing.is_new = False
                self.db.commit()
                continue
            
            # 创建新的情报记录
            processed = models.Intelligence(
                match_id=match_id,
                summary=intel.get('summary'),
                content=intel.get('content'),
                category=self._categorize_intelligence(intel.get('content', '')),
                source=intel.get('source', 'media'),
                weight=self._calculate_weight(intel),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_new=True
            )
            
            processed_intelligence.append(processed)
            self.db.add(processed)
        
        self.db.commit()
        return processed_intelligence
    
    def process_predictions(self, match_id: str, predictions_list: List[Dict]) -> List[models.Prediction]:
        """处理预测数据"""
        processed_predictions = []
        
        for pred in predictions_list:
            # 检查是否已存在相同的预测
            existing = self.db.query(models.Prediction).filter(
                models.Prediction.match_id == match_id,
                models.Prediction.type == pred.get('type'),
                models.Prediction.source == pred.get('source')
            ).first()
            
            if existing:
                # 更新现有预测
                existing.prediction = pred.get('prediction')
                existing.weight = pred.get('weight', 7.0)
                existing.updated_at = datetime.utcnow()
                self.db.commit()
                continue
            
            # 创建新的预测记录
            processed = models.Prediction(
                match_id=match_id,
                type=pred.get('type'),
                prediction=pred.get('prediction'),
                source=pred.get('source'),
                weight=pred.get('weight', 7.0),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            processed_predictions.append(processed)
            self.db.add(processed)
        
        self.db.commit()
        return processed_predictions
    
    def _categorize_intelligence(self, content: str) -> str:
        """根据内容自动分类情报"""
        content = content.lower()
        
        # 伤病情况
        if any(word in content for word in ['受伤', '停赛', '伤病', '缺阵', '缺席']):
            return 'injury'
            
        # 天气因素
        if any(word in content for word in ['天气', '雨', '雪', '温度', '湿度']):
            return 'weather'
            
        # 裁判信息
        if any(word in content for word in ['裁判', '主裁', '边裁', 'VAR']):
            return 'referee'
            
        # 战意分析
        if any(word in content for word in ['战意', '争冠', '保级', '德比', '宿敌']):
            return 'motive'
            
        # 战术/教练
        if any(word in content for word in ['战术', '阵型', '打法', '教练', '主帅']):
            return 'tactics'
            
        # 主场氛围
        if any(word in content for word in ['主场', '氛围', '球迷', '声势']):
            return 'atmosphere'
            
        # 历史交锋
        if any(word in content for word in ['历史', '交锋', '往绩', '对阵']):
            return 'history'
            
        return 'other'
    
    def _calculate_weight(self, intel: Dict) -> float:
        """计算情报权重"""
        base_weight = 7.0
        
        # 根据来源调整权重
        source = intel.get('source', 'media')
        source_weights = settings.source_weights
        base_weight = source_weights.get(source, base_weight)
        
        # 根据分类调整权重
        category = self._categorize_intelligence(intel.get('content', ''))
        category_weights = settings.category_weights
        category_weight = category_weights.get(category, base_weight)
        
        # 综合权重计算
        final_weight = (base_weight + category_weight) / 2
        
        # 根据内容关键词微调
        content = intel.get('content', '').lower()
        if any(word in content for word in ['主力', '关键', '重要']):
            final_weight += 0.5
        elif any(word in content for word in ['可能', '或许', '传闻', '疑似']):
            final_weight -= 0.5
        
        # 确保权重在合理范围内
        return max(7.0, min(9.8, final_weight))