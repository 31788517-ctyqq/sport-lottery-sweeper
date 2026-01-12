# data_source.py - 数据模型定义
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

logger = logging.getLogger(__name__)

# --- 枚举定义 ---
class Strategy(Enum):
    """爬虫策略枚举"""
    DIRECT_REQUEST = "direct_request"  # 直接请求 (VIPC API)
    SELENIUM = "selenium"              # Selenium模拟
    ALTERNATIVE_API = "alternative_api" # 备用API

class MatchStatus(Enum):
    """比赛状态枚举"""
    UPCOMING = "upcoming"  # 未开始
    LIVE = "live"          # 进行中
    FINISHED = "finished"  # 已结束
    CANCELLED = "cancelled" # 已取消

# --- 数据模型定义 ---
@dataclass
class MatchInfo:
    """比赛信息数据类"""
    match_id: str
    league: str
    home_team: str
    away_team: str
    kickoff_time: datetime
    venue: str = ""
    odds: Dict[str, float] = field(default_factory=dict)
    strategy: str = ""
    source: str = ""
    status: str = MatchStatus.UPCOMING.value
    confidence: float = 1.0
    crawl_time: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.odds:
            self.odds = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['kickoff_time'] = self.kickoff_time.isoformat() if self.kickoff_time else None
        data['crawl_time'] = self.crawl_time.isoformat() if self.crawl_time else None
        return data

    def __repr__(self):
        return (f"MatchInfo(id={self.match_id}, league={self.league}, "
                f"home={self.home_team}, away={self.away_team}, "
                f"time={self.kickoff_time.strftime('%Y-%m-%d %H:%M') if self.kickoff_time else 'N/A'})")

@dataclass
class ScraperResult:
    """爬虫结果数据类"""
    matches: List[MatchInfo]
    strategy_used: Strategy
    execution_time: float
    success: bool
    error_message: str = ""
    debug_info: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.debug_info:
            self.debug_info = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['strategy_used'] = self.strategy_used.value
        data['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        data['matches'] = [match.to_dict() for match in self.matches]
        return data

    def __repr__(self):
        return (f"ScraperResult(strategy={self.strategy_used.value}, "
                f"matches={len(self.matches)}, success={self.success}, "
                f"time={self.execution_time:.2f}s)")