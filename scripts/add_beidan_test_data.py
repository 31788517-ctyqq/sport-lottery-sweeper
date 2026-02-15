"""
添加北单策略测试数据
解决策略管理API返回404错误的问题
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(__file__))

from backend.database import get_db
from backend.models.beidan_strategy import BeidanStrategy

def add_test_strategies():
    """添加测试策略数据"""
    db = next(get_db())
    try:
        # 检查是否已有数据
        existing = db.query(BeidanStrategy).filter(BeidanStrategy.is_active == True).first()
        if existing:
            print("数据库中已有策略数据，跳过添加")
            return
        
        # 添加示例策略数据
        test_strategies = [
            {
                "name": "保守稳健策略",
                "description": "适合新手用户，风险较低的选择",
                "three_dimensional": {
                    "strengthDifference": {"includeNegative": True, "includeNeutral": True, "includePositive": False, "minValue": -15, "maxValue": 5},
                    "winPanDifference": {"includeNegative": False, "includeNeutral": True, "includePositive": True, "minValue": 0, "maxValue": 10},
                    "stabilityTier": {"includeP1": True, "includeP2": True, "includeP3": True, "includeP4": False, "includeP5": False, "includeP6": False, "includeP7": False}
                },
                "other_conditions": {
                    "leagues": ["英超", "西甲", "德甲"],
                    "dateTime": "26011",
                    "oneOddsRange": {"min": 1.5, "max": 3.0},
                    "awayOddsRange": {"min": 2.0, "max": 4.0}
                },
                "sort_config": {"field": "recommendation", "order": "asc"},
                "user_id": 1,
                "is_public": True
            },
            {
                "name": "积极进攻策略", 
                "description": "适合有经验用户，追求高收益",
                "three_dimensional": {
                    "strengthDifference": {"includeNegative": False, "includeNeutral": False, "includePositive": True, "minValue": 10, "maxValue": 25},
                    "winPanDifference": {"includeNegative": False, "includeNeutral": False, "includePositive": True, "minValue": 5, "maxValue": 15},
                    "stabilityTier": {"includeP1": False, "includeP2": True, "includeP3": True, "includeP4": True, "includeP5": True, "includeP6": True, "includeP7": True}
                },
                "other_conditions": {
                    "leagues": ["意甲", "法甲", "欧冠"],
                    "dateTime": "26012",
                    "oneOddsRange": {"min": 1.8, "max": 2.5},
                    "awayOddsRange": {"min": 2.5, "max": 5.0}
                },
                "sort_config": {"field": "match_time", "order": "desc"},
                "user_id": 1,
                "is_public": True
            },
            {
                "name": "平衡发展策略",
                "description": "平衡风险与收益的综合策略",
                "three_dimensional": {
                    "strengthDifference": {"includeNegative": True, "includeNeutral": True, "includePositive": True, "minValue": -10, "maxValue": 10},
                    "winPanDifference": {"includeNegative": True, "includeNeutral": True, "includePositive": True, "minValue": -5, "maxValue": 5},
                    "stabilityTier": {"includeP1": True, "includeP2": True, "includeP3": True, "includeP4": True, "includeP5": False, "includeP6": False, "includeP7": False}
                },
                "other_conditions": {
                    "leagues": ["中超", "日职联", "韩K联"],
                    "dateTime": "26013", 
                    "oneOddsRange": {"min": 1.6, "max": 2.8},
                    "awayOddsRange": {"min": 2.2, "max": 4.5}
                },
                "sort_config": {"field": "league", "order": "asc"},
                "user_id": 1,
                "is_public": False
            }
        ]
        
        for strategy_data in test_strategies:
            strategy = BeidanStrategy(
                name=strategy_data["name"],
                description=strategy_data["description"],
                three_dimensional=strategy_data["three_dimensional"],
                other_conditions=strategy_data["other_conditions"],
                sort_config=strategy_data["sort_config"],
                user_id=strategy_data["user_id"],
                is_public=strategy_data["is_public"],
                is_active=True,
                usage_count=0,
                success_rate="0%",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(strategy)
        
        db.commit()
        print(f"成功添加 {len(test_strategies)} 个测试策略")
        
        # 验证数据
        strategies = db.query(BeidanStrategy).filter(BeidanStrategy.is_active == True).all()
        for s in strategies:
            print(f"ID: {s.id}, Name: {s.name}, User: {s.user_id}")
            
    except Exception as e:
        print(f"添加测试数据失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_strategies()