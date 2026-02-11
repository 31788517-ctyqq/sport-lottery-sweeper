import requests
import json

def debug_frontend_response():
    print("=" * 70)
    print("调试前端请求的实际响应")
    print("=" * 70)
    
    # 模拟前端请求参数
    params = {
        'skip': 0,
        'limit': 50
    }
    
    # 直接调用API端点
    response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api', params=params)
    
    print(f"API响应状态: {response.status_code}")
    print(f"API响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAPI返回记录数: {len(data)}")
        
        if data:
            first_record = data[0]
            print(f"\n第一条记录的字段和值:")
            for key, value in first_record.items():
                print(f"  {key}: {value} (类型: {type(value).__name__})")
            
            print(f"\n期望的字段顺序与值:")
            expected_order = ['timestamp', 'level', 'request_path', 'response_status', 'duration_ms', 'ip_address', 'message']
            print("字段顺序:", expected_order)
            
            print(f"\n实际记录中的字段顺序:")
            actual_keys = list(first_record.keys())
            print("字段顺序:", actual_keys)
            
            # 检查是否所有期望的字段都存在
            missing_fields = set(expected_order) - set(actual_keys)
            extra_fields = set(actual_keys) - set(expected_order)
            
            if missing_fields:
                print(f"缺少的字段: {missing_fields}")
            if extra_fields:
                print(f"多余的字段: {extra_fields}")
                
            print(f"\n前端显示错位情况复盘:")
            print(f"  '时间' 显示为: {first_record.get('timestamp')} ✓ 正确")
            print(f"  '级别' 显示为: {first_record.get('request_path')} ← 应该是level")
            print(f"  '请求路径' 显示为: {first_record.get('response_status')} ← 应该是request_path")
            print(f"  '状态码' 显示为: {first_record.get('duration_ms')} ← 应该是response_status")
            print(f"  '耗时(ms)' 显示为: {first_record.get('ip_address')} ← 应该是duration_ms")
            print(f"  'IP地址' 显示为: {first_record.get('message')} ← 应该是ip_address")
            print(f"  '消息' 显示为: (空) ← 应该是message")
            
            print(f"\n分析: 似乎是所有字段向左偏移了一位")
        else:
            print("API返回了空数据")
    else:
        print(f"API请求失败: {response.text}")

if __name__ == "__main__":
    debug_frontend_response()