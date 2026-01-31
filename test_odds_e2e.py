"""
赔率管理模块端到端测试脚本
"""
import requests
import json
import time
from datetime import datetime, timedelta

# 配置测试参数
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# 模拟登录获取认证token
def get_auth_token():
    """获取认证token"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"  # 使用默认管理员账户
        }
        response = requests.post(f"{BASE_URL}/api/v1/admin/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token', '')
            if token:
                HEADERS['Authorization'] = f"Bearer {token}"
                print("✅ 登录成功，获取到认证token")
                return True
        print("❌ 登录失败，无法获取认证token")
        return False
    except Exception as e:
        print(f"❌ 登录过程出现异常: {e}")
        return False

def test_odds_monitoring():
    """测试赔率监控功能"""
    print("\n🔍 开始测试赔率监控功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/odds/monitoring", headers=HEADERS, params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 赔率监控数据获取成功")
                print(f"   返回记录数: {len(data['data']['items'])}")
                return True
            else:
                print(f"❌ 赔率监控数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 赔率监控数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 赔率监控数据获取异常: {e}")
        return False

def test_odds_history():
    """测试赔率历史记录功能"""
    print("\n📅 开始测试赔率历史记录功能...")
    
    try:
        # 尝试获取任意比赛的历史数据
        response = requests.get(f"{BASE_URL}/api/admin/v1/odds/history", headers=HEADERS, params={
            "match_id": 1  # 使用默认比赛ID
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 赔率历史数据获取成功")
                print(f"   返回记录数: {len(data['data']['items'])}")
                return True
            else:
                print(f"❌ 赔率历史数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 赔率历史数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 赔率历史数据获取异常: {e}")
        return False

def test_odds_anomalies():
    """测试异常赔率检测功能"""
    print("\n🚨 开始测试异常赔率检测功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/odds/anomalies", headers=HEADERS, params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 异常赔率数据获取成功")
                print(f"   返回记录数: {len(data['data']['items'])}")
                return True
            else:
                print(f"❌ 异常赔率数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 异常赔率数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 异常赔率数据获取异常: {e}")
        return False

def test_odds_stats():
    """测试赔率统计数据功能"""
    print("\n📊 开始测试赔率统计数据功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/odds/stats", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data["data"]
                print(f"✅ 赔率统计数据获取成功")
                print(f"   总赔率记录: {stats['totalOdds']}")
                print(f"   监控比赛: {stats['monitoredMatches']}")
                print(f"   异常检测: {stats['anomaliesDetected']}")
                print(f"   今日变动: {stats['changesToday']}%")
                return True
            else:
                print(f"❌ 赔率统计数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 赔率统计数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 赔率统计数据获取异常: {e}")
        return False

def test_set_odds_alert():
    """测试设置赔率提醒功能"""
    print("\n🔔 开始测试设置赔率提醒功能...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/admin/v1/odds/alert", headers=HEADERS, params={
            "match_id": 1,
            "bookmaker_id": 1,
            "threshold": 0.05
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 赔率提醒设置成功")
                return True
            else:
                print(f"❌ 赔率提醒设置失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 赔率提醒设置HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 赔率提醒设置异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("🎯 开始执行赔率管理模块端到端测试...")
    
    # 获取认证token
    if not get_auth_token():
        print("❌ 无法获取认证token，测试终止")
        return False
    
    # 运行测试用例
    results = []
    
    # 测试监控功能
    results.append(("赔率监控", test_odds_monitoring()))
    
    # 测试历史功能
    results.append(("赔率历史", test_odds_history()))
    
    # 测试异常检测
    results.append(("异常检测", test_odds_anomalies()))
    
    # 测试统计数据
    results.append(("统计数据", test_odds_stats()))
    
    # 测试提醒设置
    results.append(("设置提醒", test_set_odds_alert()))
    
    # 输出测试结果摘要
    print("\n📋 测试结果摘要:")
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试均通过！赔率管理模块端到端功能正常。")
        return True
    else:
        print("\n⚠️  部分测试未通过，请检查相关功能。")
        return False

if __name__ == "__main__":
    run_tests()