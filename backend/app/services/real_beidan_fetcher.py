import requests
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta


class RealBeidanFetcher:
    """
    获取真实北单比赛数据的类
    """
    
    def __init__(self):
        self.base_url = "https://m.100qiu.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_beidan_data(self, date_offset: int = 0) -> Optional[List[Dict]]:
        """
        获取北单比赛数据
        :param date_offset: 日期偏移量，0表示今天，1表示明天，-1表示昨天
        :return: 比赛数据列表
        """
        try:
            # 计算日期
            target_date = datetime.now() + timedelta(days=date_offset)
            date_str = target_date.strftime("%y%m%d")  # 例如: 26011
            
            # 构造请求URL
            url = f"{self.base_url}/api/dcListBasic?dateTime={date_str}"
            
            # 发送请求
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            if 'data' in data and data['data']:
                return data['data']
            else:
                print(f"未获取到日期 {date_str} 的比赛数据")
                return []
                
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None
        except Exception as e:
            print(f"获取北单数据时发生未知错误: {e}")
            return None

    def fetch_recent_data(self, days_back: int = 7) -> List[Dict]:
        """
        获取最近几天的北单比赛数据
        :param days_back: 回溯天数
        :return: 比赛数据列表
        """
        all_matches = []
        
        for i in range(-days_back, 8):  # 包括过去和未来几天
            matches = self.fetch_beidan_data(i)
            if matches:
                all_matches.extend(matches)
        
        return all_matches


# 全局实例
real_beidan_fetcher = RealBeidanFetcher()


def get_real_beidan_data(date_offset: int = 0) -> Optional[List[Dict]]:
    """
    获取真实北单比赛数据的便捷函数
    """
    return real_beidan_fetcher.fetch_beidan_data(date_offset)


def fetch_real_beidan_data(date: str) -> Optional[List[Dict]]:
    """
    兼容旧接口：使用日期字符串请求北单数据
    支持 YYMMDD 或缺零的 YYMMD / YYMMd
    """
    if not date or not date.isdigit():
        return None

    date_str = date
    if len(date_str) == 5:
        date_str = date_str[:4] + "0" + date_str[4:]
    elif len(date_str) == 4:
        date_str = date_str[:2] + "0" + date_str[2:]

    try:
        url = f"{real_beidan_fetcher.base_url}/api/dcListBasic?dateTime={date_str}"
        response = real_beidan_fetcher.session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "data" in data and data["data"]:
            return data["data"]
        return []
    except Exception:
        return None


def get_recent_beidan_data(days_back: int = 7) -> List[Dict]:
    """
    获取最近的北单比赛数据
    """
    return real_beidan_fetcher.fetch_recent_data(days_back)


if __name__ == "__main__":
    # 测试获取真实数据
    print("获取今天的北单比赛数据...")
    today_data = get_real_beidan_data(0)
    
    if today_data:
        print(f"获取到 {len(today_data)} 场比赛")
        for i, match in enumerate(today_data[:3]):  # 只显示前3场比赛
            print(f"  {i+1}. {match.get('homeTeam', 'N/A')} vs {match.get('guestTeam', 'N/A')}")
            print(f"     实力值: {match.get('homePower', 'N/A')} vs {match.get('guestPower', 'N/A')}")
            print(f"     让球盘口: {match.get('homeWinPan', 'N/A')} vs {match.get('guestWinPan', 'N/A')}")
    else:
        print("未能获取到今天的比赛数据")
        
    print("\n获取最近的北单比赛数据...")
    recent_data = get_recent_beidan_data(2)
    print(f"获取到 {len(recent_data)} 场比赛")
