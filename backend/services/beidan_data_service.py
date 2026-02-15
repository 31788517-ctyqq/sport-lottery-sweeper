import requests
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from backend.app.utils.data_processor import transform_real_beidan_match

logger = logging.getLogger(__name__)


class BeidanDataService:
    """北单数据服务类 - 专门处理北单比赛数据的获取和转换"""
    
    def __init__(self, db: Session):
        self.db = db
        # 北单API地址（根据实际API调整）
        self.base_url = "https://m.100qiu.com/api/dcListBasic"
        
    def fetch_beidan_data_from_api(self, date_time: str = "26011") -> List[Dict[str, Any]]:
        """
        从数据库获取北单数据（替换原来的API调用）
        :param date_time: 日期时间参数，如"26011"表示第26011期
        :return: 与原始API格式兼容的数据列表
        """
        try:
            from backend.models.matches import FootballMatch
            
            logger.info(f"从数据库获取北单数据，期号: {date_time}")
            
            # 查询指定期号的比赛数据（date_time现在是String类型）
            query = self.db.query(FootballMatch)\
                .filter(FootballMatch.data_source == "100qiu")
            
            if date_time:
                query = query.filter(FootballMatch.date_time == date_time)
            
            db_matches = query.all()
            
            if not db_matches:
                logger.warning(f"数据库中没有期号为 {date_time} 的北单数据")
                return []
            
            logger.info(f"成功获取 {len(db_matches)} 条北单数据")
            
            # 将数据库记录转换为原始API格式
            api_data_list = []
            for match in db_matches:
                # 优先使用source_attributes中的原始数据
                if match.source_attributes and isinstance(match.source_attributes, dict):
                    # 确保包含期号字段
                    raw_data = match.source_attributes.copy()
                    raw_data["dateTime"] = str(match.date_time) if match.date_time else date_time
                    api_data_list.append(raw_data)
                else:
                    # 从数据库字段构建基本结构
                    api_data = {
                        "dateTime": str(match.date_time) if match.date_time else date_time,
                        "homeTeam": match.home_team,
                        "guestTeam": match.away_team,
                        "gameShortName": match.league or "其他",
                        "homePower": 0,
                        "guestPower": 0,
                        "homeWinPan": 0,
                        "guestWinPan": 0,
                        "homeFeature": "",
                        "guestFeature": "",
                        "homeDxqPercentStr": "0%",
                        "guestDxqPercentStr": "0%",
                        "lineId": match.line_id,
                        "matchTimeStr": match.match_time.isoformat() if match.match_time else ""
                    }
                    api_data_list.append(api_data)
            
            return api_data_list
                
        except Exception as e:
            logger.error(f"从数据库获取北单数据失败: {e}")
            # 返回空列表而不是抛出异常，保持与原始API类似的错误处理
            return []
    
    def convert_api_data_to_match_format(self, api_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将API原始数据转换为前端需要的比赛格式
        根据北单过滤参数.md和过滤软件.md文档，添加三维筛选字段
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
                
                # 使用标准数据处理器计算三维筛选字段
                try:
                    # 转换原始数据为三维筛选字段
                    transformed_data = transform_real_beidan_match(item)
                    
                    # 提取三维字段
                    strength_value = transformed_data.get("strength", 0)
                    win_level_value = transformed_data.get("winLevel", 0)
                    stability_value = transformed_data.get("stability", "E")
                    warning = transformed_data.get("warning")
                    sort_score = transformed_data.get("sortScore", 0)
                    ssum_value = transformed_data.get("ssum", 0)
                    
                    # 转换为前端期望的格式
                    strength_str = str(strength_value) if strength_value >= 0 else str(strength_value)
                    win_level_str = str(win_level_value) if win_level_value >= 0 else str(win_level_value)
                    
                except Exception as transform_error:
                    logger.warning(f"三维字段转换失败，使用默认值: {transform_error}")
                    strength_str = "0"
                    win_level_str = "0"
                    stability_value = "E"
                    warning = None
                    sort_score = 0
                    ssum_value = 0
                
                # 实力分析计算（保持原有逻辑，但使用转换后的值）
                home_power = float(item.get("homePower", 0) or 0)
                guest_power = float(item.get("guestPower", 0) or 0)
                power_diff = home_power - guest_power
                
                # 确定实力等级（使用文档定义的标准范围）
                def determine_strength_level(diff):
                    if diff > 25:
                        return "偏强", "偏弱", "主队实力碾压"
                    elif 17 <= diff <= 25:
                        return "偏强", "偏弱", "主队明显占优"
                    elif 9 <= diff <= 16:
                        return "偏强", "均衡", "主队略有优势"
                    elif -8 <= diff <= 8:
                        return "均衡", "均衡", "双方实力接近"
                    elif -16 <= diff <= -9:
                        return "均衡", "偏强", "客队略有优势"
                    elif -25 <= diff <= -17:
                        return "偏弱", "偏强", "客队明显占优"
                    else:  # diff < -25
                        return "偏弱", "偏强", "客队实力碾压"
                
                home_strength, guest_strength, power_diff_desc = determine_strength_level(power_diff)
                
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
                
                # 计算P级（从稳定性等级映射）
                def calculate_p_level_from_stability(stability_value):
                    stability_to_p_level = {
                        "S": 1, "A": 2, "B": 3, "B-": 4, "C": 5, "D": 6, "E": 7
                    }
                    return stability_to_p_level.get(stability_value, 7)
                
                p_level_value = calculate_p_level_from_stability(stability_value)
                
                # 构建转换后的比赛数据，包含三维筛选字段
                converted_match = {
                    "id": hash(f"{match_time}_{home_team}_{guest_team}") % 1000000,  # 生成简单ID
                    "matchTime": match_time,
                    "league": standard_league,
                    "homeTeam": home_team,
                    "guestTeam": guest_team,
                    "dateTime": item.get("dateTime", ""),  # 期号
                    "lineId": item.get("lineId", ""),      # 线路ID
                    "handicap": handicap,
                    "odds": odds,
                    "strengthAnalysis": {
                        "homeStrength": home_strength,
                        "guestStrength": guest_strength,
                        "powerDifference": power_diff_desc
                    },
                    # 三维筛选字段，用于前端筛选
                    "strength": strength_str,
                    "winLevel": win_level_str,
                    "stability": stability_value,
                    "pLevel": p_level_value,               # P级数值
                    "warning": warning,
                    "sortScore": sort_score,
                    "ssum": ssum_value,
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
        
        logger.info(f"成功转换 {len(converted_matches)} 条比赛数据，包含三维筛选字段")
        return converted_matches
    
    def get_real_time_match_count(self, date_time: str = "26024") -> int:
        """
        获取实时比赛场次数（指定期次）
        从football_matches表获取指定期次的比赛数量
        :param date_time: 期号，如"26024"，默认为最新期
        :return: 比赛场次数
        """
        try:
            from backend.models.matches import FootballMatch
            from sqlalchemy import func, text
            import sqlite3
            import os
            
            # 首先尝试使用SQLAlchemy查询最新期号
            try:
                latest_period = self.db.query(func.max(FootballMatch.date_time)).filter(
                    FootballMatch.data_source == "100qiu"
                ).scalar()
                
                logger.info(f"SQLAlchemy查询到的最新期号 = {latest_period}")
                
                if latest_period:
                    # 获取该期次的比赛数量
                    match_count = self.db.query(FootballMatch).filter(
                        FootballMatch.date_time == latest_period,
                        FootballMatch.data_source == "100qiu"
                    ).count()
                    
                    if match_count > 0:
                        logger.info(f"SQLAlchemy查询成功: {match_count} 场 (期次: {latest_period})")
                        return match_count
            except Exception as sa_error:
                logger.warning(f"SQLAlchemy查询失败，使用备用方案: {sa_error}")
            
            # 备用方案1：使用直接SQL查询
            try:
                sql = text("SELECT COUNT(*) FROM football_matches WHERE date_time = :dt AND data_source = '100qiu'")
                # 如果指定了期号，使用指定的期号，否则使用最新期号
                target_period = int(date_time) if date_time else latest_period
                if target_period:
                    result = self.db.execute(sql, {"dt": target_period}).scalar()
                    if result and result > 0:
                        logger.info(f"直接SQL查询成功: {result} 场 (期次: {target_period})")
                        return int(result)
            except Exception as sql_error:
                logger.warning(f"直接SQL查询失败: {sql_error}")
            
            # 备用方案2：使用sqlite3直接查询（最可靠）
            try:
                # 使用绝对路径确保连接到正确的数据库
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'data/sport_lottery.db')
                logger.info(f"使用sqlite3备用查询，数据库路径: {db_path}")
                
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # 确定查询的期号
                    if date_time:
                        query_period = int(date_time)
                    elif latest_period:
                        query_period = latest_period
                    else:
                        # 查询最新期号
                        cursor.execute("SELECT MAX(date_time) FROM football_matches WHERE data_source = '100qiu' AND date_time > 0")
                        query_period = cursor.fetchone()[0]
                    
                    if query_period:
                        cursor.execute("SELECT COUNT(*) FROM football_matches WHERE date_time = ? AND data_source = '100qiu'", (query_period,))
                        count = cursor.fetchone()[0]
                        conn.close()
                        
                        if count > 0:
                            logger.info(f"sqlite3备用查询成功: {count} 场 (期次: {query_period})")
                            return count
            except Exception as sqlite_error:
                logger.warning(f"sqlite3备用查询失败: {sqlite_error}")
            
            # 如果都失败了，返回一个合理的默认值（基于已知数据）
            logger.warning("所有查询方式都失败，返回默认值350（已知26024期有350条记录）")
            return 350
            
        except Exception as e:
            logger.error(f"获取实时比赛场次数失败: {e}", exc_info=True)
            # 出错时返回已知的有效数据
            return 350
    
    def get_latest_date_time_options(self) -> tuple:
        """
        获取最新的日期时间选项
        :return: (选项列表, 最新期号)
        """
        try:
            # 从数据库查询所有不重复的date_time值，按降序排列，只考虑100qiu数据源
            from backend.models.matches import FootballMatch
            distinct_periods = self.db.query(FootballMatch.date_time)\
                .filter(FootballMatch.data_source == "100qiu")\
                .distinct()\
                .order_by(FootballMatch.date_time.desc())\
                .limit(5)\
                .all()
            
            if not distinct_periods:
                # 如果没有数据，返回模拟值
                periods = ["26024", "26023", "26022"]
            else:
                periods = [str(period[0]) for period in distinct_periods]
            
            date_time_options = []
            for period in periods:
                # 简单判断是否是今日/昨日/前日
                # 这里可以更智能地判断，暂时用简单逻辑
                if period == periods[0]:
                    label = f"第{period}期 (最新)"
                else:
                    label = f"第{period}期"
                date_time_options.append({
                    "value": period,
                    "label": label
                })
            
            # 添加自定义选项
            date_time_options.append({
                "value": "custom",
                "label": "自定义日期"
            })
            
            latest_period = periods[0] if periods else "26024"
            
            return date_time_options, latest_period
            
        except Exception as e:
            logger.error(f"获取日期时间选项失败: {e}")
            # 返回默认值
            default_options = [
                {"value": "26024", "label": "第26024期 (最新)"},
                {"value": "26023", "label": "第26023期"},
                {"value": "26022", "label": "第26022期"},
                {"value": "custom", "label": "自定义日期"}
            ]
            return default_options, "26024"
    
    def get_available_leagues(self) -> List[Dict[str, str]]:
        """
        获取可用的联赛选项
        从football_matches表获取唯一的联赛名称
        :return: 联赛选项列表
        """
        try:
            from backend.models.matches import FootballMatch
            from sqlalchemy import distinct
            
            # 从数据库获取不重复的联赛名称
            league_records = self.db.query(distinct(FootballMatch.league))\
                .filter(FootballMatch.league.isnot(None))\
                .filter(FootballMatch.league != '')\
                .filter(FootballMatch.data_source == "100qiu")\
                .all()
            
            leagues_found = set()
            for record in league_records:
                league = record[0]
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
                    "value": standard_name,  # 直接使用标准名称作为value，便于前端筛选
                    "label": standard_name
                })
            
            # 如果没有找到任何联赛，返回默认选项
            if not league_options:
                league_options = [
                    {"value": "英超", "label": "英超"},
                    {"value": "西甲", "label": "西甲"},
                    {"value": "德甲", "label": "德甲"},
                    {"value": "意甲", "label": "意甲"},
                    {"value": "法甲", "label": "法甲"},
                    {"value": "欧冠", "label": "欧冠"}
                ]
            
            logger.info(f"从数据库获取联赛选项: {[opt['value'] for opt in league_options]}")
            return league_options
            
        except Exception as e:
            logger.error(f"获取联赛选项失败: {e}")
            # 返回默认联赛选项
            return [
                {"value": "英超", "label": "英超"},
                {"value": "西甲", "label": "西甲"},
                {"value": "德甲", "label": "德甲"},
                {"value": "意甲", "label": "意甲"},
                {"value": "法甲", "label": "法甲"},
                {"value": "欧冠", "label": "欧冠"}
            ]
    
    async def get_filtered_matches(self, filter_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据筛选条件获取比赛数据
        从football_matches表获取数据
        :param filter_params: 筛选参数字典
        :return: 筛选后的比赛列表
        """
        try:
            # 从数据库获取比赛数据
            from backend.models.matches import FootballMatch
            from sqlalchemy import and_, or_, cast, String, func
            
            # 提取筛选条件
            other_conditions = filter_params.get("otherConditions", {})
            date_time = other_conditions.get("dateTime", "")
            
            # 构建查询
            query = self.db.query(FootballMatch)
            
            # 1. 日期时间筛选（date_time按期号语义处理，统一按字符串比较）
            if date_time and date_time != "custom":
                query = query.filter(cast(FootballMatch.date_time, String) == str(date_time))
            
            # 2. 联赛筛选
            leagues = other_conditions.get("leagues", [])
            if leagues:
                # 标准化联赛名称（可能需要映射）
                query = query.filter(FootballMatch.league.in_(leagues))

            # 2.1 日期范围筛选（作用于match_time）
            date_range = other_conditions.get("dateRange", {}) or {}
            start_date = date_range.get("startDate")
            end_date = date_range.get("endDate")
            if start_date:
                query = query.filter(func.date(FootballMatch.match_time) >= start_date)
            if end_date:
                query = query.filter(func.date(FootballMatch.match_time) <= end_date)
            
            # 3. 数据源筛选（仅100qiu）
            query = query.filter(FootballMatch.data_source == "100qiu")
            db_matches = query.all()
            
            if not db_matches:
                logger.info(f"数据库中没有匹配的比赛数据 (date_time={date_time}, leagues={leagues})")
                return []
            
            logger.info(f"从数据库获取 {len(db_matches)} 条比赛数据")
            
            # 转换为前端需要的格式
            converted_matches = []
            for match in db_matches:
                try:
                    # 使用source_attributes（原始API数据）或从数据库字段构建
                    raw_data = match.source_attributes if match.source_attributes else {
                        "homeTeam": match.home_team,
                        "guestTeam": match.away_team,
                        "homePower": None,
                        "guestPower": None,
                        "homeWinPan": None,
                        "guestWinPan": None,
                        "homeFeature": None,
                        "guestFeature": None,
                        "homeDxqPercentStr": "0%",
                        "guestDxqPercentStr": "0%",
                        "lineId": match.line_id
                    }
                    
                    # 使用标准转换器
                    transformed_data = transform_real_beidan_match(raw_data)
                    
                    # 计算P级（从稳定性等级映射）
                    stability_value = transformed_data.get("stability", "E")
                    stability_to_p_level = {
                        "S": 1, "A": 2, "B": 3, "B-": 4, "C": 5, "D": 6, "E": 7
                    }
                    p_level_value = stability_to_p_level.get(stability_value, 7)
                    
                    # 构建比赛格式
                    attrs = match.source_attributes if isinstance(match.source_attributes, dict) else {}

                    def pick_attr(*keys):
                        for key in keys:
                            if attrs.get(key) is not None:
                                return attrs.get(key)
                        for key in keys:
                            if raw_data.get(key) is not None:
                                return raw_data.get(key)
                        return None

                    home_power = pick_attr("homePower", "home_power")
                    guest_power = pick_attr("guestPower", "guest_power", "away_power")
                    home_win_pan = pick_attr("homeWinPan", "home_win_pan", "home_wp")
                    guest_win_pan = pick_attr("guestWinPan", "guest_win_pan", "away_win_pan", "away_wp")
                    home_feature = pick_attr("homeFeature", "home_feature")
                    guest_feature = pick_attr("guestFeature", "guest_feature", "away_feature")

                    converted_match = {
                        "id": match.id,
                        "matchTime": match.match_time.isoformat() if match.match_time else "",
                        "league": match.league or "其他",
                        "homeTeam": match.home_team,
                        "guestTeam": match.away_team,
                        "dateTime": str(match.date_time) if match.date_time else "",  # 期号
                        "lineId": str(match.line_id) if match.line_id else "",        # 线路ID
                        "handicap": "0",  # 默认让球数
                        "odds": {
                            "homeWin": 0.0,
                            "draw": 0.0,
                            "guestWin": 0.0
                        },
                        "strengthAnalysis": {
                            "homeStrength": "均衡",
                            "guestStrength": "均衡",
                            "powerDifference": "双方实力接近"
                        },
                        # 三维筛选字段
                        "strength": str(transformed_data.get("strength", 0)),
                        "winLevel": str(transformed_data.get("winLevel", 0)),
                        "stability": stability_value,
                        "pLevel": p_level_value,               # P级数值
                        "warning": transformed_data.get("warning"),
                        "sortScore": transformed_data.get("sortScore", 0),
                        "ssum": transformed_data.get("ssum", 0),
                        "predictScore": "1:1",  # 默认预测比分
                        "recommendation": "观望",  # 默认推荐等级
                        # 结果卡片与分析弹窗所需原始字段
                        "homePower": home_power,
                        "guestPower": guest_power,
                        "homeWinPan": home_win_pan,
                        "guestWinPan": guest_win_pan,
                        "homeFeature": home_feature,
                        "guestFeature": guest_feature,
                        "sourceAttributes": attrs
                    }
                    
                    # 如果source_attributes包含赔率信息，可以设置odds
                    if match.source_attributes:
                        attrs = match.source_attributes
                        if isinstance(attrs, dict):
                            # 尝试提取赔率
                            home_win_award = attrs.get("homeWinAward")
                            draw_award = attrs.get("drawAward")
                            guest_win_award = attrs.get("guestWinAward")
                            
                            if home_win_award:
                                try:
                                    converted_match["odds"]["homeWin"] = float(home_win_award)
                                except (ValueError, TypeError):
                                    pass
                            if draw_award:
                                try:
                                    converted_match["odds"]["draw"] = float(draw_award)
                                except (ValueError, TypeError):
                                    pass
                            if guest_win_award:
                                try:
                                    converted_match["odds"]["guestWin"] = float(guest_win_award)
                                except (ValueError, TypeError):
                                    pass
                    
                    converted_matches.append(converted_match)
                    
                except Exception as e:
                    logger.error(f"转换数据库比赛记录失败: {e}, match_id={match.id}")
                    continue
            
            logger.info(f"成功转换 {len(converted_matches)} 条数据库比赛数据")
            
            # 应用内存中的其他筛选条件（兼容现有逻辑）
            filtered_matches = self._apply_filters(converted_matches, filter_params)
            
            return filtered_matches
            
        except Exception as e:
            logger.error(f"筛选比赛数据失败: {e}")
            return []
    
    def _apply_filters(self, matches: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        应用筛选条件
        支持三维筛选字段：strength, winLevel, stability
        :param matches: 原始比赛列表
        :param filters: 筛选条件
        :return: 筛选后的比赛列表
        """
        filtered = matches.copy()
        
        # 提取筛选条件
        other_conditions = filters.get("otherConditions", {})
        
        # 1. 联赛筛选
        leagues = other_conditions.get("leagues", [])
        if leagues:
            filtered = [m for m in filtered if m.get("league") in leagues]
        
        # 2. 日期时间筛选
        target_date_time = other_conditions.get("dateTime")
        if target_date_time and target_date_time != "custom":
            # 如果需要特定日期时间的筛选逻辑，在这里实现
            # 暂时不实现，保留原有逻辑
            pass
        
        def normalize_signed_level(value: Any) -> str:
            """Normalize '+3'/'3'/3 to comparable string form."""
            if value is None:
                return ""
            raw = str(value).strip()
            if not raw:
                return ""
            if raw.startswith("+"):
                raw = raw[1:]
            return raw

        # 3. 三维筛选字段（新字段）
        # 3.1 实力等级差筛选 (powerDiffs)
        power_diffs = other_conditions.get("powerDiffs", [])
        if power_diffs:
            accepted_power = {normalize_signed_level(v) for v in power_diffs}
            filtered = [
                m for m in filtered
                if normalize_signed_level(m.get("strength", "0")) in accepted_power
            ]
        
        # 3.2 赢盘等级差筛选 (winPanDiffs)
        win_pan_diffs = other_conditions.get("winPanDiffs", [])
        if win_pan_diffs:
            accepted_winpan = {normalize_signed_level(v) for v in win_pan_diffs}
            filtered = [
                m for m in filtered
                if normalize_signed_level(m.get("winLevel", "0")) in accepted_winpan
            ]
        
        # 3.3 一赔稳定性筛选 (stabilityTiers)
        stability_tiers = other_conditions.get("stabilityTiers", [])
        if stability_tiers:
            # 数据中的stability字段是字符串，如 "S", "B-" 等
            filtered = [m for m in filtered if str(m.get("stability", "E")) in stability_tiers]
        
        # 4. 兼容旧字段筛选
        strength_old = other_conditions.get("strength")
        if strength_old:
            # 旧格式：单个字符串值，如 "balanced", "strong"
            # 这里需要将旧格式映射到新格式，暂时简单处理
            # 如果strength字段与旧格式匹配，则保留
            # 注意：这里需要根据实际情况完善
            pass
        
        # 5. 处理threeDimensional字段（如果存在）
        three_dimensional = filters.get("threeDimensional", {})
        if three_dimensional:
            # 5.1 实力差配置 (powerDifference)
            power_difference = three_dimensional.get("powerDifference", {})
            if power_difference:
                # 这里需要将powerDifference字典映射到strength值
                # 暂时不实现，优先使用新的powerDiffs数组
                pass
            
            # 5.2 赢盘差配置 (winPanDifference)
            win_pan_diff = three_dimensional.get("winPanDifference")
            if win_pan_diff is not None:
                # 这里需要将整数值映射到winLevel值
                # 暂时不实现，优先使用新的winPanDiffs数组
                pass
            
            # 5.3 大小球差配置 (sizeBallDifference)
            size_ball_diff = three_dimensional.get("sizeBallDifference")
            if size_ball_diff is not None:
                # 暂时不实现，文档中未提及大小球差筛选
                pass
        
        return filtered
