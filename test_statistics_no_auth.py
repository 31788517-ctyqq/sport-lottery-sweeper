import requests
import json

BASE_URL = "http://localhost:8000"

def test_statistics_no_auth():
    """测试统计端点无认证"""
    payload = {
        "strength_filter": None,
        "win_pan_filter": None,
        "stability_filter": None,
        "p_level_filter": None,
        "leagues": None,
        "date_time": "26011",
        "date_range": None,
        "sort_by": "p_level",
        "sort_order": "desc",
        "include_derating": True
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/v1/beidan-filter/statistics", json=payload)
        print(f"状态码: {resp.status_code}")
        if resp.status_code == 200:
            print("成功！响应:", json.dumps(resp.json(), ensure_ascii=False, indent=2))
        else:
            print(f"错误: {resp.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_statistics_no_auth()