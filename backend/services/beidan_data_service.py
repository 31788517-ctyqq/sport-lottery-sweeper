import requests
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import re
import json
from sqlalchemy import func
from backend.app.utils.data_processor import transform_real_beidan_match



logger = logging.getLogger(__name__)


def json_attr_text_expr(session: Session, column, key: str):
    """Extract a JSON text attribute in a dialect-safe way."""
    dialect_name = ((session.bind.dialect.name if session.bind and session.bind.dialect else "") or "").lower()
    if dialect_name.startswith("postgres"):
        return column.op("->>")(key)
    return func.json_extract(column, f"$.{key}")


_BD_ISSUE_DATES_CACHE: Dict[str, List[str]] = {}


def _normalize_bd_issue_no(value: Any) -> str:
    text = str(value or "").strip()
    m = re.search(r"(\d{5})", text)
    return m.group(1) if m else ""


def _fetch_500_bd_issue_dates(issue_no: str) -> List[str]:
    """Fetch all source dates covered by one beidan issue from trade.500.com."""
    key = _normalize_bd_issue_no(issue_no)
    if not key:
        return []
    if key in _BD_ISSUE_DATES_CACHE:
        return list(_BD_ISSUE_DATES_CACHE[key])

    url = f"https://trade.500.com/bjdc/?expect={key}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://trade.500.com/bjdc/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            _BD_ISSUE_DATES_CACHE[key] = []
            return []
        html = resp.text or ""
        served = re.search(r'id="expect"[^>]*value="(\d{5})"', html)
        if served and served.group(1) != key:
            # 500 fallback to another issue, ignore this payload
            _BD_ISSUE_DATES_CACHE[key] = []
            return []
        dates = sorted(set(re.findall(r"switch_for_(\d{4}-\d{2}-\d{2})", html)))
        _BD_ISSUE_DATES_CACHE[key] = dates
        return list(dates)
    except Exception as e:
        logger.warning(f"获取500北单期号日期失败(issue={key}): {e}")
        _BD_ISSUE_DATES_CACHE[key] = []
        return []


class BeidanDataService:
    """鍖楀崟鏁版嵁鏈嶅姟绫?- 涓撻棬澶勭悊鍖楀崟姣旇禌鏁版嵁鐨勮幏鍙栧拰杞崲"""
    
    def __init__(self, db: Session):
        self.db = db
        # 鍖楀崟API鍦板潃锛堟牴鎹疄闄匒PI璋冩暣锛?
        self.base_url = "https://m.100qiu.com/api/dcListBasic"
        
    def fetch_beidan_data_from_api(self, date_time: str = "26011") -> List[Dict[str, Any]]:
        """
        浠庢暟鎹簱鑾峰彇鍖楀崟鏁版嵁锛堟浛鎹㈠師鏉ョ殑API璋冪敤锛?
        :param date_time: 鏃ユ湡鏃堕棿鍙傛暟锛屽"26011"琛ㄧず绗?6011鏈?
        :return: 涓庡師濮婣PI鏍煎紡鍏煎鐨勬暟鎹垪琛?
        """
        try:
            from backend.models.matches import FootballMatch
            
            logger.info(f"浠庢暟鎹簱鑾峰彇鍖楀崟鏁版嵁锛屾湡鍙? {date_time}")
            
            # 鏌ヨ鎸囧畾鏈熷彿鐨勬瘮璧涙暟鎹紙date_time鐜板湪鏄疭tring绫诲瀷锛?
            query = self.db.query(FootballMatch)\
                .filter(FootballMatch.data_source == "100qiu")
            
            if date_time:
                query = query.filter(FootballMatch.date_time == date_time)
            
            db_matches = query.all()
            
            if not db_matches:
                logger.warning(f"数据库中没有期号 {date_time} 的北单数据")
                return []
            
            logger.info(f"成功获取 {len(db_matches)} 条北单数据")
            
            # 灏嗘暟鎹簱璁板綍杞崲涓哄師濮婣PI鏍煎紡
            api_data_list = []
            for match in db_matches:
                # 浼樺厛浣跨敤source_attributes涓殑鍘熷鏁版嵁
                if match.source_attributes and isinstance(match.source_attributes, dict):
                    # 纭繚鍖呭惈鏈熷彿瀛楁
                    raw_data = match.source_attributes.copy()
                    raw_data["dateTime"] = str(match.date_time) if match.date_time else date_time
                    api_data_list.append(raw_data)
                else:
                    # 浠庢暟鎹簱瀛楁鏋勫缓鍩烘湰缁撴瀯
                    api_data = {
                        "dateTime": str(match.date_time) if match.date_time else date_time,
                        "homeTeam": match.home_team,
                        "guestTeam": match.away_team,
                        "gameShortName": match.league or "鍏朵粬",
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
            logger.error(f"浠庢暟鎹簱鑾峰彇鍖楀崟鏁版嵁澶辫触: {e}")
            # 杩斿洖绌哄垪琛ㄨ€屼笉鏄姏鍑哄紓甯革紝淇濇寔涓庡師濮婣PI绫讳技鐨勯敊璇鐞?
            return []
    
    def convert_api_data_to_match_format(self, api_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        灏咥PI鍘熷鏁版嵁杞崲涓哄墠绔渶瑕佺殑姣旇禌鏍煎紡
        鏍规嵁鍖楀崟杩囨护鍙傛暟.md鍜岃繃婊よ蒋浠?md鏂囨。锛屾坊鍔犱笁缁寸瓫閫夊瓧娈?
        :param api_data: API杩斿洖鐨勫師濮嬫暟鎹?
        :return: 杞崲鍚庣殑姣旇禌鏁版嵁鍒楄〃
        """
        converted_matches = []
        
        for item in api_data:
            try:
                # 鍩虹淇℃伅杞崲
                match_time = item.get("matchTimeStr", "")
                if not match_time:
                    continue
                    
                # 闃熶紞淇℃伅澶勭悊
                home_team = item.get("homeTeam", "").strip()
                guest_team = item.get("guestTeam", "").strip()
                
                if not home_team or not guest_team:
                    continue
                
                # 鑱旇禌淇℃伅澶勭悊
                league = item.get("gameShortName", "鍏朵粬")
                # 鏍囧噯鍖栬仈璧涘悕绉?
                league_mapping = {
                    "鑻辫秴": "鑻辫秴",
                    "瑗跨敳": "瑗跨敳", 
                    "寰风敳": "寰风敳",
                    "鎰忕敳": "鎰忕敳",
                    "娉曠敳": "娉曠敳",
                    "娆у啝": "娆у啝",
                    "世界杯": "世界杯",
                }
                standard_league = league_mapping.get(league, "鍏朵粬")
                
                # 浣跨敤鏍囧噯鏁版嵁澶勭悊鍣ㄨ绠椾笁缁寸瓫閫夊瓧娈?
                try:
                    # 杞崲鍘熷鏁版嵁涓轰笁缁寸瓫閫夊瓧娈?
                    transformed_data = transform_real_beidan_match(item)
                    
                    # 鎻愬彇涓夌淮瀛楁
                    strength_value = transformed_data.get("strength", 0)
                    win_level_value = transformed_data.get("winLevel", 0)
                    stability_value = transformed_data.get("stability", "E")
                    warning = transformed_data.get("warning")
                    sort_score = transformed_data.get("sortScore", 0)
                    ssum_value = transformed_data.get("ssum", 0)
                    
                    # 杞崲涓哄墠绔湡鏈涚殑鏍煎紡
                    strength_str = str(strength_value) if strength_value >= 0 else str(strength_value)
                    win_level_str = str(win_level_value) if win_level_value >= 0 else str(win_level_value)
                    
                except Exception as transform_error:
                    logger.warning(f"涓夌淮瀛楁杞崲澶辫触锛屼娇鐢ㄩ粯璁ゅ€? {transform_error}")
                    strength_str = "0"
                    win_level_str = "0"
                    stability_value = "E"
                    warning = None
                    sort_score = 0
                    ssum_value = 0
                
                # 瀹炲姏鍒嗘瀽璁＄畻锛堜繚鎸佸師鏈夐€昏緫锛屼絾浣跨敤杞崲鍚庣殑鍊硷級
                home_power = float(item.get("homePower", 0) or 0)
                guest_power = float(item.get("guestPower", 0) or 0)
                power_diff = home_power - guest_power
                
                # 纭畾瀹炲姏绛夌骇锛堜娇鐢ㄦ枃妗ｅ畾涔夌殑鏍囧噯鑼冨洿锛?
                def determine_strength_level(diff):
                    if diff > 25:
                        return "鍋忓己", "鍋忓急", "涓婚槦瀹炲姏纰惧帇"
                    elif 17 <= diff <= 25:
                        return "鍋忓己", "鍋忓急", "涓婚槦鏄庢樉鍗犱紭"
                    elif 9 <= diff <= 16:
                        return "鍋忓己", "鍧囪　", "涓婚槦鐣ユ湁浼樺娍"
                    elif -8 <= diff <= 8:
                        return "鍧囪　", "鍧囪　", "鍙屾柟瀹炲姏鎺ヨ繎"
                    elif -16 <= diff <= -9:
                        return "鍧囪　", "鍋忓己", "瀹㈤槦鐣ユ湁浼樺娍"
                    elif -25 <= diff <= -17:
                        return "鍋忓急", "鍋忓己", "瀹㈤槦鏄庢樉鍗犱紭"
                    else:  # diff < -25
                        return "鍋忓急", "鍋忓己", "瀹㈤槦瀹炲姏纰惧帇"
                
                home_strength, guest_strength, power_diff_desc = determine_strength_level(power_diff)
                
                # 璧旂巼淇℃伅澶勭悊
                home_win_award = item.get("homeWinAward", "")
                guest_win_award = item.get("guestWinAward", "")
                draw_award = item.get("drawAward", "")
                
                # 杞崲璧旂巼涓烘诞鐐规暟
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
                
                # 璁╃悆鏁板鐞?
                handicap = "0"  # 榛樿璁╃悆鏁颁负0
                
                # 棰勬祴姣斿垎锛堝熀浜庡疄鍔涘垎鏋愮畝鍗曟帹绠楋級
                if abs(power_diff) >= 10:
                    if power_diff > 0:
                        predict_score = "2:0" if power_diff >= 20 else "2:1"
                    else:
                        predict_score = "0:2" if power_diff <= -20 else "1:2"
                else:
                    predict_score = "1:1"
                
                # 鎺ㄨ崘绛夌骇
                if abs(power_diff) >= 15:
                    recommendation = "閲嶇偣鍏虫敞"
                elif abs(power_diff) >= 8:
                    recommendation = "鍊煎緱鍏虫敞"
                else:
                    recommendation = "瑙傛湜"
                
                # 璁＄畻P绾э紙浠庣ǔ瀹氭€х瓑绾ф槧灏勶級
                def calculate_p_level_from_stability(stability_value):
                    stability_to_p_level = {
                        "S": 1, "A": 2, "B": 3, "B-": 4, "C": 5, "D": 6, "E": 7
                    }
                    return stability_to_p_level.get(stability_value, 7)
                
                p_level_value = calculate_p_level_from_stability(stability_value)
                
                # 鏋勫缓杞崲鍚庣殑姣旇禌鏁版嵁锛屽寘鍚笁缁寸瓫閫夊瓧娈?
                converted_match = {
                    "id": hash(f"{match_time}_{home_team}_{guest_team}") % 1000000,  # 鐢熸垚绠€鍗旾D
                    "matchTime": match_time,
                    "league": standard_league,
                    "homeTeam": home_team,
                    "guestTeam": guest_team,
                    "dateTime": item.get("dateTime", ""),  # 鏈熷彿
                    "lineId": item.get("lineId", ""),      # 绾胯矾ID
                    "handicap": handicap,
                    "odds": odds,
                    "strengthAnalysis": {
                        "homeStrength": home_strength,
                        "guestStrength": guest_strength,
                        "powerDifference": power_diff_desc
                    },
                    # 涓夌淮绛涢€夊瓧娈碉紝鐢ㄤ簬鍓嶇绛涢€?
                    "strength": strength_str,
                    "winLevel": win_level_str,
                    "stability": stability_value,
                    "pLevel": p_level_value,               # P绾ф暟鍊?
                    "warning": warning,
                    "sortScore": sort_score,
                    "ssum": ssum_value,
                    "predictScore": predict_score,
                    "recommendation": recommendation,
                    # 淇濈暀鍘熷鏁版嵁鐢ㄤ簬鍚庣画鍒嗘瀽
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
                logger.error(f"杞崲姣旇禌鏁版嵁澶辫触: {e}, 鏁版嵁: {item}")
                continue
        
        logger.info(f"成功转换 {len(converted_matches)} 条比赛数据，包含三维筛选字段")
        return converted_matches
    
    def get_real_time_match_count(self, date_time: str = "26024") -> int:
        """
        鑾峰彇瀹炴椂姣旇禌鍦烘鏁帮紙鎸囧畾鏈熸锛?
        浠巉ootball_matches琛ㄨ幏鍙栨寚瀹氭湡娆＄殑姣旇禌鏁伴噺
        :param date_time: 鏈熷彿锛屽"26024"锛岄粯璁や负鏈€鏂版湡
        :return: 姣旇禌鍦烘鏁?
        """
        try:
            from backend.models.matches import FootballMatch
            from sqlalchemy import func, text
            import sqlite3
            import os
            
            # 棣栧厛灏濊瘯浣跨敤SQLAlchemy鏌ヨ鏈€鏂版湡鍙?
            try:
                latest_period = self.db.query(func.max(FootballMatch.date_time)).filter(
                    FootballMatch.data_source == "100qiu"
                ).scalar()
                
                logger.info(f"SQLAlchemy鏌ヨ鍒扮殑鏈€鏂版湡鍙?= {latest_period}")
                
                if latest_period:
                    # 鑾峰彇璇ユ湡娆＄殑姣旇禌鏁伴噺
                    match_count = self.db.query(FootballMatch).filter(
                        FootballMatch.date_time == latest_period,
                        FootballMatch.data_source == "100qiu"
                    ).count()
                    
                    if match_count > 0:
                        logger.info(f"SQLAlchemy鏌ヨ鎴愬姛: {match_count} 鍦?(鏈熸: {latest_period})")
                        return match_count
            except Exception as sa_error:
                logger.warning(f"SQLAlchemy鏌ヨ澶辫触锛屼娇鐢ㄥ鐢ㄦ柟妗? {sa_error}")
            
            # 澶囩敤鏂规1锛氫娇鐢ㄧ洿鎺QL鏌ヨ
            try:
                sql = text("SELECT COUNT(*) FROM football_matches WHERE date_time = :dt AND data_source = '100qiu'")
                # 如果指定了期号，使用指定期号，否则使用最新期号
                target_period = int(date_time) if date_time else latest_period
                if target_period:
                    result = self.db.execute(sql, {"dt": target_period}).scalar()
                    if result and result > 0:
                        logger.info(f"鐩存帴SQL鏌ヨ鎴愬姛: {result} 鍦?(鏈熸: {target_period})")
                        return int(result)
            except Exception as sql_error:
                logger.warning(f"鐩存帴SQL鏌ヨ澶辫触: {sql_error}")
            
            # 澶囩敤鏂规2锛氫娇鐢╯qlite3鐩存帴鏌ヨ锛堟渶鍙潬锛?
            try:
                # 浣跨敤缁濆璺緞纭繚杩炴帴鍒版纭殑鏁版嵁搴?
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'data/sport_lottery.db')
                logger.info(f"浣跨敤sqlite3澶囩敤鏌ヨ锛屾暟鎹簱璺緞: {db_path}")
                
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # 纭畾鏌ヨ鐨勬湡鍙?
                    if date_time:
                        query_period = int(date_time)
                    elif latest_period:
                        query_period = latest_period
                    else:
                        # 鏌ヨ鏈€鏂版湡鍙?
                        cursor.execute("SELECT MAX(date_time) FROM football_matches WHERE data_source = '100qiu' AND date_time > 0")
                        query_period = cursor.fetchone()[0]
                    
                    if query_period:
                        cursor.execute("SELECT COUNT(*) FROM football_matches WHERE date_time = ? AND data_source = '100qiu'", (query_period,))
                        count = cursor.fetchone()[0]
                        conn.close()
                        
                        if count > 0:
                            logger.info(f"sqlite3澶囩敤鏌ヨ鎴愬姛: {count} 鍦?(鏈熸: {query_period})")
                            return count
            except Exception as sqlite_error:
                logger.warning(f"sqlite3澶囩敤鏌ヨ澶辫触: {sqlite_error}")
            
            # 濡傛灉閮藉け璐ヤ簡锛岃繑鍥炰竴涓悎鐞嗙殑榛樿鍊硷紙鍩轰簬宸茬煡鏁版嵁锛?
            logger.warning("鎵€鏈夋煡璇㈡柟寮忛兘澶辫触锛岃繑鍥為粯璁ゅ€?50锛堝凡鐭?6024鏈熸湁350鏉¤褰曪級")
            return 350
            
        except Exception as e:
            logger.error(f"鑾峰彇瀹炴椂姣旇禌鍦烘鏁板け璐? {e}", exc_info=True)
            # 鍑洪敊鏃惰繑鍥炲凡鐭ョ殑鏈夋晥鏁版嵁
            return 350
    
    def get_latest_date_time_options(self) -> tuple:
        """
        鑾峰彇鏈€鏂扮殑鏃ユ湡鏃堕棿閫夐」
        :return: (閫夐」鍒楄〃, 鏈€鏂版湡鍙?
        """
        try:
            # 浠庢暟鎹簱鏌ヨ鎵€鏈変笉閲嶅鐨刣ate_time鍊硷紝鎸夐檷搴忔帓鍒楋紝鍙€冭檻100qiu鏁版嵁婧?
            from backend.models.matches import FootballMatch
            distinct_periods = self.db.query(FootballMatch.date_time)\
                .filter(FootballMatch.data_source == "100qiu")\
                .distinct()\
                .order_by(FootballMatch.date_time.desc())\
                .limit(5)\
                .all()
            
            if not distinct_periods:
                # 濡傛灉娌℃湁鏁版嵁锛岃繑鍥炴ā鎷熷€?
                periods = ["26024", "26023", "26022"]
            else:
                periods = [str(period[0]) for period in distinct_periods]
            
            date_time_options = []
            for period in periods:
                # 绠€鍗曞垽鏂槸鍚︽槸浠婃棩/鏄ㄦ棩/鍓嶆棩
                # 杩欓噷鍙互鏇存櫤鑳藉湴鍒ゆ柇锛屾殏鏃剁敤绠€鍗曢€昏緫
                if period == periods[0]:
                    label = f"第{period}期(最新)"
                else:
                    label = f"第{period}期"
                date_time_options.append({
                    "value": period,
                    "label": label
                })
            
            # 娣诲姞鑷畾涔夐€夐」
            date_time_options.append({
                "value": "custom",
                "label": "自定义日期"
            })
            
            latest_period = periods[0] if periods else "26024"
            
            return date_time_options, latest_period
            
        except Exception as e:
            logger.error(f"鑾峰彇鏃ユ湡鏃堕棿閫夐」澶辫触: {e}")
            # 杩斿洖榛樿鍊?
            default_options = [
                {"value": "26024", "label": "第26024期(最新)"},
                {"value": "26023", "label": "第26023期"},
                {"value": "26022", "label": "第26022期"},
                {"value": "custom", "label": "自定义日期"}
            ]
            return default_options, "26024"
    
    def get_available_leagues(self) -> List[Dict[str, str]]:
        """
        鑾峰彇鍙敤鐨勮仈璧涢€夐」
        浠巉ootball_matches琛ㄨ幏鍙栧敮涓€鐨勮仈璧涘悕绉?
        :return: 鑱旇禌閫夐」鍒楄〃
        """
        try:
            from backend.models.matches import FootballMatch
            from sqlalchemy import distinct
            
            # 浠庢暟鎹簱鑾峰彇涓嶉噸澶嶇殑鑱旇禌鍚嶇О
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
            
            # 鏍囧噯鍖栬仈璧涘悕绉板苟鏋勫缓閫夐」
            league_mapping = {
                "鑻辫秴": "鑻辫秴",
                "瑗跨敳": "瑗跨敳",
                "寰风敳": "寰风敳", 
                "鎰忕敳": "鎰忕敳",
                "娉曠敳": "娉曠敳",
                "娆у啝": "娆у啝",
                "世界杯": "世界杯",
                "涓秴": "涓秴",
                "J鑱旇禌": "J鑱旇禌",
                "K鑱旇禌": "K鑱旇禌"
            }
            
            league_options = []
            for league in sorted(leagues_found):
                standard_name = league_mapping.get(league, league)
                league_options.append({
                    "value": standard_name,  # 鐩存帴浣跨敤鏍囧噯鍚嶇О浣滀负value锛屼究浜庡墠绔瓫閫?
                    "label": standard_name
                })
            
            # 濡傛灉娌℃湁鎵惧埌浠讳綍鑱旇禌锛岃繑鍥為粯璁ら€夐」
            if not league_options:
                league_options = [
                    {"value": "鑻辫秴", "label": "鑻辫秴"},
                    {"value": "瑗跨敳", "label": "瑗跨敳"},
                    {"value": "寰风敳", "label": "寰风敳"},
                    {"value": "鎰忕敳", "label": "鎰忕敳"},
                    {"value": "娉曠敳", "label": "娉曠敳"},
                    {"value": "娆у啝", "label": "娆у啝"}
                ]
            
            logger.info(f"浠庢暟鎹簱鑾峰彇鑱旇禌閫夐」: {[opt['value'] for opt in league_options]}")
            return league_options
            
        except Exception as e:
            logger.error(f"鑾峰彇鑱旇禌閫夐」澶辫触: {e}")
            # 杩斿洖榛樿鑱旇禌閫夐」
            return [
                {"value": "鑻辫秴", "label": "鑻辫秴"},
                {"value": "瑗跨敳", "label": "瑗跨敳"},
                {"value": "寰风敳", "label": "寰风敳"},
                {"value": "鎰忕敳", "label": "鎰忕敳"},
                {"value": "娉曠敳", "label": "娉曠敳"},
                {"value": "娆у啝", "label": "娆у啝"}
            ]
    
    async def get_filtered_matches(self, filter_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        鏍规嵁绛涢€夋潯浠惰幏鍙栨瘮璧涙暟鎹?
        浠巉ootball_matches琛ㄨ幏鍙栨暟鎹?
        :param filter_params: 绛涢€夊弬鏁板瓧鍏?
        :return: 绛涢€夊悗鐨勬瘮璧涘垪琛?
        """
        try:
            # 浠庢暟鎹簱鑾峰彇姣旇禌鏁版嵁
            from backend.models.matches import FootballMatch
            from sqlalchemy import and_, or_, cast, String, func
            
            # 鎻愬彇绛涢€夋潯浠?
            other_conditions = filter_params.get("otherConditions", {})
            date_time = other_conditions.get("dateTime", "")
            
            # 鏋勫缓鏌ヨ
            query = self.db.query(FootballMatch)
            
            # 1. 鏃ユ湡鏃堕棿绛涢€夛紙date_time鎸夋湡鍙疯涔夊鐞嗭紝缁熶竴鎸夊瓧绗︿覆姣旇緝锛?
            if date_time and date_time != "custom":
                query = query.filter(cast(FootballMatch.date_time, String) == str(date_time))
            
            # 2. 鑱旇禌绛涢€?
            leagues = other_conditions.get("leagues", [])
            if leagues:
                # 鏍囧噯鍖栬仈璧涘悕绉帮紙鍙兘闇€瑕佹槧灏勶級
                query = query.filter(FootballMatch.league.in_(leagues))

            # 2.1 鏃ユ湡鑼冨洿绛涢€夛紙浣滅敤浜巑atch_time锛?
            date_range = other_conditions.get("dateRange", {}) or {}
            start_date = date_range.get("startDate")
            end_date = date_range.get("endDate")
            if start_date:
                query = query.filter(func.date(FootballMatch.match_time) >= start_date)
            if end_date:
                query = query.filter(func.date(FootballMatch.match_time) <= end_date)

            # 2.2 场次范围筛选（基于 line_id）
            line_id_start = (
                other_conditions.get("lineIdStart")
                or other_conditions.get("line_id_start")
                or other_conditions.get("start_line_id")
            )
            line_id_end = (
                other_conditions.get("lineIdEnd")
                or other_conditions.get("line_id_end")
                or other_conditions.get("end_line_id")
            )


            def _parse_line_id(value):
                if value is None:
                    return None
                text = str(value).strip()
                if not text:
                    return None
                try:
                    return int(text)
                except Exception:
                    return None

            start_line_num = _parse_line_id(line_id_start)
            end_line_num = _parse_line_id(line_id_end)
            if start_line_num is not None:
                query = query.filter(FootballMatch.line_id >= start_line_num)
            if end_line_num is not None:
                query = query.filter(FootballMatch.line_id <= end_line_num)
            
            # 3. 鏁版嵁婧愮瓫閫夛紙浠?00qiu锛?
            query = query.filter(FootballMatch.data_source == "100qiu")
            db_matches = query.all()

            if not db_matches:
                logger.info(f"鏁版嵁搴撲腑娌℃湁鍖归厤鐨勬瘮璧涙暟鎹?(date_time={date_time}, leagues={leagues})")
                return []
            
            logger.info(f"从数据库获取 {len(db_matches)} 条比赛数据")


            def normalize_attrs(value):
                if isinstance(value, dict):
                    return value
                if isinstance(value, str):
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return {}
                return {}

            def normalize_text_value(value):
                if value is None:
                    return ""
                if isinstance(value, dict):
                    for key in ("text", "label", "name", "value", "statusDes", "status_des", "status"):
                        if key in value and value.get(key) is not None:
                            return normalize_text_value(value.get(key))
                    for nested in value.values():
                        nested_text = normalize_text_value(nested)
                        if nested_text:
                            return nested_text
                    return ""
                if isinstance(value, (list, tuple)):
                    parts = [normalize_text_value(v) for v in value]
                    parts = [p for p in parts if p]
                    return "/".join(parts)
                text = str(value).strip()
                return text

            def normalize_score_value(value):
                text = normalize_text_value(value)
                if not text:
                    return ""
                text = text.replace("：", "-").replace(":", "-")
                m = re.search(r"(\d+)\s*-\s*(\d+)", text)
                if m:
                    return f"{m.group(1)}-{m.group(2)}"
                return text

            def extract_schedule_score_pair(schedule_obj, attrs_obj):
                if schedule_obj.home_score is not None and schedule_obj.away_score is not None:
                    full_score_text = f"{schedule_obj.home_score}-{schedule_obj.away_score}"
                else:
                    full_score_text = normalize_score_value(
                        attrs_obj.get("full_score")
                        or attrs_obj.get("score")
                        or attrs_obj.get("fullScore")
                        or attrs_obj.get("score_full")
                    )

                half_score_text = normalize_score_value(
                    schedule_obj.halftime_score
                    or attrs_obj.get("halftime_score")
                    or attrs_obj.get("half_score")
                    or attrs_obj.get("halfScore")
                    or attrs_obj.get("halftimeScore")
                    or attrs_obj.get("halfTimeScore")
                    or attrs_obj.get("mid_score")
                )
                return full_score_text, half_score_text

            schedule_time_map = {}
            schedule_time_map_by_number = {}
            schedule_time_candidates_by_number = {}
            schedule_score_map = {}
            schedule_score_map_by_number = {}
            schedule_score_candidates_by_number = {}
            schedule_score_map_by_issue = {}
            schedule_score_map_by_issue_number = {}

            try:
                from backend.models.match import Match, Team
                from sqlalchemy.orm import aliased

                match_dates = {m.match_time.date() for m in db_matches if m.match_time}
                match_date_keys = {d.isoformat() for d in match_dates if d}
                issue_no_values = {
                    _normalize_bd_issue_no(m.date_time)
                    for m in db_matches
                    if _normalize_bd_issue_no(m.date_time)
                }
                line_number_values = set()
                for m in db_matches:
                    if m.line_id is None:
                        continue
                    number_text = str(m.line_id).strip()
                    if not number_text:
                        continue
                    line_number_values.add(number_text.lstrip("0") or number_text)
                if match_dates or issue_no_values:
                    HomeTeam = aliased(Team)
                    AwayTeam = aliased(Team)
                    source_date_expr = json_attr_text_expr(self.db, Match.source_attributes, "source_schedule_date")
                    issue_no_expr = json_attr_text_expr(self.db, Match.source_attributes, "issue_no")
                    number_expr = json_attr_text_expr(self.db, Match.source_attributes, "number")

                    issue_date_values = set()
                    for issue_no in issue_no_values:
                        issue_date_values.update(_fetch_500_bd_issue_dates(issue_no))

                    # 500失败时回退：按年度 source_schedule_date 顺序推测该期覆盖日期（取近3天窗口）
                    if not issue_date_values and issue_no_values:
                        year_dates_cache: Dict[int, List[str]] = {}
                        for issue_no in issue_no_values:
                            if not re.fullmatch(r"\d{5}", issue_no):
                                continue
                            yy = int(issue_no[:2])
                            seq = int(issue_no[2:])
                            if seq <= 0:
                                continue
                            year = 2000 + yy
                            if year not in year_dates_cache:
                                rows = (
                                    self.db.query(source_date_expr.label("source_date"))
                                    .filter(
                                        Match.data_source == "yingqiu_bd",
                                        source_date_expr.like(f"{year}-%"),
                                    )
                                    .distinct()
                                    .order_by(source_date_expr.asc())
                                    .all()
                                )
                                year_dates_cache[year] = [
                                    str(r.source_date).strip()
                                    for r in rows
                                    if str(r.source_date or "").strip()
                                ]
                            year_dates = year_dates_cache.get(year, [])
                            if not year_dates:
                                continue
                            end_idx = min(seq, len(year_dates))
                            start_idx = max(0, end_idx - 3)
                            issue_date_values.update(year_dates[start_idx:end_idx])

                    date_match_filter = None
                    if match_dates or match_date_keys:
                        date_match_filter = or_(
                            Match.match_date.in_(match_dates),
                            source_date_expr.in_(match_date_keys)
                        )
                    scope_filters = []
                    if date_match_filter is not None:
                        scope_filters.append(date_match_filter)
                    if issue_no_values:
                        scope_filters.append(issue_no_expr.in_(issue_no_values))
                    if issue_date_values:
                        scope_filters.append(source_date_expr.in_(list(issue_date_values)))
                    if line_number_values:
                        scope_filters.append(number_expr.in_(list(line_number_values)))

                    schedule_query = (
                        self.db.query(Match, HomeTeam, AwayTeam)
                        .join(HomeTeam, Match.home_team_id == HomeTeam.id, isouter=True)
                        .join(AwayTeam, Match.away_team_id == AwayTeam.id, isouter=True)
                        .filter(Match.data_source == "yingqiu_bd")
                    )
                    if scope_filters:
                        schedule_query = schedule_query.filter(or_(*scope_filters))
                    else:
                        schedule_query = schedule_query.filter(False)

                    schedule_rows = schedule_query.all()

                    for schedule, home_team, away_team in schedule_rows:
                        kickoff = schedule.scheduled_kickoff
                        if kickoff is None and schedule.match_date and schedule.match_time:
                            kickoff = datetime.combine(schedule.match_date, schedule.match_time)
                        kickoff_str = kickoff.strftime("%Y-%m-%d %H:%M:%S") if kickoff else ""

                        attrs = normalize_attrs(schedule.source_attributes)
                        full_score_text, half_score_text = extract_schedule_score_pair(schedule, attrs)

                        date_keys = set()
                        if schedule.match_date:
                            date_keys.add(schedule.match_date.isoformat())
                        source_date = attrs.get("source_schedule_date")
                        if source_date:
                            date_keys.add(str(source_date).strip()[:10])
                        issue_no = str(attrs.get("issue_no") or "").strip()

                        number_raw = attrs.get("number") or attrs.get("lineId") or attrs.get("line_id")
                        home_name = (home_team.name if home_team else "").strip()
                        away_name = (away_team.name if away_team else "").strip()

                        for date_key in date_keys:
                            if not date_key:
                                continue
                            if number_raw:
                                number_text = str(number_raw).strip()
                                number_key = number_text.lstrip("0") or number_text
                                if kickoff_str:
                                    schedule_time_map_by_number[(date_key, number_key)] = kickoff_str
                                schedule_score_map_by_number[(date_key, number_key)] = (
                                    full_score_text,
                                    half_score_text,
                                )
                                if kickoff_str:
                                    schedule_time_candidates_by_number.setdefault(number_key, []).append(
                                        (kickoff_str, home_name, away_name)
                                    )
                                schedule_score_candidates_by_number.setdefault(number_key, []).append(
                                    (full_score_text, half_score_text, home_name, away_name)
                                )
                            if home_name and away_name:
                                if kickoff_str:
                                    schedule_time_map[(date_key, home_name, away_name)] = kickoff_str
                                schedule_score_map[(date_key, home_name, away_name)] = (
                                    full_score_text,
                                    half_score_text,
                                )
                        if issue_no:
                            if number_raw:
                                number_text = str(number_raw).strip()
                                number_key = number_text.lstrip("0") or number_text
                                schedule_score_map_by_issue_number[(issue_no, number_key)] = (
                                    full_score_text,
                                    half_score_text,
                                )
                            if home_name and away_name:
                                schedule_score_map_by_issue[(issue_no, home_name, away_name)] = (
                                    full_score_text,
                                    half_score_text,
                                )

            except Exception as schedule_error:
                self.db.rollback()
                logger.warning(f"璇诲彇鍖楀崟璧涚▼鏃堕棿澶辫触: {schedule_error}")

            
            # 杞崲涓哄墠绔渶瑕佺殑鏍煎紡
            converted_matches = []

            for match in db_matches:
                try:
                    source_attrs = normalize_attrs(match.source_attributes)
                    # 浣跨敤source_attributes锛堝師濮婣PI鏁版嵁锛夋垨浠庢暟鎹簱瀛楁鏋勫缓
                    raw_data = source_attrs if source_attrs else {
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
                    
                    # 浣跨敤鏍囧噯杞崲鍣?

                    transformed_data = transform_real_beidan_match(raw_data)
                    
                    # 璁＄畻P绾э紙浠庣ǔ瀹氭€х瓑绾ф槧灏勶級
                    stability_value = transformed_data.get("stability", "E")
                    stability_to_p_level = {
                        "S": 1, "A": 2, "B": 3, "B-": 4, "C": 5, "D": 6, "E": 7
                    }
                    p_level_value = stability_to_p_level.get(stability_value, 7)
                    
                    # 鏋勫缓姣旇禌鏍煎紡
                    attrs = source_attrs


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
                    raw_match_time = pick_attr("matchTime", "match_time", "matchTimeStr", "match_time_str")

                    def normalize_text(value):
                        return normalize_text_value(value)

                    def normalize_score(value):
                        return normalize_score_value(value)

                    def normalize_handicap(value):
                        text = normalize_text(value)
                        if not text:
                            return ""
                        m = re.search(r"[-+]?\d+(?:\.\d+)?", text)
                        if not m:
                            return text
                        try:
                            number = float(m.group(0))
                        except ValueError:
                            return text
                        if number.is_integer():
                            return str(int(number))
                        return str(number).rstrip("0").rstrip(".")

                    def format_match_time(value):
                        if value is None:
                            return ""
                        if isinstance(value, datetime):
                            return value.strftime("%Y-%m-%d %H:%M:%S")
                        text = str(value).strip()
                        if not text:
                            return ""
                        return text

                    def normalize_team_name(value):
                        text = normalize_text(value)
                        if not text:
                            return ""
                        text = re.sub(r"[\s\-\._·•\(\)（）\[\]]+", "", text)
                        text = (
                            text.replace("足球俱乐部", "")
                            .replace("俱乐部", "")
                            .replace("FC", "")
                            .replace("fc", "")
                        )
                        return text.lower()

                    def team_name_similar(lhs, rhs):
                        l_name = normalize_team_name(lhs)
                        r_name = normalize_team_name(rhs)
                        if not l_name or not r_name:
                            return False
                        return l_name == r_name or l_name in r_name or r_name in l_name

                    match_time_display = format_match_time(raw_match_time)
                    if not match_time_display and match.match_time:
                        match_time_display = match.match_time.strftime("%Y-%m-%d %H:%M:%S")

                    def needs_schedule_time(text):
                        if not text:
                            return True
                        if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
                            return True
                        return "00:00:00" in text

                    if needs_schedule_time(match_time_display) and match.match_time:
                        date_key = match.match_time.date().isoformat()
                        home_name = (match.home_team or "").strip()
                        away_name = (match.away_team or "").strip()
                        schedule_time = schedule_time_map.get((date_key, home_name, away_name))
                        if not schedule_time:
                            line_text = str(match.line_id).strip() if match.line_id is not None else ""
                            line_key = line_text.lstrip("0") or line_text
                            schedule_time = schedule_time_map_by_number.get((date_key, line_key))
                        if not schedule_time:
                            line_text = str(match.line_id).strip() if match.line_id is not None else ""
                            line_key = line_text.lstrip("0") or line_text
                            global_times = schedule_time_candidates_by_number.get(line_key, [])
                            for fallback_time, fallback_home, fallback_away in global_times:
                                if team_name_similar(home_name, fallback_home) and team_name_similar(away_name, fallback_away):
                                    schedule_time = fallback_time
                                    break
                            if not schedule_time and len(global_times) == 1:
                                schedule_time = global_times[0][0]
                        if schedule_time:
                            match_time_display = schedule_time

                    handicap_text = normalize_handicap(
                        pick_attr("rq", "handicap", "letGoal", "let_ball", "rqValue", "rq_val")
                    ) or "0"
                    status_text = normalize_text(
                        pick_attr("statusDes", "status_des", "status", "matchStatus", "state")
                    ) or normalize_text(match.status)

                    if match.home_score is not None and match.away_score is not None:
                        score_text = f"{match.home_score}-{match.away_score}"
                    else:
                        score_text = normalize_score(
                            pick_attr("score", "full_score", "fullScore", "score_full")
                        )

                    halftime_score_text = normalize_score(
                        pick_attr("halfScore", "half_score", "halftimeScore", "halfTimeScore", "mid_score")
                    )

                    # 比分/半场字段优先复用北单赛程（yingqiu_bd）同场次数据
                    home_name = (match.home_team or "").strip()
                    away_name = (match.away_team or "").strip()
                    schedule_score_pair = None
                    if match.match_time:
                        date_key = match.match_time.date().isoformat()
                        schedule_score_pair = schedule_score_map.get((date_key, home_name, away_name))
                        if not schedule_score_pair:
                            line_text = str(match.line_id).strip() if match.line_id is not None else ""
                            line_key = line_text.lstrip("0") or line_text
                            schedule_score_pair = schedule_score_map_by_number.get((date_key, line_key))
                    if not schedule_score_pair:
                        issue_no = _normalize_bd_issue_no(match.date_time)
                        if issue_no:
                            schedule_score_pair = schedule_score_map_by_issue.get((issue_no, home_name, away_name))
                            if not schedule_score_pair:
                                line_text = str(match.line_id).strip() if match.line_id is not None else ""
                                line_key = line_text.lstrip("0") or line_text
                                schedule_score_pair = schedule_score_map_by_issue_number.get((issue_no, line_key))
                    if not schedule_score_pair:
                        line_text = str(match.line_id).strip() if match.line_id is not None else ""
                        line_key = line_text.lstrip("0") or line_text
                        global_scores = schedule_score_candidates_by_number.get(line_key, [])
                        for fallback_full, fallback_half, fallback_home, fallback_away in global_scores:
                            if team_name_similar(home_name, fallback_home) and team_name_similar(away_name, fallback_away):
                                schedule_score_pair = (fallback_full, fallback_half)
                                break
                        if not schedule_score_pair and len(global_scores) == 1:
                            fallback_full, fallback_half, _, _ = global_scores[0]
                            schedule_score_pair = (fallback_full, fallback_half)
                    if schedule_score_pair:
                        schedule_full, schedule_half = schedule_score_pair
                        if schedule_full:
                            score_text = schedule_full
                        if schedule_half:
                            halftime_score_text = schedule_half


                    converted_match = {

                        "id": match.id,
                        "matchTime": match_time_display,
                        "league": match.league or "鍏朵粬",
                        "homeTeam": match.home_team,
                        "guestTeam": match.away_team,
                        "dateTime": str(match.date_time) if match.date_time else "",  # 鏈熷彿
                        "lineId": str(match.line_id) if match.line_id else "",        # 绾胯矾ID
                        "handicap": handicap_text,
                        "status": status_text,
                        "score": score_text,
                        "halfScore": halftime_score_text,
                        "homeScore": match.home_score,
                        "awayScore": match.away_score,
                        "odds": {
                            "homeWin": 0.0,
                            "draw": 0.0,
                            "guestWin": 0.0
                        },
                        "strengthAnalysis": {
                            "homeStrength": "鍧囪　",
                            "guestStrength": "鍧囪　",
                            "powerDifference": "鍙屾柟瀹炲姏鎺ヨ繎"
                        },
                        # 涓夌淮绛涢€夊瓧娈?
                        "strength": str(transformed_data.get("strength", 0)),
                        "winLevel": str(transformed_data.get("winLevel", 0)),
                        "stability": stability_value,
                        "pLevel": p_level_value,               # P绾ф暟鍊?
                        "warning": transformed_data.get("warning"),
                        "sortScore": transformed_data.get("sortScore", 0),
                        "ssum": transformed_data.get("ssum", 0),
                        "predictScore": "1:1",  # 榛樿棰勬祴姣斿垎
                        "recommendation": "瑙傛湜",  # 榛樿鎺ㄨ崘绛夌骇
                        # 缁撴灉鍗＄墖涓庡垎鏋愬脊绐楁墍闇€鍘熷瀛楁
                        "homePower": home_power,
                        "guestPower": guest_power,
                        "homeWinPan": home_win_pan,
                        "guestWinPan": guest_win_pan,
                        "homeFeature": home_feature,
                        "guestFeature": guest_feature,
                        "sourceAttributes": attrs
                    }
                    
                    # 濡傛灉source_attributes鍖呭惈璧旂巼淇℃伅锛屽彲浠ヨ缃畂dds
                    if source_attrs:
                        attrs = source_attrs
                        if isinstance(attrs, dict):

                            # 灏濊瘯鎻愬彇璧旂巼
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
                    logger.error(f"杞崲鏁版嵁搴撴瘮璧涜褰曞け璐? {e}, match_id={match.id}")
                    continue
            
            logger.info(f"鎴愬姛杞崲 {len(converted_matches)} 鏉℃暟鎹簱姣旇禌鏁版嵁")
            
            # 搴旂敤鍐呭瓨涓殑鍏朵粬绛涢€夋潯浠讹紙鍏煎鐜版湁閫昏緫锛?
            filtered_matches = self._apply_filters(converted_matches, filter_params)
            
            return filtered_matches
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"绛涢€夋瘮璧涙暟鎹け璐? {e}")
            return []
    
    def _apply_filters(self, matches: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        搴旂敤绛涢€夋潯浠?
        鏀寔涓夌淮绛涢€夊瓧娈碉細strength, winLevel, stability
        :param matches: 鍘熷姣旇禌鍒楄〃
        :param filters: 绛涢€夋潯浠?
        :return: 绛涢€夊悗鐨勬瘮璧涘垪琛?
        """
        filtered = matches.copy()
        
        # 鎻愬彇绛涢€夋潯浠?
        other_conditions = filters.get("otherConditions", {})
        
        # 1. 鑱旇禌绛涢€?
        leagues = other_conditions.get("leagues", [])
        if leagues:
            filtered = [m for m in filtered if m.get("league") in leagues]
        
        # 2. 鏃ユ湡鏃堕棿绛涢€?
        target_date_time = other_conditions.get("dateTime")
        if target_date_time and target_date_time != "custom":
            # 濡傛灉闇€瑕佺壒瀹氭棩鏈熸椂闂寸殑绛涢€夐€昏緫锛屽湪杩欓噷瀹炵幇
            # 鏆傛椂涓嶅疄鐜帮紝淇濈暀鍘熸湁閫昏緫
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

        # 3. 涓夌淮绛涢€夊瓧娈碉紙鏂板瓧娈碉級
        # 3.1 瀹炲姏绛夌骇宸瓫閫?(powerDiffs)
        power_diffs = other_conditions.get("powerDiffs", [])
        if power_diffs:
            accepted_power = {normalize_signed_level(v) for v in power_diffs}
            filtered = [
                m for m in filtered
                if normalize_signed_level(m.get("strength", "0")) in accepted_power
            ]
        
        # 3.2 璧㈢洏绛夌骇宸瓫閫?(winPanDiffs)
        win_pan_diffs = other_conditions.get("winPanDiffs", [])
        if win_pan_diffs:
            accepted_winpan = {normalize_signed_level(v) for v in win_pan_diffs}
            filtered = [
                m for m in filtered
                if normalize_signed_level(m.get("winLevel", "0")) in accepted_winpan
            ]
        
        # 3.3 涓€璧旂ǔ瀹氭€х瓫閫?(stabilityTiers)
        stability_tiers = other_conditions.get("stabilityTiers", [])
        if stability_tiers:
            # 鏁版嵁涓殑stability瀛楁鏄瓧绗︿覆锛屽 "S", "B-" 绛?
            filtered = [m for m in filtered if str(m.get("stability", "E")) in stability_tiers]
        
        # 4. 鍏煎鏃у瓧娈电瓫閫?
        strength_old = other_conditions.get("strength")
        if strength_old:
            # 鏃ф牸寮忥細鍗曚釜瀛楃涓插€硷紝濡?"balanced", "strong"
            # 杩欓噷闇€瑕佸皢鏃ф牸寮忔槧灏勫埌鏂版牸寮忥紝鏆傛椂绠€鍗曞鐞?
            # 濡傛灉strength瀛楁涓庢棫鏍煎紡鍖归厤锛屽垯淇濈暀
            # 娉ㄦ剰锛氳繖閲岄渶瑕佹牴鎹疄闄呮儏鍐靛畬鍠?
            pass
        
        # 5. 澶勭悊threeDimensional瀛楁锛堝鏋滃瓨鍦級
        three_dimensional = filters.get("threeDimensional", {})
        if three_dimensional:
            # 5.1 瀹炲姏宸厤缃?(powerDifference)
            power_difference = three_dimensional.get("powerDifference", {})
            if power_difference:
                # 杩欓噷闇€瑕佸皢powerDifference瀛楀吀鏄犲皠鍒皊trength鍊?
                # 鏆傛椂涓嶅疄鐜帮紝浼樺厛浣跨敤鏂扮殑powerDiffs鏁扮粍
                pass
            
            # 5.2 璧㈢洏宸厤缃?(winPanDifference)
            win_pan_diff = three_dimensional.get("winPanDifference")
            if win_pan_diff is not None:
                # 杩欓噷闇€瑕佸皢鏁存暟鍊兼槧灏勫埌winLevel鍊?
                # 鏆傛椂涓嶅疄鐜帮紝浼樺厛浣跨敤鏂扮殑winPanDiffs鏁扮粍
                pass
            
            # 5.3 澶у皬鐞冨樊閰嶇疆 (sizeBallDifference)
            size_ball_diff = three_dimensional.get("sizeBallDifference")
            if size_ball_diff is not None:
                # 鏆傛椂涓嶅疄鐜帮紝鏂囨。涓湭鎻愬強澶у皬鐞冨樊绛涢€?
                pass
        
        return filtered

