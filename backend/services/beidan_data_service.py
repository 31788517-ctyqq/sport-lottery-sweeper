import requests
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BeidanDataService:
    """北单数据服务类 - 专门处理北单比赛数据的获取和转换"""
    
    def __init__(self, db: Session):
        self.db = db
        # 北单API地址（根据实际API调整）
        self.base_url = "https://m.100qiu.com/api/dcListBasic"
        
    def fetch_beidan_data_from_api(self, date_time: str = "26011") -> List[Dict[str, Any]]:
        """
        从API获取北单数据
        :param date_time: 日期时间参数，如"26011"表示第26011期
        :return: API返回的原始数据列表
        """
        params = {
            "dateTime": date_time,
            "lotteryType": "BDSF"  # 北单玩法标识
        }
        
        try:
            logger.info(f"正在获取北单数据，期号: {date_time}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and isinstance(data["data"], list):
                logger.info(f"成功获取 {len(data['data'])} 条北单数据")
                return data["data"]
            else:
                logger.warning(f"API响应中没有有效北单数据: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求北单API失败: {e}")
            return []
        except ValueError as e:
            logger.error(f"解析北单API响应失败: {e}")
            return []
    
    def convert_api_data_to_match_format(self, api_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将API原始数据转换为前端需要的比赛格式
        :param api_data: API返回的原始数据
        :return: 转换后的比赛数据列表
        """
        converted_matches = []
        
        for item in api_data:
            try:
                # 基础信息转换
                match_time = item.get("matchTimeStr", "")
                if not match_time:
                    continue
                    
                # 队伍信息处理
                home_team = item.get("homeTeam", "").strip()
                guest_team = item.get("guestTeam", "").strip()
                
                if not home_team or not guest_team:
                    continue
                
                # 联赛信息处理
                league = item.get("gameShortName", "其他")
                # 标准化联赛名称
                league_mapping = {
                    "英超": "英超",
                    "西甲": "西甲", 
                    "德甲": "德甲",
                    "意甲": "意甲",
                    "法甲": "法甲",
                    "欧冠": "欧冠",
                    "世界杯": "世界杯"
                }
                standard_league = league_mapping.get(league, "其他")
                
                # 实力分析计算
                home_power = float(item.get("homePower", 0) or 0)
                guest_power = float(item.get("guestPower", 0) or 0)
                power_diff = home_power - guest_power
                
                # 确定实力等级
                if abs(power_diff) < 5:
                    home_strength = "均衡"
                    guest_strength = "均衡"
                    power_diff_desc = "势均力敌"
                elif power_diff > 0:
                    if power_diff >= 15:
                        home_strength = "偏强"
                        guest_strength = "偏弱"
                        power_diff_desc = "主队大优"
                    else:
                        home_strength = "偏强"
                        guest_strength = "均衡"
                        power_diff_desc = "主队占优"
                else:
                    if power_diff <= -15:
                        home_strength = "偏弱"
                        guest_strength = "偏强"
                        power_diff_desc = "客队大优"
                    else:
                        home_strength = "均衡"
                        guest_strength = "偏强"
                        power_diff_desc = "客队占优"
                
                # 赔率信息处理
                home_win_award = item.get("homeWinAward", "")
                guest_win_award = item.get("guestWinAward", "")
                draw_award = item.get("drawAward", "")
                
                # 转换赔率为浮点数
                def convert_odds(odds_str):
                    try:
                        return float(odds_str) if odds_str else 0.0
                    except (ValueError, TypeError):
                        return 0.0
                
                odds = {
                    "homeWin": convert_odds(home_win_award),
                    "draw": convert_odds(draw_award),
                    "guestWin": convert_odds(guest_win_award)
                }
                
                # 让球数处理
                handicap = "0"  # 默认让球数为0
                
                # 预测比分（基于实力分析简单推算）
                if abs(power_diff) >= 10:
                    if power_diff > 0:
                        predict_score = "2:0" if power_diff >= 20 else "2:1"
                    else:
                        predict_score = "0:2" if power_diff <= -20 else "1:2"
                else:
                    predict_score = "1:1"
                
                # 推荐等级
                if abs(power_diff) >= 15:
                    recommendation = "重点关注"
                elif abs(power_diff) >= 8:
                    recommendation = "值得关注"
                else:
                    recommendation = "观望"
                
                # 构建转换后的比赛数据
                converted_match = {
                    "id": hash(f"{match_time}_{home_team}_{guest_team}") % 1000000,  # 生成简单ID
                    "matchTime": match_time,
                    "league": standard_league,
                    "homeTeam": home_team,
                    "guestTeam": guest_team,
                    "handicap": handicap,
                    "odds": odds,
                    "strengthAnalysis": {
                        "homeStrength": home_strength,
                        "guestStrength": guest_strength,
                        "powerDifference": power_diff_desc
                    },
                    "predictScore": predict_score,
                    "recommendation": recommendation,
                    # 保留原始数据用于后续分析
                    "rawData": {
                        "homePower": home_power,
                        "guestPower": guest_power,
                        "powerDiff": power_diff,
                        "homeWinPan": float(item.get("homeWinPan", 0) or 0),
                        "guestWinPan": float(item.get("guestWinPan", 0) or 0),
                        "homeFeature": item.get("homeFeature"),
                        "guestFeature": item.get("guestFeature")
                    }
                }
                
                converted_matches.append(converted_match)
                
            except Exception as e:
                logger.error(f"转换比赛数据失败: {e}, 数据: {item}")
                continue
        
        logger.info(f"成功转换 {len(converted_matches)} 条比赛数据")
        return converted_matches
    
    def get_real_time_match_count(self) -> int:
        """
        获取实时比赛场次数（当前期次）
        :return: 比赛场次数
        """
        try:
            # 获取最新期次的实时数据
            api_data = self.fetch_beidan_data_from_api("26011")  # 使用最新期次
            return len(api_data)
        except Exception as e:
            logger.error(f"获取实时场次数失败: {e}")
            return 0
    
    def get_latest_date_time_options(self) -> tuple:
        """
        获取最新的日期时间选项
        :return: (选项列表, 最新期号)
        """
        try:
            # 模拟获取最近几期的数据
            periods = ["26011", "26010", "26009"]
            date_time_options = []
            
            for period in periods:
                api_data = self.fetch_beidan_data_from_api(period)
                if api_data:
                    date_time_options.append({
                        "value": period,
                        "label": f"第{period}期 ({'今日' if period == '26011' else '昨日' if period == '26010' else '前日'})"
                    })
            
            # 添加自定义选项
            date_time_options.append({
                "value": "custom",
                "label": "自定义日期"
            })
            
            latest_period = periods[0] if periods else "26011"
            
            return date_time_options, latest_period
            
        except Exception as e:
            logger.error(f"获取日期时间选项失败: {e}")
            # 返回默认值
            default_options = [
                {"value": "26011", "label": "第26011期 (今日)"},
                {"value": "26010", "label": "第26010期 (昨日)"},
                {"value": "26009", "label": "第26009期 (前日)"},
                {"value": "custom", "label": "自定义日期"}
            ]
            return default_options, "26011"
    
    def get_available_leagues(self) -> List[Dict[str, str]]:
        """
        获取可用的联赛选项
        :return: 联赛选项列表
        """
        try:
            # 从API获取一期数据来分析包含的联赛
            api_data = self.fetch_beidan_data_from_api("26011")
            
            leagues_found = set()
            for item in api_data:
                league = item.get("gameShortName", "其他")
                if league and league.strip():
                    leagues_found.add(league.strip())
            
            # 标准化联赛名称并构建选项
            league_mapping = {
                "英超": "英超",
                "西甲": "西甲",
                "德甲": "德甲", 
                "意甲": "意甲",
                "法甲": "法甲",
                "欧冠": "欧冠",
                "世界杯": "世界杯",
                "中超": "中超",
                "J联赛": "J联赛",
                "K联赛": "K联赛"
            }
            
            league_options = []
            for league in sorted(leagues_found):
                standard_name = league_mapping.get(league, league)
                league_options.append({
                    "value": league.lower().replace(" ", "_"),
                    "label": standard_name
                })
            
            # 如果没有找到任何联赛，返回默认选项
            if not league_options:
                league_options = [
                    {"value": "premier_league", "label": "英超"},
                    {"value": "la_liga", "label": "西甲"},
                    {"value": "bundesliga", "label": "德甲"},
                    {"value": "serie_a", "label": "意甲"},
                    {"value": "ligue_1", "label": "法甲"},
                    {"value": "champions_league", "label": "欧冠"}
                ]
            
            return league_options
            
        except Exception as e:
            logger.error(f"获取联赛选项失败: {e}")
            # 返回默认联赛选项
            return [
                {"value": "premier_league", "label": "英超"},
                {"value": "la_liga", "label": "西甲"},
                {"value": "bundesliga", "label": "德甲"},
                {"value": "serie_a", "label": "意甲"},
                {"value": "ligue_1", "label": "法甲"},
                {"value": "champions_league", "label": "欧冠"}
            ]
    
    async def get_filtered_matches(self, filter_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据筛选条件获取比赛数据
        :param filter_params: 筛选参数字典
        :return: 筛选后的比赛列表
        """
        try:
            # 获取基础数据
            date_time = filter_params.get("dateTime", "26011")
            api_data = self.fetch_beidan_data_from_api(date_time)
            
            if not api_data:
                return []
            
            # 转换为标准格式
            all_matches = self.convert_api_data_to_match_format(api_data)
            
            # 应用筛选条件
            filtered_matches = self._apply_filters(all_matches, filter_params)
            
            return filtered_matches
            
        except Exception as e:
            logger.error(f"筛选比赛数据失败: {e}")
            return []
    
    def _apply_filters(self, matches: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        应用筛选条件
        :param matches: 原始比赛列表
        :param filters: 筛选条件
        :return: 筛选后的比赛列表
        """
        filtered = matches.copy()
        
        # 联赛筛选
        leagues = filters.get("otherConditions", {}).get("leagues", [])
        if leagues:
            filtered = [m for m in filtered if m["league"] in leagues]
        
        # 日期时间筛选
        target_date_time = filters.get("otherConditions", {}).get("dateTime")
        if target_date_time and target_date_time != "custom":
            # 如果需要特定日期时间的筛选逻辑，在这里实现
            pass
        
        # 强度筛选
        strength = filters.get("otherConditions", {}).get("strength")
        if strength:
            # 根据强度筛选逻辑实现
            pass
        
        # TODO: 实现三维条件的具体筛选逻辑
        # 这里需要根据threeDimensional参数进行复杂的筛选
        
        return filtered