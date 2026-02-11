import requests
import json
from datetime import datetime

def analyze_api_structure():
    url = "https://m.100qiu.com/api/dcListBasic?dateTime=26011"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        
        data = response.json()
        
        if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
            sample_record = data['data'][0]
            
            print("=" * 80)
            print("API 数据结构分析报告")
            print("=" * 80)
            
            print(f"数据总数: {len(data['data'])} 条记录")
            print(f"字段总数: {len(sample_record)} 个字段")
            print()
            
            print("字段详细分析:")
            print("-" * 80)
            
            # 按照功能分组字段
            basic_fields = []      # 基础信息字段
            power_fields = []      # 实力值字段
            pan_fields = []        # 盘口字段
            award_fields = []      # 赔率字段
            goal_fields = []       # 进球字段
            efficiency_fields = [] # 效率字段
            performance_fields = [] # 表现字段
            history_fields = []    # 历史字段
            other_fields = []      # 其他字段
            
            for key, value in sample_record.items():
                if key in ['lineId', 'rq', 'homeTeam', 'guestTeam', 'matchTimeStr', 'gameShortName']:
                    basic_fields.append((key, type(value).__name__, str(value)))
                elif 'Power' in key:
                    power_fields.append((key, type(value).__name__, str(value)))
                elif 'Pan' in key:
                    pan_fields.append((key, type(value).__name__, str(value)))
                elif 'Award' in key:
                    award_fields.append((key, type(value).__name__, str(value)))
                elif 'Qiu' in key:
                    goal_fields.append((key, type(value).__name__, str(value)))
                elif 'Efficiency' in key:
                    efficiency_fields.append((key, type(value).__name__, str(value)))
                elif 'Spf' in key or 'Gap' in key:
                    performance_fields.append((key, type(value).__name__, str(value)))
                elif 'JiFen' in key or 'Dxq' in key or 'jiaoFen' in key:
                    history_fields.append((key, type(value).__name__, str(value)))
                else:
                    other_fields.append((key, type(value).__name__, str(value)))
            
            # 输出分组字段
            def print_group(title, fields):
                if fields:
                    print(f"\n【{title}】")
                    print(f"{'字段名':<25} {'类型':<10} {'示例值'}")
                    print("-" * 80)
                    for field in fields:
                        print(f"{field[0]:<25} {field[1]:<10} {field[2]}")
                    print()
            
            print_group("基础信息字段", basic_fields)
            print_group("实力值字段", power_fields)
            print_group("盘口字段", pan_fields)
            print_group("赔率字段", award_fields)
            print_group("进球字段", goal_fields)
            print_group("效率字段", efficiency_fields)
            print_group("表现字段", performance_fields)
            print_group("历史字段", history_fields)
            print_group("其他字段", other_fields)
            
            print("=" * 80)
            print("北单过滤功能开发建议")
            print("=" * 80)
            print("基于API数据分析，建议实现以下过滤功能：")
            print()
            
            print("1. 实力等级差筛选：")
            print("   - 基于 homePower 和 guestPower 字段计算实力差")
            print("   - 实力差 = abs(homePower - guestPower)")
            print()
            
            print("2. 赢盘等级差筛选：")
            print("   - 基于 homeWinPan 和 guestWinPan 字段计算盘口差")
            print("   - 盘口差 = abs(homeWinPan - guestWinPan)")
            print()
            
            print("3. 一赔稳定性筛选：")
            print("   - 基于 homeWinAward, guestWinAward, drawAward 赔率值")
            print("   - 可计算赔率波动性或稳定性指标")
            print()
            
            print("4. 附加筛选维度：")
            print("   - 联赛筛选：gameShortName")
            print("   - 比赛时间：matchTimeStr")
            print("   - 让球：rq")
            print("   - 进球分布：homeWinQiu_x, awayWinQiu_x 等")
            print()
            
            print("5. 数据处理建议：")
            print("   - 将 matchTimeStr 转换为日期对象进行时间范围筛选")
            print("   - 提取 teamFeature 中的数值信息用于分析")
            print("   - 整合历史对战信息(jiaoFen)用于预测分析")
            
        else:
            print("未能找到有效的数据结构")
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    except Exception as e:
        print(f"Other error: {e}")

if __name__ == "__main__":
    analyze_api_structure()