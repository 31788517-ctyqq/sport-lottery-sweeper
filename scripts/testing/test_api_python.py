#!/usr/bin/env python3
"""
使用Python直接测试API
"""

import requests
import json

def test_api():
    """测试API"""
    try:
        print("=" * 60)
        print("测试API端点")
        print("=" * 60)
        
        # 测试数据源列表API
        response = requests.get("http://127.0.0.1:8002/api/v1/admin/data-source/sources?page=1&size=10")
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_api()