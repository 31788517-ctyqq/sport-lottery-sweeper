"""
比赛管理模块端到端测试脚本
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

def test_match_crud():
    """测试比赛数据的CRUD操作"""
    print("\n🔍 开始测试比赛数据的CRUD操作...")
    
    # 测试1: 获取比赛列表
    print("1️⃣ 测试获取比赛列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/matches", headers=HEADERS, params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 获取比赛列表成功")
                total_before = data["data"]["total"]
            else:
                print(f"❌ 获取比赛列表失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 获取比赛列表HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取比赛列表异常: {e}")
        return False
    
    # 测试2: 获取联赛列表
    print("2️⃣ 测试获取联赛列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/matches/leagues", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and len(data["data"]) > 0:
                print("✅ 获取联赛列表成功")
                league = data["data"][0]  # 使用第一个联赛
            else:
                print(f"❌ 获取联赛列表失败或列表为空: {data.get('message')}")
                return False
        else:
            print(f"❌ 获取联赛列表HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取联赛列表异常: {e}")
        return False
    
    # 测试3: 创建比赛
    print("3️⃣ 测试创建比赛...")
    try:
        match_data = {
            "league_id": league["id"],
            "home_team_id": 1,  # 使用默认球队ID
            "away_team_id": 2,  # 使用默认球队ID
            "match_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "match_time": "20:00"
        }
        response = requests.post(f"{BASE_URL}/api/admin/v1/matches", headers=HEADERS, params=match_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 比赛创建成功")
                created_match_id = data["data"]["id"]
            else:
                print(f"❌ 比赛创建失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 比赛创建HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 比赛创建异常: {e}")
        return False
    
    # 测试4: 获取刚创建的比赛详情
    print("4️⃣ 测试获取比赛详情...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/matches/{created_match_id}", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 获取比赛详情成功")
            else:
                print(f"❌ 获取比赛详情失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 获取比赛详情HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取比赛详情异常: {e}")
        return False
    
    # 测试5: 更新比赛
    print("5️⃣ 测试更新比赛...")
    try:
        update_data = {
            "status": "live"
        }
        response = requests.put(f"{BASE_URL}/api/admin/v1/matches/{created_match_id}", headers=HEADERS, params=update_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 比赛更新成功")
            else:
                print(f"❌ 比赛更新失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 比赛更新HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 比赛更新异常: {e}")
        return False
    
    # 测试6: 更新比赛状态
    print("6️⃣ 测试更新比赛状态...")
    try:
        response = requests.put(f"{BASE_URL}/api/admin/v1/matches/{created_match_id}/status", 
                               headers=HEADERS, 
                               params={"status": "finished"})
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 比赛状态更新成功")
            else:
                print(f"❌ 比赛状态更新失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 比赛状态更新HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 比赛状态更新异常: {e}")
        return False
    
    # 测试7: 更新比赛分数
    print("7️⃣ 测试更新比赛分数...")
    try:
        response = requests.put(f"{BASE_URL}/api/admin/v1/matches/{created_match_id}/scores", 
                               headers=HEADERS, 
                               params={"home_score": 2, "away_score": 1})
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 比赛分数更新成功")
            else:
                print(f"❌ 比赛分数更新失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 比赛分数更新HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 比赛分数更新异常: {e}")
        return False
    
    # 测试8: 删除比赛
    print("8️⃣ 测试删除比赛...")
    try:
        response = requests.delete(f"{BASE_URL}/api/admin/v1/matches/{created_match_id}", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 比赛删除成功")
            else:
                print(f"❌ 比赛删除失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 比赛删除HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 比赛删除异常: {e}")
        return False
    
    print("✅ 比赛CRUD操作测试完成")
    return True

def test_match_statistics():
    """测试比赛统计数据功能"""
    print("\n📊 开始测试比赛统计数据功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/matches/stats", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data["data"]
                print(f"✅ 统计数据获取成功")
                print(f"   总比赛数: {stats['totalMatches']}")
                print(f"   今日比赛: {stats['todayMatches']}")
                print(f"   进行中比赛: {stats['liveMatches']}")
                print(f"   已完成比赛: {stats['finishedMatches']}")
                print(f"   异常数据: {stats['anomalyCount']}")
                print(f"   联赛数: {stats['totalLeagues']}")
                return True
            else:
                print(f"❌ 统计数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 统计数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 统计数据获取异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("🎯 开始执行比赛管理模块端到端测试...")
    
    # 获取认证token
    if not get_auth_token():
        print("❌ 无法获取认证token，测试终止")
        return False
    
    # 运行测试用例
    results = []
    
    # 测试CRUD操作
    results.append(("CRUD操作", test_match_crud()))
    
    # 测试统计数据
    results.append(("统计数据", test_match_statistics()))
    
    # 输出测试结果摘要
    print("\n📋 测试结果摘要:")
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试均通过！比赛管理模块端到端功能正常。")
        return True
    else:
        print("\n⚠️  部分测试未通过，请检查相关功能。")
        return False

if __name__ == "__main__":
    run_tests()