#!/usr/bin/env python3
"""
初始化默认爬虫告警规则
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.models.crawler_alert_rules import CrawlerAlertRule
from backend.schemas.crawler_alert import AlertRuleCreate
from backend.services.crawler_alert_service import CrawlerAlertService


def init_default_alert_rules():
    """初始化默认告警规则"""
    db = SessionLocal()
    
    try:
        # 检查是否已有告警规则
        existing_rules = db.query(CrawlerAlertRule).count()
        if existing_rules > 0:
            print(f"数据库中已存在 {existing_rules} 个告警规则，跳过初始化")
            return
        
        # 默认告警规则配置
        default_rules = [
            {
                "name": "高错误率告警",
                "description": "当爬虫错误率超过阈值时触发告警",
                "metric_type": "error_rate",
                "threshold": 20.0,  # 20%
                "comparison_operator": "gt",
                "time_window_minutes": 60,
                "alert_level": "error",
                "cooldown_minutes": 30,
                "notification_channels": ["email", "slack"]
            },
            {
                "name": "严重错误率告警",
                "description": "当爬虫错误率超过严重阈值时触发告警",
                "metric_type": "error_rate",
                "threshold": 50.0,  # 50%
                "comparison_operator": "gt",
                "time_window_minutes": 30,
                "alert_level": "critical",
                "cooldown_minutes": 15,
                "notification_channels": ["email", "slack", "webhook"]
            },
            {
                "name": "响应时间过长告警",
                "description": "当爬虫平均响应时间超过阈值时触发告警",
                "metric_type": "response_time",
                "threshold": 5000.0,  # 5秒
                "comparison_operator": "gt",
                "time_window_minutes": 60,
                "alert_level": "warning",
                "cooldown_minutes": 60,
                "notification_channels": ["email"]
            },
            {
                "name": "严重响应时间告警",
                "description": "当爬虫响应时间过长时触发严重告警",
                "metric_type": "response_time",
                "threshold": 10000.0,  # 10秒
                "comparison_operator": "gt",
                "time_window_minutes": 30,
                "alert_level": "critical",
                "cooldown_minutes": 30,
                "notification_channels": ["email", "slack"]
            },
            {
                "name": "连续失败告警",
                "description": "当爬虫连续失败次数过多时触发告警",
                "metric_type": "consecutive_failures",
                "threshold": 5,
                "comparison_operator": "gte",
                "time_window_minutes": 120,
                "alert_level": "error",
                "cooldown_minutes": 60,
                "notification_channels": ["email", "slack"]
            },
            {
                "name": "严重连续失败告警",
                "description": "当爬虫连续失败次数达到严重程度时触发告警",
                "metric_type": "consecutive_failures",
                "threshold": 10,
                "comparison_operator": "gte",
                "time_window_minutes": 60,
                "alert_level": "critical",
                "cooldown_minutes": 30,
                "notification_channels": ["email", "slack", "webhook"]
            },
            {
                "name": "数据质量告警",
                "description": "当数据质量分数过低时触发告警",
                "metric_type": "data_quality",
                "threshold": 80.0,  # 80分
                "comparison_operator": "lt",
                "time_window_minutes": 120,
                "alert_level": "warning",
                "cooldown_minutes": 120,
                "notification_channels": ["email"]
            },
            {
                "name": "严重数据质量告警",
                "description": "当数据质量分数严重过低时触发告警",
                "metric_type": "data_quality",
                "threshold": 60.0,  # 60分
                "comparison_operator": "lt",
                "time_window_minutes": 60,
                "alert_level": "critical",
                "cooldown_minutes": 60,
                "notification_channels": ["email", "slack"]
            }
        ]
        
        service = CrawlerAlertService(db)
        created_count = 0
        
        for rule_config in default_rules:
            try:
                rule_data = AlertRuleCreate(**rule_config)
                result = service.create_alert_rule(rule_data, created_by=1)  # 假设管理员ID为1
                
                if result["success"]:
                    created_count += 1
                    print(f"✓ 创建告警规则成功: {rule_config['name']}")
                else:
                    print(f"✗ 创建告警规则失败: {rule_config['name']} - {result['message']}")
                    
            except Exception as e:
                print(f"✗ 创建告警规则异常: {rule_config['name']} - {str(e)}")
        
        print(f"\n默认告警规则初始化完成: 成功创建 {created_count}/{len(default_rules)} 个规则")
        
        # 输出创建的规则摘要
        print("\n=== 已创建的告警规则 ===")
        rules = service.get_alert_rules()
        for rule in rules:
            print(f"- {rule['name']} ({rule['metric_type']}, 阈值: {rule['threshold']}, 级别: {rule['alert_level']})")
        
    except Exception as e:
        print(f"初始化默认告警规则失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """主函数"""
    print("=== 爬虫告警规则初始化工具 ===")
    print(f"初始化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 测试数据库连接
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✓ 数据库连接正常")
        print()
        
        # 初始化默认规则
        init_default_alert_rules()
        
    except Exception as e:
        print(f"✗ 初始化过程出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()