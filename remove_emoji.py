#!/usr/bin/env python3
"""
批量移除测试文件中的emoji字符
解决Windows控制台编码问题
"""

import os
import re
import sys

# emoji到文本的映射
EMOJI_MAP = {
    "🧪": "[TEST]",
    "🔍": "[SEARCH]",
    "📊": "[STATS]",
    "📋": "[LOG]",
    "📈": "[CHART]",
    "🔗": "[LINK]",
    "🎯": "[TARGET]",
    "⚠️": "[WARNING]",
    "🎉": "[SUCCESS]",
    "✅": "[OK]",
    "❌": "[ERROR]",
    "💡": "[HINT]",
    "🚀": "[LAUNCH]",
    "🔧": "[FIX]",
    "📝": "[NOTE]",
    "⚡": "[SPEED]",
    "🔄": "[REFRESH]",
    "🔒": "[LOCK]",
    "🔓": "[UNLOCK]",
    "📁": "[FOLDER]",
    "📄": "[FILE]",
    "🔔": "[NOTIFY]",
    "⏱️": "[TIMER]",
    "🔑": "[KEY]",
    "🌐": "[WEB]",
    "📱": "[MOBILE]",
    "💻": "[DESKTOP]",
    "🗂️": "[CATEGORY]",
    "📌": "[PIN]",
    "📍": "[LOCATION]",
    "🛡️": "[SECURITY]",
    "📊": "[ANALYTICS]",
    "📈": "[TREND]",
    "📉": "[DECLINE]",
    "🔍": "[INSPECT]",
    "🔎": "[ZOOM]",
    "💼": "[BUSINESS]",
    "💰": "[MONEY]",
    "🕐": "[TIME]",
    "🔋": "[BATTERY]",
    "📶": "[SIGNAL]",
    "🔅": "[BRIGHTNESS]",
    "🔆": "[BRIGHTNESS_HIGH]",
    "📏": "[RULER]",
    "📐": "[TRIANGLE]",
    "🔢": "[NUMBERS]",
    "🔠": "[UPPERCASE]",
    "🔡": "[LOWERCASE]",
    "🔣": "[SYMBOLS]",
    "🎌": "[FLAGS]",
    "🏁": "[FINISH]",
    "🚩": "[FLAG]",
    "🎰": "[SLOT]",
    "🎮": "[GAME]",
    "🎲": "[DICE]",
    "🎳": "[BOWLING]",
    "🏓": "[PINGPONG]",
    "🏸": "[BADMINTON]",
    "🏒": "[HOCKEY]",
    "🏑": "[FIELD_HOCKEY]",
    "🏏": "[CRICKET]",
    "🎾": "[TENNIS]",
    "🏐": "[VOLLEYBALL]",
    "🏊": "[SWIMMING]",
    "🏄": "[SURFING]",
    "🚴": "[CYCLING]",
    "🏇": "[HORSE_RACING]",
    "🏂": "[SNOWBOARDING]",
    "🏌️": "[GOLF]",
    "🏹": "[ARCHERY]",
    "🎣": "[FISHING]",
    "🎿": "[SKIING]",
    "🛷": "[SLED]",
    "🛴": "[SCOOTER]",
    "🚲": "[BIKE]",
    "🛵": "[MOTOR_SCOOTER]",
    "🚂": "[TRAIN]",
    "🚃": "[RAILWAY_CAR]",
    "🚄": "[BULLET_TRAIN]",
    "🚅": "[BULLET_TRAIN_SPEED]",
    "🚆": "[TRAIN2]",
    "🚇": "[METRO]",
    "🚈": "[LIGHT_RAIL]",
    "🚉": "[STATION]",
    "🚊": "[TRAM]",
    "🚝": "[MONORAIL]",
    "🚞": "[MOUNTAIN_RAILWAY]",
    "🚋": "[TRAIN_CAR]",
    "🚌": "[BUS]",
    "🚍": "[ONCOMING_BUS]",
    "🚎": "[TROLLEYBUS]",
    "🚐": "[MINIBUS]",
    "🚑": "[AMBULANCE]",
    "🚒": "[FIRE_ENGINE]",
    "🚓": "[POLICE_CAR]",
    "🚔": "[ONCOMING_POLICE_CAR]",
    "🚕": "[TAXI]",
    "🚖": "[ONCOMING_TAXI]",
    "🚗": "[CAR]",
    "🚘": "[ONCOMING_AUTOMOBILE]",
    "🚙": "[BLUE_CAR]",
    "🚚": "[TRUCK]",
    "🚛": "[ARTICULATED_LORRY]",
    "🚜": "[TRACTOR]",
    "🚢": "[SHIP]",
    "🚣": "[ROWBOAT]",
    "🚤": "[SPEEDBOAT]",
    "🛳️": "[PASSENGER_SHIP]",
    "🛥️": "[MOTORBOAT]",
    "🚁": "[HELICOPTER]",
    "🛩️": "[AIRPLANE]",
    "🚀": "[ROCKET]",
    "🛰️": "[SATELLITE]",
    "💺": "[SEAT]",
    "🛎️": "[BELLHOP]",
    "🚪": "[DOOR]",
    "🛏️": "[BED]",
    "🛋️": "[COUCH]",
    "🚽": "[TOILET]",
    "🚿": "[SHOWER]",
    "🛀": "[BATH]",
    "🛁": "[BATHTUB]",
    "🛒": "[SHOPPING_CART]",
    "🚬": "[SMOKING]",
    "🗿": "[MOAI]",
    "🛂": "[PASSPORT_CONTROL]",
    "🛃": "[CUSTOMS]",
    "🛄": "[BAGGAGE_CLAIM]",
    "🛅": "[LEFT_LUGGAGE]",
    "🚸": "[CHILDREN_CROSSING]",
    "⛔": "[NO_ENTRY]",
    "🚫": "[PROHIBITED]",
    "🚳": "[NO_BICYCLES]",
    "🚭": "[NO_SMOKING]",
    "🚯": "[NO_LITTERING]",
    "🚱": "[NON_POTABLE_WATER]",
    "🚷": "[NO_PEDESTRIANS]",
    "📵": "[NO_MOBILE_PHONES]",
    "🔞": "[UNDERAGE]",
    "☢️": "[RADIOACTIVE]",
    "☣️": "[BIOHAZARD]",
    "⬆️": "[UP]",
    "↗️": "[UP_RIGHT]",
    "➡️": "[RIGHT]",
    "↘️": "[DOWN_RIGHT]",
    "⬇️": "[DOWN]",
    "↙️": "[DOWN_LEFT]",
    "⬅️": "[LEFT]",
    "↖️": "[UP_LEFT]",
    "↕️": "[UP_DOWN]",
    "↔️": "[LEFT_RIGHT]",
    "↩️": "[RIGHT_ARROW_CURVING_LEFT]",
    "↪️": "[LEFT_ARROW_CURVING_RIGHT]",
    "⤴️": "[RIGHT_ARROW_CURVING_UP]",
    "⤵️": "[RIGHT_ARROW_CURVING_DOWN]",
    "🔃": "[CLOCKWISE_VERTICAL_ARROWS]",
    "🔄": "[COUNTERCLOCKWISE_ARROWS_BUTTON]",
    "🔙": "[BACK_ARROW]",
    "🔚": "[END_ARROW]",
    "🔛": "[ON_ARROW]",
    "🔜": "[SOON_ARROW]",
    "🔝": "[TOP_ARROW]",
}

def replace_emoji_in_file(filepath):
    """替换文件中的emoji字符"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换所有emoji
        for emoji, replacement in EMOJI_MAP.items():
            content = content.replace(emoji, replacement)
        
        # 也处理一些常见的变体
        content = re.sub(r'\[OK\]|✅', '[OK]', content)
        content = re.sub(r'\[ERROR\]|❌', '[ERROR]', content)
        content = re.sub(r'\[WARNING\]|⚠️', '[WARNING]', content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    
    except Exception as e:
        print(f"处理文件 {filepath} 时出错: {e}")
        return False

def main():
    """主函数"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(project_root, 'tests')
    
    if not os.path.exists(tests_dir):
        print(f"测试目录不存在: {tests_dir}")
        return
    
    print(f"开始扫描测试目录: {tests_dir}")
    
    modified_count = 0
    total_files = 0
    
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                total_files += 1
                
                if replace_emoji_in_file(filepath):
                    modified_count += 1
                    print(f"已修改: {filepath}")
    
    print(f"\n处理完成!")
    print(f"扫描文件数: {total_files}")
    print(f"修改文件数: {modified_count}")

if __name__ == "__main__":
    main()