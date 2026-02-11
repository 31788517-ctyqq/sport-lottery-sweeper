from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal
import re


def convert_real_api_to_internal_model(real_data: Dict[str, Any], date_time: Optional[str] = None) -> Dict[str, Any]:
    """
    将真实API数据转换为内部数据模型
    """
    # 提取并转换数值字段
    home_power = real_data.get('homePower', 0)
    guest_power = real_data.get('guestPower', 0)
    home_win_pan = real_data.get('homeWinPan', 0.0)
    guest_win_pan = real_data.get('guestWinPan', 0.0)
    
    # 计算实力等级差和赢盘等级差
    power_diff = abs(home_power - guest_power)
    win_pan_diff = abs(home_win_pan - guest_win_pan)
    
    # 赔率处理
    home_award = float(real_data.get('homeWinAward', 0)) if real_data.get('homeWinAward') else 0
    guest_award = float(real_data.get('guestWinAward', 0)) if real_data.get('guestWinAward') else 0
    draw_award = float(real_data.get('drawAward', 0)) if real_data.get('drawAward') else 0
    
    # 计算一赔稳定性（这里是一个简化计算，可以根据实际需求调整）
    stability = abs(home_award - guest_award) if home_award != 0 and guest_award != 0 else 0
    
    # 解析比赛时间
    match_time_str = real_data.get('matchTimeStr', '')
    match_time = None
    if match_time_str:
        try:
            match_time = datetime.strptime(match_time_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    # 构建内部模型
    internal_model = {
        'match_id': real_data.get('lineId', ''),
        'home_team': real_data.get('homeTeam', ''),
        'away_team': real_data.get('guestTeam', ''),
        'league': real_data.get('gameShortName', ''),
        'match_time': match_time,
        'power_home': home_power,
        'power_away': guest_power,
        'win_pan_home': home_win_pan,
        'win_pan_away': guest_win_pan,
        'odds_home': home_award,
        'odds_away': guest_award,
        'odds_draw': draw_award,
        'stability': stability,
        'power_diff': power_diff,
        'win_pan_diff': win_pan_diff,
        'rq': int(real_data.get('rq', 0)),  # 让球
        'home_feature': real_data.get('homeFeature', ''),
        'away_feature': real_data.get('guestFeature', ''),
        'home_spf': real_data.get('homeSpf', ''),  # 主队胜负平
        'away_spf': real_data.get('guestSpf', ''),  # 客队胜负平
        'data_source': '100qiu',
        'raw_data': real_data  # 保留原始数据
    }
    
    # 如果提供了date_time，将其添加到raw_data中
    if date_time:
        internal_model['raw_data']['date_time'] = date_time
    
    return internal_model


def convert_real_api_batch_to_internal(real_data_list: List[Dict[str, Any]], date_time: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    批量转换真实API数据到内部模型
    """
    return [convert_real_api_to_internal_model(item, date_time) for item in real_data_list]


def calculate_p_level(power_diff: float, win_pan_diff: float, stability: float) -> int:
    """
    根据实力等级差、赢盘等级差和一赔稳定性计算P级
    """
    # 这里是简化的P级计算逻辑，可以根据实际需求调整
    if power_diff <= 10 and win_pan_diff <= 0.5 and stability <= 0.5:
        return 1  # P1级
    elif power_diff <= 20 and win_pan_diff <= 1.0 and stability <= 1.0:
        return 2  # P2级
    elif power_diff <= 30 and win_pan_diff <= 1.5 and stability <= 1.5:
        return 3  # P3级
    elif power_diff <= 40 and win_pan_diff <= 2.0 and stability <= 2.0:
        return 4  # P4级
    else:
        return 5  # P5级


def apply_downgrade_rule(power_diff_direction: str, win_pan_diff_direction: str, p_level: int) -> int:
    """
    应用降级规则：实力等级差方向与赢盘等级差方向背离时，P级强制下移一级
    """
    if power_diff_direction != win_pan_diff_direction and p_level < 5:
        return p_level + 1
    return p_level


def extract_delta_wp(internal_model: Dict[str, Any]) -> float:
    """
    提取ΔWP值（这里是一个简化的实现，根据实际需求调整）
    """
    # 根据实际需求计算ΔWP
    home_wp = internal_model.get('win_pan_home', 0)
    away_wp = internal_model.get('win_pan_away', 0)
    return abs(home_wp - away_wp)


def calculate_strength_diff(home_power: float, away_power: float) -> int:
    """
    计算实力等级差 (ΔP)
    ΔP = 主队实力值 - 客队实力值
    """
    diff = home_power - away_power
    
    if diff > 25:
        return 3
    elif 17 <= diff <= 25:
        return 2
    elif 9 <= diff <= 16:
        return 1
    elif -8 <= diff <= 8:
        return 0
    elif -16 <= diff <= -9:
        return -1
    elif -25 <= diff <= -17:
        return -2
    else:  # diff < -25
        return -3


def calculate_win_level_diff(home_wp: float, away_wp: float) -> int:
    """
    计算赢盘等级差 (ΔWP)
    Step 1: 单队WP评分 → 分值转换
       WP>1.40 → S(4)
       1.20-1.40 → A(3) 
       0.80-1.20 → B(2)
       0.60-0.80 → C(1)
       WP<0.60 → D(0)
    
    Step 2: ΔWP = 主队分值 - 客队分值
    """
    def wp_to_score(wp: float) -> int:
        if wp > 1.40:
            return 4  # S
        elif 1.20 <= wp <= 1.40:
            return 3  # A
        elif 0.80 <= wp <= 1.19:
            return 2  # B
        elif 0.60 <= wp <= 0.79:
            return 1  # C
        else:  # wp < 0.60
            return 0  # D

    home_score = wp_to_score(home_wp)
    away_score = wp_to_score(away_wp)
    
    return home_score - away_score


def calculate_stability_tier(home_odds: List[float], away_odds: List[float]) -> str:
    """
    计算一赔稳定性 (P-Tier)
    基于一赔指数出现频率计算的稳定性等级，反映正路可信度。
    """
    # 简化实现，实际情况需要更复杂的计算逻辑
    has_home_odds = len(home_odds) > 0
    has_away_odds = len(away_odds) > 0
    
    if has_home_odds and has_away_odds:
        # 双一赔
        p_value = sum(home_odds) + sum(away_odds)
        if p_value >= 140:
            return "S"  # S(P1)
        elif 110 <= p_value < 140:
            return "A"  # S(P2)
        else:
            return "B-"  # S(P4)
    elif has_home_odds or has_away_odds:
        # 单一赔
        odds_sum = sum(home_odds) if has_home_odds else sum(away_odds)
        if odds_sum >= 40:
            return "B"  # S(P3)
        elif 15 <= odds_sum < 40:
            return "C"  # S(P5)
        else:
            return "D"  # S(P6)
    else:
        # 无一赔
        return "E"  # S(P7)


def transform_beidan_match(raw_data: Dict) -> Dict:
    """
    北单数据转换器（实现文档P7页数据结构要求）
    """
    # 提取数据，适配真实API数据结构
    home_team = raw_data.get('homeTeam', raw_data.get('home_team', ''))
    guest_team = raw_data.get('guestTeam', raw_data.get('away_team', ''))
    
    # 适配真实API中的字段名
    home_power = raw_data.get('homePower', raw_data.get('home_power', 0))
    guest_power = raw_data.get('guestPower', raw_data.get('away_power', 0))
    
    home_wp = raw_data.get('homeWinPan', raw_data.get('home_wp', 0))
    guest_wp = raw_data.get('guestWinPan', raw_data.get('away_wp', 0))
    
    # 从特征字符串中提取一赔概率
    home_feature = raw_data.get('homeFeature', '')
    guest_feature = raw_data.get('guestFeature', '')
    
    # 提取一赔概率值
    home_odds = extract_odds_from_feature(home_feature)
    guest_odds = extract_odds_from_feature(guest_feature)
    
    # 获取ssum值
    ssum = raw_data.get('ssum', 0)
    
    return {
        'id': raw_data.get('id', raw_data.get('lineId', '')),
        'teams': f"{home_team} vs {guest_team}",
        'strength': calculate_strength_diff(home_power, guest_power),
        'winLevel': calculate_win_level_diff(home_wp, guest_wp),
        'stability': calculate_stability_tier(home_odds, guest_odds),
        'warning': None,
        'sortScore': 0,
        'ssum': ssum
    }


def extract_odds_from_feature(feature_str: str) -> List[float]:
    """
    从特征字符串中提取一赔概率
    例如："一赔概率50%" -> [50.0]
    """
    import re
    # 查找形如 "XX%" 的数字
    matches = re.findall(r'(\d+)%', feature_str)
    if matches:
        return [float(match) for match in matches]
    return []


def transform_real_beidan_match(raw_data: Dict) -> Dict:
    """
    转换真实API数据结构的北单比赛数据
    """
    # 从真实API数据结构中提取必要字段
    home_team = raw_data.get('homeTeam', '')
    guest_team = raw_data.get('guestTeam', '')
    
    # 实力值
    home_power = raw_data.get('homePower', 0)
    guest_power = raw_data.get('guestPower', 0)
    
    # 让球盘口
    home_wp = raw_data.get('homeWinPan', 0)
    guest_wp = raw_data.get('guestWinPan', 0)
    
    # 从特征字符串中提取一赔概率
    home_feature = raw_data.get('homeFeature', '')
    guest_feature = raw_data.get('guestFeature', '')
    
    home_odds = extract_odds_from_feature(home_feature)
    guest_odds = extract_odds_from_feature(guest_feature)
    
    # 计算ssum值 - 使用一些指标的组合
    ssum = calculate_ssum_value(raw_data)
    
    return {
        'id': raw_data.get('lineId', raw_data.get('id', '')),
        'teams': f"{home_team} vs {guest_team}",
        'strength': calculate_strength_diff(home_power, guest_power),
        'winLevel': calculate_win_level_diff(home_wp, guest_wp),
        'stability': calculate_stability_tier(home_odds, guest_odds),
        'warning': None,
        'sortScore': 0,
        'ssum': ssum
    }


def calculate_ssum_value(match_data: Dict) -> int:
    """
    根据比赛数据计算ssum值（用于P7排序规则）
    """
    # 计算一个综合分数，基于多个因素
    factors = [
        match_data.get('homePower', 0),
        match_data.get('guestPower', 0),
        abs(match_data.get('homeWinPan', 0) - match_data.get('guestWinPan', 0)) * 10,
        int(match_data.get('homeDxqPercentStr', '0').rstrip('%')),
        int(match_data.get('guestDxqPercentStr', '0').rstrip('%')),
    ]
    
    # 取平均值并转换为整数
    avg_factor = sum(f for f in factors if isinstance(f, (int, float))) / len([f for f in factors if isinstance(f, (int, float))])
    return int(avg_factor)


def transform_multiple_beidan_matches(matches_data: List[Dict]) -> List[Dict]:
    """
    批量转换北单比赛数据
    """
    transformed_matches = []
    for match_data in matches_data:
        try:
            # 尝试使用真实API数据结构进行转换
            if 'homeTeam' in match_data or 'guestTeam' in match_data:
                transformed = transform_real_beidan_match(match_data)
            else:
                transformed = transform_beidan_match(match_data)
            transformed_matches.append(transformed)
        except Exception as e:
            print(f"转换比赛数据失败: {e}, 数据: {match_data}")
            continue
    
    return transformed_matches