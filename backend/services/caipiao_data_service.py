import requests
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.schemas.caipiao_data import CaipiaoDataCreate
from backend.crud.crud_caipiao_data import create_caipiao_data_batch
import logging

logger = logging.getLogger(__name__)


class CaipiaoDataService:
    def __init__(self, db: Session):
        self.db = db
        self.base_url = "https://m.100qiu.com/api/dcListBasic"

    def fetch_data_from_api(self, date_time: str = "26011") -> List[Dict[str, Any]]:
        """
        从API获取竞彩数据
        :param date_time: 日期时间参数，默认为"26011"
        :return: API返回的数据列表
        """
        params = {
            "dateTime": date_time
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and isinstance(data["data"], list):
                return data["data"]
            else:
                logger.warning(f"API响应中没有有效数据: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求API失败: {e}")
            return []
        except ValueError as e:
            logger.error(f"解析API响应失败: {e}")
            return []

    def map_api_data_to_schema(self, api_data: List[Dict[str, Any]]) -> List[CaipiaoDataCreate]:
        """
        将API返回的数据映射为数据库模型
        :param api_data: API返回的数据列表
        :return: 映射后的数据对象列表
        """
        schema_list = []
        
        for item in api_data:
            # 将API字段映射到数据库模型字段
            schema_item = CaipiaoDataCreate(
                line_id=item.get("lineId", ""),
                rq=item.get("rq", ""),
                home_team=item.get("homeTeam", ""),
                guest_team=item.get("guestTeam", ""),
                home_power=item.get("homePower", 0),
                guest_power=item.get("guestPower", 0),
                home_win_pan=float(item.get("homeWinPan", 0)),
                home_win_qiu_0=item.get("homeWinQiu_0", 0),
                home_win_qiu_1=item.get("homeWinQiu_1", 0),
                home_win_qiu_2=item.get("homeWinQiu_2", 0),
                home_lose_qiu_0=item.get("homeLoseQiu_0", 0),
                home_lose_qiu_1=item.get("homeLoseQiu_1", 0),
                home_lose_qiu_2=item.get("homeLoseQiu_2", 0),
                guest_win_pan=float(item.get("guestWinPan", 0)),
                away_win_qiu_0=item.get("awayWinQiu_0", 0),
                away_win_qiu_1=item.get("awayWinQiu_1", 0),
                away_win_qiu_2=item.get("awayWinQiu_2", 0),
                away_lose_qiu_0=item.get("awayLoseQiu_0", 0),
                away_lose_qiu_1=item.get("awayLoseQiu_1", 0),
                away_lose_qiu_2=item.get("awayLoseQiu_2", 0),
                home_feature=item.get("homeFeature"),
                guest_feature=item.get("guestFeature"),
                home_enter_efficiency=item.get("homeEnterEfficiency"),
                home_prevent_efficiency=item.get("homePreventEfficiency"),
                guest_enter_efficiency=item.get("guestEnterEfficiency"),
                guest_prevent_efficiency=item.get("guestPreventEfficiency"),
                home_spf=item.get("homeSpf"),
                guest_spf=item.get("guestSpf"),
                home_win_gap_1=item.get("homeWinGap_1", 0),
                home_win_gap_2=item.get("homeWinGap_2", 0),
                home_lose_gap_1=item.get("homeLoseGap_1", 0),
                home_lose_gap_2=item.get("homeLoseGap_2", 0),
                away_win_gap_1=item.get("awayWinGap_1", 0),
                away_win_gap_2=item.get("awayWinGap_2", 0),
                away_lose_gap_1=item.get("awayLoseGap_1", 0),
                away_lose_gap_2=item.get("awayLoseGap_2", 0),
                home_dxq_percent_str=item.get("homeDxqPercentStr"),
                guest_dxq_percent_str=item.get("guestDxqPercentStr"),
                home_dxq_desc=item.get("homeDxqDesc"),
                guest_dxq_desc=item.get("guestDxqDesc"),
                home_dxq_same10_desc=item.get("homeDxqSame10Desc"),
                away_dxq_same10_desc=item.get("awayDxqSame10Desc"),
                jiao_fen_desc=item.get("jiaoFenDesc"),
                jiao_fen_match1=item.get("jiaoFenMatch1"),
                jiao_fen_match2=item.get("jiaoFenMatch2"),
                match_time_str=item.get("matchTimeStr", ""),
                game_short_name=item.get("gameShortName", ""),
                home_win_award=item.get("homeWinAward", ""),
                guest_win_award=item.get("guestWinAward", ""),
                draw_award=item.get("drawAward", ""),
                # 对于其他联赛的额外字段
                home_ji_fen_home_all=item.get("homeJiFenHomeAll"),
                home_ji_fen_home=item.get("homeJiFenHome"),
                away_ji_fen_home_all=item.get("awayJiFenHomeAll"),
                away_ji_fen_home=item.get("awayJiFenHome"),
                away_ji_fen_guest=item.get("awayJiFenGuest")
            )
            schema_list.append(schema_item)
        
        return schema_list

    def sync_data_from_api(self, date_time: str = "26011") -> int:
        """
        从API同步数据到数据库
        :param date_time: 日期时间参数
        :return: 同步的数据条数
        """
        # 从API获取数据
        api_data = self.fetch_data_from_api(date_time)
        if not api_data:
            logger.warning("没有从API获取到数据")
            return 0
        
        # 将API数据映射为数据库模型
        schema_data = self.map_api_data_to_schema(api_data)
        
        # 批量保存到数据库
        created_records = create_caipiao_data_batch(self.db, schema_data)
        
        logger.info(f"成功同步 {len(created_records)} 条竞彩数据")
        return len(created_records)