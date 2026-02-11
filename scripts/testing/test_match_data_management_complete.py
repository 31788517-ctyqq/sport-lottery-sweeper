"""
比赛数据管理菜单端到端自动化测试脚本
"""
import requests
import json
import time
from datetime import datetime, timedelta
import random

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
        # 修正登录API路径
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            # 检查响应结构并提取token
            token = result.get('data', {}).get('access_token', '')
            if token:
                HEADERS['Authorization'] = f"Bearer {token}"
                print("✅ 登录成功，获取到认证token")
                return True
        print(f"❌ 登录失败，无法获取认证token，状态码: {response.status_code}")
        print(f"   响应内容: {response.text}")
        return False
    except Exception as e:
        print(f"❌ 登录过程出现异常: {e}")
        return False

# 第一部分：联赛管理测试
def test_league_management():
    """测试联赛管理功能"""
    print("\n🏆 开始测试联赛管理功能...")
    
    # 测试1.1: 获取联赛列表
    print("  测试1.1: 获取联赛列表")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/leagues/", headers=HEADERS, params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 联赛列表获取成功")
            else:
                print(f"    ❌ 联赛列表获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 联赛列表获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 联赛列表获取异常: {e}")
        return False
    
    # 测试1.2: 创建联赛
    print("  测试1.2: 创建联赛")
    try:
        league_data = {
            "name": f"测试联赛_{int(time.time())}",
            "country": "测试国",
            "level": "top",
            "season": "2026",
            "status": "active",
            "description": "这是一个测试联赛"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/v1/leagues/", 
                                headers=HEADERS, json=league_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                league_id = data['data']['id']
                print(f"    ✅ 联赛创建成功，ID: {league_id}")
            else:
                print(f"    ❌ 联赛创建失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 联赛创建HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 联赛创建异常: {e}")
        return False
    
    # 测试1.3: 更新联赛
    print("  测试1.3: 更新联赛")
    try:
        update_data = {
            "name": f"更新联赛_{int(time.time())}",
            "country": "更新国",
            "level": "second",
            "season": "2027",
            "status": "inactive",
            "description": "这是一个更新的测试联赛"
        }
        
        response = requests.put(f"{BASE_URL}/api/admin/v1/leagues/{league_id}", 
                              headers=HEADERS, json=update_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 联赛更新成功")
            else:
                print(f"    ❌ 联赛更新失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 联赛更新HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 联赛更新异常: {e}")
        return False
    
    # 测试1.4: 获取统计数据
    print("  测试1.5: 获取联赛统计数据")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/leagues/stats", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 联赛统计数据获取成功")
            else:
                print(f"    ❌ 联赛统计数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 联赛统计数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 联赛统计数据获取异常: {e}")
        return False
    
    # 测试1.5: 获取国家列表
    print("  测试1.6: 获取国家列表")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/leagues/countries", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 国家列表获取成功")
            else:
                print(f"    ❌ 国家列表获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 国家列表获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 国家列表获取异常: {e}")
        return False
    
    # 测试1.6: 删除联赛
    print("  测试1.7: 删除联赛")
    try:
        response = requests.delete(f"{BASE_URL}/api/admin/v1/leagues/{league_id}", 
                                  headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 联赛删除成功")
            else:
                print(f"    ❌ 联赛删除失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 联赛删除HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 联赛删除异常: {e}")
        return False
    
    print("  🏆 联赛管理功能测试完成")
    return True

# 第二部分：比赛管理测试
def test_match_management():
    """测试比赛管理功能"""
    print("\n⚽ 开始测试比赛管理功能...")
    
    # 测试2.1: 获取比赛列表
    print("  测试2.1: 获取比赛列表")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/matches/", headers=HEADERS, params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 比赛列表获取成功")
            else:
                print(f"    ❌ 比赛列表获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 比赛列表获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 比赛列表获取异常: {e}")
        return False
    
    # 测试2.2: 创建比赛
    print("  测试2.2: 创建比赛")
    try:
        # 首先获取一个联赛ID用于创建比赛
        response = requests.get(f"{BASE_URL}/api/admin/v1/leagues/", headers=HEADERS, params={
            "page": 1,
            "size": 1
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data['data']['items']:
                league_id = data['data']['items'][0]['id']
                
                match_data = {
                    "league_id": league_id,
                    "home_team": f"主队_{int(time.time())}",
                    "away_team": f"客队_{int(time.time())}",
                    "match_time": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "pending",
                    "score": None
                }
                
                response = requests.post(f"{BASE_URL}/api/admin/v1/matches/", 
                                        headers=HEADERS, json=match_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        match_id = data['data']['id']
                        print(f"    ✅ 比赛创建成功，ID: {match_id}")
                    else:
                        print(f"    ❌ 比赛创建失败: {data.get('message')}")
                        return False
                else:
                    print(f"    ❌ 比赛创建HTTP错误: {response.status_code}")
                    return False
            else:
                print("    ❌ 无法获取联赛用于创建比赛")
                return False
        else:
            print(f"    ❌ 获取联赛列表HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 比赛创建异常: {e}")
        return False
    
    # 测试2.3: 更新比赛
    print("  测试2.3: 更新比赛")
    try:
        update_data = {
            "home_team": f"更新主队_{int(time.time())}",
            "away_team": f"更新客队_{int(time.time())}",
            "status": "running",
            "score": "1-0"
        }
        
        response = requests.put(f"{BASE_URL}/api/admin/v1/matches/{match_id}", 
                              headers=HEADERS, json=update_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 比赛更新成功")
            else:
                print(f"    ❌ 比赛更新失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 比赛更新HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 比赛更新异常: {e}")
        return False
    
    # 测试2.4: 获取比赛统计数据
    print("  测试2.4: 获取比赛统计数据")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/matches/stats", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 比赛统计数据获取成功")
            else:
                print(f"    ❌ 比赛统计数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 比赛统计数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 比赛统计数据获取异常: {e}")
        return False
    
    # 测试2.5: 删除比赛
    print("  测试2.5: 删除比赛")
    try:
        response = requests.delete(f"{BASE_URL}/api/admin/v1/matches/{match_id}", 
                                  headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 比赛删除成功")
            else:
                print(f"    ❌ 比赛删除失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 比赛删除HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 比赛删除异常: {e}")
        return False
    
    print("  ⚽ 比赛管理功能测试完成")
    return True

# 第三部分：赔率管理测试
def test_odds_management():
    """测试赔率管理功能"""
    print("\n🎲 开始测试赔率管理功能...")
    
    # 测试3.1: 获取赔率监控数据
    print("  测试3.1: 获取赔率监控数据")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/odds/monitoring", headers=HEADERS, params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 赔率监控数据获取成功")
            else:
                print(f"    ❌ 赔率监控数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 赔率监控数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 赔率监控数据获取异常: {e}")
        return False
    
    # 测试3.2: 获取赔率历史记录
    print("  测试3.2: 获取赔率历史记录")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/odds/history", headers=HEADERS, params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 赔率历史记录获取成功")
            else:
                print(f"    ❌ 赔率历史记录获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 赔率历史记录获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 赔率历史记录获取异常: {e}")
        return False
    
    # 测试3.3: 获取异常赔率检测
    print("  测试3.3: 获取异常赔率检测")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/odds/anomalies", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 异常赔率检测获取成功")
            else:
                print(f"    ❌ 异常赔率检测获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 异常赔率检测获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 异常赔率检测获取异常: {e}")
        return False
    
    # 测试3.4: 获取赔率统计数据
    print("  测试3.4: 获取赔率统计数据")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/odds/stats", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 赔率统计数据获取成功")
            else:
                print(f"    ❌ 赔率统计数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 赔率统计数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 赔率统计数据获取异常: {e}")
        return False
    
    print("  🎲 赔率管理功能测试完成")
    return True

# 第四部分：竞彩赛程测试
def test_lottery_schedule():
    """测试竞彩赛程功能"""
    print("\n🎫 开始测试竞彩赛程功能...")
    
    # 测试4.1: 获取竞彩赛程列表
    print("  测试4.1: 获取竞彩赛程列表")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/lottery-schedules/", headers=HEADERS, params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 竞彩赛程列表获取成功")
            else:
                print(f"    ❌ 竞彩赛程列表获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 竞彩赛程列表获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 竞彩赛程列表获取异常: {e}")
        return False
    
    # 测试4.2: 创建竞彩赛程
    print("  测试4.2: 创建竞彩赛程")
    try:
        # 首先获取一个联赛ID用于创建赛程
        response = requests.get(f"{BASE_URL}/api/admin/v1/leagues/", headers=HEADERS, params={
            "page": 1,
            "size": 1
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data['data']['items']:
                league_id = data['data']['items'][0]['id']
                
                schedule_data = {
                    "league_name": data['data']['items'][0]['name'],
                    "home_team": f"主队_{int(time.time())}",
                    "away_team": f"客队_{int(time.time())}",
                    "match_time": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "pending",
                    "score": None
                }
                
                response = requests.post(f"{BASE_URL}/api/admin/v1/lottery-schedules/", 
                                        headers=HEADERS, json=schedule_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        schedule_id = data['data']['id']
                        print(f"    ✅ 竞彩赛程创建成功，ID: {schedule_id}")
                        
                        # 测试4.3: 更新竞彩赛程
                        print("  测试4.3: 更新竞彩赛程")
                        update_data = {
                            "league_name": data['data']['items'][0]['name'],
                            "home_team": f"更新主队_{int(time.time())}",
                            "away_team": f"更新客队_{int(time.time())}",
                            "status": "running",
                            "score": "2-1"
                        }
                        
                        response = requests.put(f"{BASE_URL}/api/admin/v1/lottery-schedules/{schedule_id}", 
                                              headers=HEADERS, json=update_data)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success"):
                                print("    ✅ 竞彩赛程更新成功")
                            else:
                                print(f"    ❌ 竞彩赛程更新失败: {data.get('message')}")
                                return False
                        else:
                            print(f"    ❌ 竞彩赛程更新HTTP错误: {response.status_code}")
                            return False
                        
                        # 测试4.4: 删除竞彩赛程
                        print("  测试4.4: 删除竞彩赛程")
                        response = requests.delete(f"{BASE_URL}/api/admin/v1/lottery-schedules/{schedule_id}", 
                                                  headers=HEADERS)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success"):
                                print("    ✅ 竞彩赛程删除成功")
                            else:
                                print(f"    ❌ 竞彩赛程删除失败: {data.get('message')}")
                                return False
                        else:
                            print(f"    ❌ 竞彩赛程删除HTTP错误: {response.status_code}")
                            return False
                    else:
                        print(f"    ❌ 竞彩赛程创建失败: {data.get('message')}")
                        return False
                else:
                    print(f"    ❌ 竞彩赛程创建HTTP错误: {response.status_code}")
                    return False
            else:
                print("    ❌ 无法获取联赛用于创建赛程")
                return False
        else:
            print(f"    ❌ 获取联赛列表HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 竞彩赛程创建异常: {e}")
        return False
    
    # 测试4.5: 获取竞彩赛程统计数据
    print("  测试4.5: 获取竞彩赛程统计数据")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/lottery-schedules/stats", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 竞彩赛程统计数据获取成功")
            else:
                print(f"    ❌ 竞彩赛程统计数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 竞彩赛程统计数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 竞彩赛程统计数据获取异常: {e}")
        return False
    
    print("  🎫 竞彩赛程功能测试完成")
    return True

# 第五部分：北单赛程测试
def test_beidan_schedule():
    """测试北单赛程功能"""
    print("\n🎯 开始测试北单赛程功能...")
    
    # 测试5.1: 获取北单赛程列表
    print("  测试5.1: 获取北单赛程列表")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/beidan-schedules/", headers=HEADERS, params={
            "page": 1,
            "size": 10,
            "days": 5
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 北单赛程列表获取成功")
            else:
                print(f"    ❌ 北单赛程列表获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 北单赛程列表获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 北单赛程列表获取异常: {e}")
        return False
    
    # 测试5.2: 获取北单赛程统计数据
    print("  测试5.2: 获取北单赛程统计数据")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/beidan-schedules/stats", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 北单赛程统计数据获取成功")
            else:
                print(f"    ❌ 北单赛程统计数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 北单赛程统计数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 北单赛程统计数据获取异常: {e}")
        return False
    
    # 测试5.3: 获取联赛列表
    print("  测试5.3: 获取联赛列表")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/beidan-schedules/leagues", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("    ✅ 联赛列表获取成功")
            else:
                print(f"    ❌ 联赛列表获取失败: {data.get('message')}")
                return False
        else:
            print(f"    ❌ 联赛列表获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ 联赛列表获取异常: {e}")
        return False
    
    print("  🎯 北单赛程功能测试完成")
    return True

def run_comprehensive_tests():
    """运行综合测试"""
    print("🎯 开始执行比赛数据管理菜单端到端测试...")
    
    # 获取认证token
    if not get_auth_token():
        print("❌ 无法获取认证token，测试终止")
        return False
    
    # 运行各模块测试
    results = []
    
    results.append(("联赛管理", test_league_management()))
    results.append(("比赛管理", test_match_management()))
    results.append(("赔率管理", test_odds_management()))
    results.append(("竞彩赛程", test_lottery_schedule()))
    results.append(("北单赛程", test_beidan_schedule()))
    
    # 输出测试结果摘要
    print("\n📋 测试结果摘要:")
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试均通过！比赛数据管理菜单端到端功能正常。")
        return True
    else:
        print("\n⚠️  部分测试未通过，请检查相关功能。")
        return False

if __name__ == "__main__":
    run_comprehensive_tests()