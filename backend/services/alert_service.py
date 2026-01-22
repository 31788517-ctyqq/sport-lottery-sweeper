"""
告警服务
用于监控命中率并触发告警
"""
from sqlalchemy.orm import Session
from ..models.draw_prediction_result import DrawPredictionResult
from .draw_prediction_service import get_predictions
from datetime import datetime
from typing import Optional

# 告警阈值（命中率低于此值触发告警）
ALERT_THRESHOLD = 0.70  # 70%
ALERT_WINDOW_DAYS = 7  # 统计最近7天的命中率

def calculate_accuracy(db: Session, days: int = ALERT_WINDOW_DAYS) -> Optional[float]:
    """
    计算最近N天的命中率
    返回 0.0 ~ 1.0 之间的值
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    preds = get_predictions(db, start_date=start_date)

    # 只统计已结束的比赛
    finished = [p for p in preds if p.actual_result]
    if not finished:
        return None

    hits = [p for p in finished if p.actual_result == 'draw']
    accuracy = len(hits) / len(finished) if finished else 0
    return accuracy

def check_and_trigger_alert(db: Session) -> dict:
    """
    检查命中率并触发告警
    返回告警信息字典
    """
    accuracy = calculate_accuracy(db)

    if accuracy is None:
        return {
            "should_alert": False,
            "reason": "没有已结束的比赛数据"
        }

    if accuracy < ALERT_THRESHOLD:
        return {
            "should_alert": True,
            "accuracy": accuracy,
            "threshold": ALERT_THRESHOLD,
            "message": f"最近{ALERT_WINDOW_DAYS}天的命中率 ({accuracy:.1%}) 低于阈值 ({ALERT_THRESHOLD:.1%})，请注意模型性能！"
        }

    return {
        "should_alert": False,
        "accuracy": accuracy,
        "threshold": ALERT_THRESHOLD
    }

from datetime import timedelta
