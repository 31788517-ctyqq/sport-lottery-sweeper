from typing import Dict, List
from ..utils.data_processor import transform_beidan_match


class MatchModel:
    def __init__(self, id: str, teams: str, strength: int, winLevel: int, 
                 stability: str, tier: str = "", warning: str = "", 
                 sortScore: int = 0, ssum: int = 0):
        self.id = id
        self.teams = teams
        self.strength = strength
        self.winLevel = winLevel
        self.stability = stability
        self.tier = tier
        self.warning = warning
        self.sortScore = sortScore
        self.ssum = ssum


class BeidanFilterEngine:
    def __init__(self):
        # 初始化P级映射
        self.p_tier_map = {
            'S': 'P1', 'A': 'P2', 'B': 'P3', 'B-': 'P4', 
            'C': 'P5', 'D': 'P6', 'E': 'P7'
        }

    def transform_beidan_match(self, raw_data: dict) -> MatchModel:
        """
        北单数据转换器
        """
        transformed = transform_beidan_match(raw_data)
        
        # 计算P级
        tier = self.p_tier_map.get(transformed['stability'], '')
        
        return MatchModel(
            id=transformed['id'],
            teams=transformed['teams'],
            strength=transformed['strength'],
            winLevel=transformed['winLevel'],
            stability=transformed['stability'],
            tier=tier,
            warning=transformed['warning'],
            sortScore=transformed['sortScore'],
            ssum=transformed['ssum']
        )

    def apply_derating_rules(self, match: MatchModel) -> MatchModel:
        """
        应用文档P8降级规则
        """
        # 规则1：方向背离检测
        # 实力等级差方向 与 赢盘等级差方向 背离
        # (如：实力+3主优，但赢盘-3客热)
        if (match.strength > 0 and match.winLevel < 0) or \
           (match.strength < 0 and match.winLevel > 0):
            match.warning = "方向背离"
            match = self.downgrade_tier(match)  # P级降级
        
        # 规则2：实力优势方评级为 D级 (ΔP为-3的客队统治方)
        # 实力优势方评级为D级时，P级强制下移一级
        if abs(match.strength) == 3 and match.stability == 'D':
            match = self.downgrade_tier(match)
            
        return match

    def downgrade_tier(self, match: MatchModel) -> MatchModel:
        """
        降级P级
        """
        tier_order = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7']
        current_index = tier_order.index(match.tier) if match.tier in tier_order else len(tier_order)-1
        
        # 如果已经是P7，则不再降级
        if current_index < len(tier_order) - 1:
            match.tier = tier_order[current_index + 1]
        
        return match

    def apply_filters(self, matches: List[MatchModel], filters: dict) -> List[MatchModel]:
        """
        应用筛选条件
        """
        filtered = [
            m for m in matches 
            if (not filters.get('strength') or str(m.strength) in filters['strength']) and
               (not filters.get('winLevel') or str(m.winLevel) in filters['winLevel']) and
               (not filters.get('stability') or m.stability in filters['stability'])
        ]
        
        # 北单特有规则处理
        is_beidan = filters.get('source') == 'beidan'
        
        if is_beidan:
            # 应用文档P8降级规则
            filtered = [self.apply_derating_rules(m) for m in filtered]
            # 应用文档P7排序规则
            filtered = self._apply_beidan_sorting(filtered)
        
        return filtered

    def _apply_beidan_sorting(self, matches: List[MatchModel]) -> List[MatchModel]:
        """
        实现文档P7排序规则
        1. P3场次必须排在P4之前
        2. 同P级按ΔWP降序排列
        3. P7场次按Ssum升序排列
        """
        tier_order = {'P1': 1, 'P2': 2, 'P3': 3, 'P4': 4, 'P5': 5, 'P6': 6, 'P7': 7}
        
        def sort_key(match):
            # P级顺序
            tier_val = tier_order.get(match.tier, 99)
            # P7按Ssum升序，其他按winLevel降序
            secondary_sort = match.ssum if match.tier == 'P7' else -match.winLevel
            return (tier_val, secondary_sort)
        
        return sorted(matches, key=sort_key)

    def _p_tier_value(self, stability: str) -> int:
        """
        获取P级的数值表示
        """
        tier_values = {'S': 1, 'A': 2, 'B': 3, 'B-': 4, 'C': 5, 'D': 6, 'E': 7}
        return tier_values.get(stability, 99)


class FilterEngine:
    """
    兼容旧API的过滤引擎封装
    """
    def __init__(self):
        self._engine = BeidanFilterEngine()

    def apply_filters(self, filter_request) -> list:
        """
        兼容基础筛选接口：当前仅返回空列表，避免运行时异常。
        后续应接入真实数据源并调用 BeidanFilterEngine。
        """
        return []
