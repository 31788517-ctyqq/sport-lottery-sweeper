from typing import List
from sqlalchemy.orm import Session
from ..models.lottery import FootballMatch  # 假设使用FootballMatch模型


def get_beidan_matches(db: Session) -> List[object]:
    """
    获取北单比赛数据
    """
    # 这里是示例实现，实际需要根据数据库结构调整
    matches = db.query(FootballMatch).all()
    
    # 转换为适合北单筛选的数据结构
    result = []
    for match in matches:
        # 构造北单比赛数据
        beidan_match = {
            'id': match.id,
            'match_id': match.id,
            'home_team': match.home_team,
            'away_team': match.away_team,
            'home_power': getattr(match, 'home_power', 0),
            'away_power': getattr(match, 'away_power', 0),
            'home_wp': getattr(match, 'home_wp', 0),
            'away_wp': getattr(match, 'away_wp', 0),
            'home_odds': getattr(match, 'home_odds', '[]'),
            'away_odds': getattr(match, 'away_odds', '[]'),
            'ssum': getattr(match, 'ssum', 0)
        }
        result.append(beidan_match)
    
    return result