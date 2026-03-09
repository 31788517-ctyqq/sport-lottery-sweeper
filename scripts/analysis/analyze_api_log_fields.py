import requests
import json
import re
from datetime import datetime

def analyze_api_log_fields():
    # 获取API日志数据
    response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=5')
    if response.status_code == 200:
        data = response.json()
        print('API日志字段值格式分析：')
        print('='*60)
        
        if data and len(data) > 0:
            # 选择第一条日志进行详细分析
            log_entry = data[0]
            
            print(f'时间 (timestamp): {log_entry.get("timestamp")} - 格式: YYYY-MM-DDTHH:MM:SS')
            print(f'级别 (level): {log_entry.get("level")} - 应为: INFO/WARN/ERROR等')
            print(f'请求路径 (request_path): {log_entry.get("request_path")} - 应为: /crawler/task/N')
            print(f'状态码 (response_status): {log_entry.get("response_status")} - 应为数字')
            print(f'耗时(ms) (duration_ms): {log_entry.get("duration_ms")} - 应为整数毫秒值')
            print(f'IP地址 (ip_address): {log_entry.get("ip_address")} - 可能为空')
            print(f'消息 (message): {log_entry.get("message")} - 应为描述性文本')
            print()
            
            # 验证格式
            timestamp = log_entry.get('timestamp')
            level = log_entry.get('level')
            request_path = log_entry.get('request_path')
            response_status = log_entry.get('response_status')
            duration_ms = log_entry.get('duration_ms')
            message = log_entry.get('message')
            
            issues = []
            
            # 验证时间戳格式
            if timestamp:
                try:
                    # 尝试解析时间戳
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    print('✓ 时间戳格式正确')
                except ValueError:
                    issues.append(f'时间戳格式错误: {timestamp}')
                    print(f'✗ 时间戳格式错误: {timestamp}')
            
            # 验证级别
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'WARN', 'ERROR', 'CRITICAL']
            if level and level in valid_levels:
                print('✓ 级别值有效')
            else:
                issues.append(f'级别值无效: {level}')
                print(f'✗ 级别值无效: {level}')
            
            # 验证请求路径
            if request_path and request_path.startswith('/crawler/task/'):
                print('✓ 请求路径格式正确')
            else:
                issues.append(f'请求路径格式错误: {request_path}')
                print(f'✗ 请求路径格式错误: {request_path}')
            
            # 验证响应状态码
            if response_status and isinstance(response_status, int):
                print('✓ 状态码类型正确')
            else:
                issues.append(f'状态码类型错误: {response_status} (类型: {type(response_status)})')
                print(f'✗ 状态码类型错误: {response_status} (类型: {type(response_status)})')
            
            # 验证耗时
            if duration_ms and isinstance(duration_ms, int):
                print('✓ 耗时值类型正确')
            else:
                issues.append(f'耗时值类型错误: {duration_ms} (类型: {type(duration_ms)})')
                print(f'✗ 耗时值类型错误: {duration_ms} (类型: {type(duration_ms)})')
            
            # 验证消息
            if message and isinstance(message, str):
                print('✓ 消息类型正确')
            else:
                issues.append(f'消息类型错误: {message} (类型: {type(message)})')
                print(f'✗ 消息类型错误: {message} (类型: {type(message)})')
            
            print()
            if issues:
                print('发现以下问题:')
                for issue in issues:
                    print(f'- {issue}')
            else:
                print('所有字段值格式均正确!')
        else:
            print('没有获取到数据')
    else:
        print(f'API请求失败: {response.status_code}')

if __name__ == "__main__":
    analyze_api_log_fields()