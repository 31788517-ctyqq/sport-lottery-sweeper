"""
数据处理服务
处理比赛数据标准化和实体名称映射
"""

import re
import logging
from typing import Dict, Any

from backend.config.entity_mappings import get_standard_name
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class MatchDataProcessor:
    def __init__(self, source_config):
        self.source_config = source_config
        self.source_id = source_config.get('source_id', 'default')
        
    def process_match_data(self, raw_data):
        """处理原始比赛数据，进行标准化"""
        processed_data = {
            'home_team_id': self._normalize_team_name(raw_data.get('home_team')),
            'away_team_id': self._normalize_team_name(raw_data.get('away_team')),
            'league_id': self._normalize_league_name(raw_data.get('league')),
            'match_time': raw_data.get('match_time'),
            'odds': raw_data.get('odds'),
            'source_id': self.source_id,
            # ... other fields ...
        }
        
        return processed_data
        
    def _normalize_team_name(self, team_name):
        """标准化球队名称，返回业务唯一标识符"""
        if not team_name:
            return None
            
        # 尝试精确匹配
        standard_id = get_standard_name('team', team_name, self.source_id)
        if standard_id:
            return standard_id
            
        # 尝试模糊匹配（处理拼写错误或缩写）
        for possible_match in self._fuzzy_match_candidates(team_name):
            standard_id = get_standard_name('team', possible_match, self.source_id)
            if standard_id:
                return standard_id
                
        # 无法匹配时记录日志并返回原始值
        logger.warning(f"无法标准化球队名称: {team_name} (来源: {self.source_id})")
        return team_name  # 保留原始值作为后备
        
    def _fuzzy_match_candidates(self, name):
        """生成可能的模糊匹配候选"""
        if not name:
            return []
            
        # 移除常见停用词
        cleaned = re.sub(r'\b(fc|cf|club|united)\b', '', name, flags=re.IGNORECASE)
        # 生成缩写形式
        initials = ''.join([w[0].upper() for w in re.findall(r'\w+', cleaned)])
        # 生成常见变体
        candidates = [
            name.lower(),
            name.upper(),
            name.title(),
            initials,
            re.sub(r'[\s\-_]+', '', name)
        ]
        # 去除空字符串
        return [c for c in candidates if c.strip()]
        
    def _normalize_league_name(self, league_name):
        """标准化联赛名称，返回业务唯一标识符"""
        if not league_name:
            return None
            
        # 尝试精确匹配
        standard_id = get_standard_name('league', league_name, self.source_id)
        if standard_id:
            return standard_id
            
        # 尝试模糊匹配
        for possible_match in self._fuzzy_match_candidates(league_name):
            standard_id = get_standard_name('league', possible_match, self.source_id)
            if standard_id:
                return standard_id
                
        # 无法匹配时记录日志并返回原始值
        logger.warning(f"无法标准化联赛名称: {league_name} (来源: {self.source_id})")
        return league_name  # 保留原始值作为后备