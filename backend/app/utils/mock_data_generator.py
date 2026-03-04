from typing import List, Dict
import random
from datetime import datetime, timedelta


def generate_mock_beidan_matches(count: int = 50) -> List[Dict]:
    """
    生成模拟北单比赛数据，根据实际API数据结构
    """
    teams = [
        ("坦桑尼亚", "突尼斯"), ("乌干达", "尼日利亚"), ("贝宁", "塞内加尔"),
        ("伯恩利", "纽卡斯尔"), ("切尔西", "伯恩茅斯"), ("诺丁汉森林", "埃弗顿"),
        ("邓迪FC", "基尔马诺克"), ("曼联", "阿森纳"), ("利物浦", "曼城"),
        ("皇马", "巴萨"), ("拜仁", "多特"), ("尤文", "国米"),
        ("巴黎", "马赛"), ("波尔图", "本菲卡"), ("阿贾克斯", "费耶诺德"),
        ("凯尔特人", "流浪者"), ("AC米兰", "拉齐奥"), ("马德里竞技", "比利亚雷亚尔"),
        ("莱比锡", "柏林赫塔"), ("摩纳哥", "里昂"), ("塞维利亚", "皇家社会"),
        ("本菲卡", "波尔图"), ("罗马", "那不勒斯"), ("切尔西", "热刺"),
        ("拜仁", "莱比锡"), ("尤文", "AC米兰"), ("皇马", "马德里竞技"),
        ("曼城", "利物浦"), ("阿森纳", "热刺"), ("巴塞罗那", "瓦伦西亚"),
        ("多特蒙德", "沙尔克04"), ("国际米兰", "罗马"), ("拜仁", "霍芬海姆"),
        ("利物浦", "埃弗顿"), ("曼联", "曼城"), ("阿森纳", "切尔西"),
        ("皇马", "塞维利亚"), ("巴萨", "马德里竞技"), ("拜仁", "多特蒙德"),
        ("尤文图斯", "那不勒斯"), ("巴黎圣日耳曼", "马赛"), ("曼城", "热刺"),
        ("利物浦", "曼联"), ("切尔西", "阿森纳"), ("皇马", "巴塞罗那"),
        ("拜仁", "莱比锡"), ("尤文图斯", "国际米兰"), ("巴黎圣日耳曼", "里昂"),
        ("曼城", "阿森纳"), ("利物浦", "切尔西"), ("皇马", "瓦伦西亚"),
        ("拜仁", "弗赖堡"), ("尤文图斯", "拉齐奥"), ("巴黎圣日耳曼", "摩纳哥")
    ]

    matches = []
    for i in range(min(count, len(teams))):
        home_team, away_team = teams[i]
        
        match = {
            "id": f"BD{i+1:03d}",
            "lineId": f"{i+1:03d}",  # 对应实际API的lineId
            "rq": str(random.choice([-1, 0, 1])),  # 让球数
            "homeTeam": home_team,
            "guestTeam": away_team,
            "homePower": random.randint(30, 70),  # 主队实力值
            "guestPower": 100 - random.randint(30, 70),  # 客队实力值
            "homeWinPan": round(random.uniform(0.0, 2.0), 2),  # 主队让球盘口
            "awayWinQiu_0": random.randint(0, 6),  # 客队0球进数
            "awayWinQiu_1": random.randint(0, 6),  # 客队1球进数
            "awayWinQiu_2": random.randint(0, 6),  # 客队2球进数
            "awayLoseQiu_0": random.randint(0, 6),  # 客队0球失数
            "awayLoseQiu_1": random.randint(0, 6),  # 客队1球失数
            "awayLoseQiu_2": random.randint(0, 6),  # 客队2球失数
            "guestWinPan": round(random.uniform(0.0, 2.0), 2),  # 客队让球盘口
            "homeWinQiu_0": random.randint(0, 6),  # 主队0球进数
            "homeWinQiu_1": random.randint(0, 6),  # 主队1球进数
            "homeWinQiu_2": random.randint(0, 6),  # 主队2球进数
            "homeLoseQiu_0": random.randint(0, 6),  # 主队0球失数
            "homeLoseQiu_1": random.randint(0, 6),  # 主队1球失数
            "homeLoseQiu_2": random.randint(0, 6),  # 主队2球失数
            "homeFeature": f"一赔概率{random.randint(40, 70)}%",  # 主队特征
            "guestFeature": f"一赔概率{random.randint(40, 70)}%",  # 客队特征
            "homeEnterEfficiency": f"进攻:{round(random.uniform(0.1, 0.3), 2)}",  # 主队进攻效率
            "homePreventEfficiency": f"防守:{round(random.uniform(-0.25, -0.1), 2)}",  # 主队防守效率
            "guestEnterEfficiency": f"进攻:{round(random.uniform(0.1, 0.3), 2)}",  # 客队进攻效率
            "guestPreventEfficiency": f"防守:{round(random.uniform(-0.25, -0.1), 2)}",  # 客队防守效率
            "homeSpf": f"{random.randint(4, 7)}胜{random.randint(1, 3)}平{random.randint(1, 4)}负",  # 主队战绩
            "guestSpf": f"{random.randint(4, 7)}胜{random.randint(1, 3)}平{random.randint(1, 4)}负",  # 客队战绩
            "homeWinGap_1": random.randint(0, 5),  # 主队主场赢球差距1
            "homeWinGap_2": random.randint(0, 5),  # 主队主场赢球差距2
            "homeLoseGap_1": random.randint(0, 5),  # 主队主场输球差距1
            "homeLoseGap_2": random.randint(0, 5),  # 主队主场输球差距2
            "awayWinGap_1": random.randint(0, 5),  # 客队客场赢球差距1
            "awayWinGap_2": random.randint(0, 5),  # 客队客场赢球差距2
            "awayLoseGap_1": random.randint(0, 5),  # 客队客场输球差距1
            "awayLoseGap_2": random.randint(0, 5),  # 客队客场输球差距2
            "homeDxqPercentStr": f"{random.randint(10, 70)}%",  # 主队大球概率
            "guestDxqPercentStr": f"{random.randint(10, 90)}%",  # 客队大球概率
            "homeDxqDesc": f"近期:进球{round(random.uniform(0.5, 2.8), 1)} 失球{round(random.uniform(0.5, 2.8), 1)}",  # 主队近期进球失球
            "guestDxqDesc": f"近期:进球{round(random.uniform(0.5, 2.8), 1)} 失球{round(random.uniform(0.5, 2.8), 1)}",  # 客队近期进球失球
            "homeDxqSame10Desc": f"主场:进球{round(random.uniform(0.5, 2.8), 1)} 失球{round(random.uniform(0.5, 2.8), 1)}",  # 主队主场进球失球
            "awayDxqSame10Desc": f"客场:进球{round(random.uniform(0.5, 2.8), 1)} 失球{round(random.uniform(0.5, 2.8), 1)}",  # 客队客场进球失球
            "matchTimeStr": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),  # 比赛时间
            "gameShortName": random.choice(["英超", "西甲", "意甲", "德甲", "法甲", "欧冠", "欧联", "非洲杯", "世界杯"]),  # 赛事简称
            "homeWinAward": str(round(random.uniform(1.5, 5.0), 2)),  # 主队胜赔率
            "guestWinAward": str(round(random.uniform(1.5, 5.0), 2)),  # 客队胜赔率
            "drawAward": str(round(random.uniform(2.0, 4.0), 2)),  # 平局赔率
            "ssum": random.randint(0, 100)  # 添加ssum字段用于排序
        }
        matches.append(match)
    
    return matches


if __name__ == "__main__":
    # 生成并打印示例数据
    sample_data = generate_mock_beidan_matches(5)
    for match in sample_data:
        print(f"ID: {match['id']}, Teams: {match['homeTeam']} vs {match['guestTeam']}")
        print(f"  Power: {match['homePower']} vs {match['guestPower']}")
        print(f"  WinPan: {match['homeWinPan']} vs {match['guestWinPan']}")
        print(f"  RQ: {match['rq']}")
        print("---")