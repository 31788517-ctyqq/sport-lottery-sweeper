import requests
import json
from datetime import datetime

def validate_datetime_handling():
    try:
        response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=1')
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                log_entry = data[0]
                print('API响应验证（datetime处理）：')
                print('='*50)
                
                # 检查timestamp和created_at字段是否为有效的ISO格式日期字符串
                timestamp_str = log_entry.get('timestamp')
                created_at_str = log_entry.get('created_at')
                
                print(f"timestamp: {timestamp_str}")
                print(f"created_at: {created_at_str}")
                
                # 验证是否可以解析为datetime对象
                try:
                    # 尝试解析timestamp
                    if timestamp_str:
                        # 可能是 'YYYY-MM-DDTHH:MM:SS' 格式
                        if len(timestamp_str) == 19:  # 'YYYY-MM-DDTHH:MM:SS'
                            parsed_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
                        elif len(timestamp_str) >= 26:  # ISO 8601 extended format
                            parsed_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        else:
                            parsed_timestamp = datetime.fromisoformat(timestamp_str)
                        print(f"✓ timestamp 可以解析为datetime: {parsed_timestamp}")
                    else:
                        print("⚠ timestamp 为 None")
                        
                    # 尝试解析created_at
                    if created_at_str:
                        if len(created_at_str) == 19:  # 'YYYY-MM-DDTHH:MM:SS'
                            parsed_created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%S')
                        elif len(created_at_str) >= 26:
                            parsed_created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        else:
                            parsed_created_at = datetime.fromisoformat(created_at_str)
                        print(f"✓ created_at 可以解析为datetime: {parsed_created_at}")
                    else:
                        print("⚠ created_at 为 None")
                        
                except ValueError as e:
                    print(f"✗ datetime解析失败: {e}")
                    return False
                
                print("\n✓ 所有datetime字段都可以被正确解析")
                print("✓ API响应符合预期（datetime字段被序列化为ISO字符串）")
                return True
            else:
                print('没有获取到数据')
                return False
        else:
            print(f'API请求失败: {response.status_code}')
            print(response.text[:500])
            return False
    except Exception as e:
        print(f'请求异常: {e}')
        return False

if __name__ == "__main__":
    validate_datetime_handling()