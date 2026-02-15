import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 模拟parse_match_from_100qiu函数
def parse_match_from_100qiu(item, date_time):
    """
    从100qiu API响应中解析比赛数据
    这里根据实际API响应结构进行解析
    """
    try:
        # 提取基本字段
        line_id = str(item.get('lineId', ''))
        home_team = item.get('homeTeam', '未知主队')
        away_team = item.get('guestTeam', '未知客队')  # 注意：100qiu使用guestTeam而不是awayTeam
        league = item.get('gameShortName', '未知联赛')
        
        # 处理比赛时间
        from datetime import datetime
        match_time_str = item.get('matchTimeStr', None)
        match_time = None
        if match_time_str:
            if isinstance(match_time_str, str):
                try:
                    # 100qiu返回的是"YYYY-MM-DD"格式
                    match_time = datetime.strptime(match_time_str, "%Y-%m-%d")
                except ValueError:
                    # 如果解析失败，使用当前时间
                    match_time = datetime.now()
        else:
            match_time = datetime.now()
        
        # 获取比分信息
        home_score = None
        away_score = None
        
        # 状态默认为pending（未开始）
        status = 'pending'
        
        # 提取基本字段
        line_id_str = str(item.get('lineId', '')).strip()
        
        # 转换期号和序号为整数
        try:
            date_time_int = int(date_time) if date_time else 0
            line_id_int = int(line_id_str) if line_id_str else 0
        except ValueError:
            date_time_int = 0
            line_id_int = 0
        
        print(f"调试信息:")
        print(f"  date_time参数: {date_time} (类型: {type(date_time)})")
        print(f"  date_time_int: {date_time_int}")
        print(f"  line_id_str: '{line_id_str}'")
        print(f"  line_id_int: {line_id_int}")
        
        # 生成新的match_id格式：date_time_line_id（如：26024_001）
        if date_time_int > 0 and line_id_int > 0:
            match_id = f"{date_time_int}_{line_id_int:03d}"
        elif line_id_str:
            # 兼容旧格式
            match_id = f"100qiu_{line_id_str}"
        else:
            # 如果没有有效数据，使用时间戳生成临时ID
            import time
            match_id = f"{int(time.time() * 1000)}"
        
        # 确保date_time不为None（数据库约束可能为NOT NULL）
        final_date_time = date_time_int if date_time_int != 0 else 26022  # 默认期号
        # 确保line_id不为0
        final_line_id = line_id_int if line_id_int != 0 else 1
        
        print(f"  final_date_time: {final_date_time}")
        print(f"  final_line_id: {final_line_id}")
        
        # 将date_time和line_id添加到source_attributes中
        source_attributes = item.copy()
        source_attributes['date_time'] = final_date_time
        source_attributes['line_id'] = final_line_id
        
        # 返回符合FootballMatch模型的字段
        match_data = {
            "match_id": match_id,
            "date_time": final_date_time,
            "line_id": final_line_id,
            "home_team": home_team,
            "away_team": away_team,
            "match_time": match_time,
            "league": league,
            "status": status,
            "home_score": home_score,
            "away_score": away_score,
            "data_source": "100qiu",
            "source_attributes": source_attributes
        }
        
        print(f"返回的match_data:")
        for key, value in match_data.items():
            print(f"  {key}: {value} (类型: {type(value)})")
        
        return match_data
    except Exception as e:
        print(f"解析比赛数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None

# 测试数据
test_item = {
    "lineId": "001",
    "homeTeam": "普洛耶什蒂",
    "guestTeam": "尤尼史洛波西亚",
    "gameShortName": "罗甲",
    "matchTimeStr": "2026-02-03"
}

print("测试1: date_time为字符串'26022'")
result1 = parse_match_from_100qiu(test_item, "26022")
print("\n" + "="*60 + "\n")

print("测试2: date_time为None")
result2 = parse_match_from_100qiu(test_item, None)
print("\n" + "="*60 + "\n")

print("测试3: date_time为空字符串")
result3 = parse_match_from_100qiu(test_item, "")
print("\n" + "="*60 + "\n")

print("测试4: lineId为空字符串")
test_item2 = test_item.copy()
test_item2["lineId"] = ""
result4 = parse_match_from_100qiu(test_item2, "26022")