"""
联赛管理模块端到端测试脚本
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

def test_get_leagues():
    """测试获取联赛列表功能"""
    print("\n🔍 开始测试获取联赛列表功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/leagues/", headers=HEADERS, params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 联赛列表获取成功")
                print(f"   返回记录数: {len(data['data']['items'])}")
                return True
            else:
                print(f"❌ 联赛列表获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 联赛列表获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 联赛列表获取异常: {e}")
        return False

def test_create_league():
    """测试创建联赛功能"""
    print("\n📝 开始测试创建联赛功能...")
    
    try:
        # 准备测试数据
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
                print("✅ 联赛创建成功")
                print(f"   创建联赛ID: {data['data']['id']}")
                return True, data['data']['id']
            else:
                print(f"❌ 联赛创建失败: {data.get('message')}")
                return False, None
        else:
            print(f"❌ 联赛创建HTTP错误: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ 联赛创建异常: {e}")
        return False, None

def test_update_league(league_id):
    """测试更新联赛功能"""
    print(f"\n✏️  开始测试更新联赛功能 (ID: {league_id})...")
    
    try:
        # 准备更新数据
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
                print("✅ 联赛更新成功")
                return True
            else:
                print(f"❌ 联赛更新失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 联赛更新HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 联赛更新异常: {e}")
        return False

def test_delete_league(league_id):
    """测试删除联赛功能"""
    print(f"\n🗑️  开始测试删除联赛功能 (ID: {league_id})...")
    
    try:
        response = requests.delete(f"{BASE_URL}/api/admin/v1/leagues/{league_id}", 
                                  headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 联赛删除成功")
                return True
            else:
                print(f"❌ 联赛删除失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 联赛删除HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 联赛删除异常: {e}")
        return False

def test_get_countries():
    """测试获取国家列表功能"""
    print("\n🌍 开始测试获取国家列表功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/leagues/countries", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 国家列表获取成功")
                print(f"   返回国家数: {len(data['data']['countries'])}")
                return True
            else:
                print(f"❌ 国家列表获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 国家列表获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 国家列表获取异常: {e}")
        return False

def test_get_league_stats():
    """测试获取联赛统计数据功能"""
    print("\n📊 开始测试获取联赛统计数据功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/leagues/stats", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data["data"]
                print(f"✅ 联赛统计数据获取成功")
                print(f"   总联赛数: {stats['totalLeagues']}")
                print(f"   总国家数: {stats['totalCountries']}")
                print(f"   进行中联赛: {stats['activeLeagues']}")
                print(f"   赛季完成率: {stats['completionRate']}%")
                return True
            else:
                print(f"❌ 联赛统计数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 联赛统计数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 联赛统计数据获取异常: {e}")
        return False

def test_filter_leagues():
    """测试联赛筛选功能"""
    print("\n🔍 开始测试联赛筛选功能...")
    
    try:
        # 测试按状态筛选
        response = requests.get(f"{BASE_URL}/api/admin/v1/leagues/", headers=HEADERS, params={
            "page": 1,
            "size": 10,
            "status": "active"
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 联赛筛选功能测试成功")
                print(f"   筛选结果记录数: {len(data['data']['items'])}")
                return True
            else:
                print(f"❌ 联赛筛选功能测试失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 联赛筛选功能测试HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 联赛筛选功能测试异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("🎯 开始执行联赛管理模块端到端测试...")
    
    # 获取认证token
    if not get_auth_token():
        print("❌ 无法获取认证token，测试终止")
        return False
    
    # 运行测试用例
    results = []
    
    # 测试获取联赛列表
    results.append(("获取联赛列表", test_get_leagues()))
    
    # 测试获取国家列表
    results.append(("获取国家列表", test_get_countries()))
    
    # 测试统计数据
    results.append(("统计数据", test_get_league_stats()))
    
    # 测试创建联赛
    success, league_id = test_create_league()
    results.append(("创建联赛", success))
    
    if success and league_id:
        # 测试更新联赛
        results.append(("更新联赛", test_update_league(league_id)))
        
        # 测试筛选功能
        results.append(("筛选功能", test_filter_leagues()))
        
        # 测试删除联赛
        results.append(("删除联赛", test_delete_league(league_id)))
    
    # 输出测试结果摘要
    print("\n📋 测试结果摘要:")
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试均通过！联赛管理模块端到端功能正常。")
        return True
    else:
        print("\n⚠️  部分测试未通过，请检查相关功能。")
        return False

if __name__ == "__main__":
    run_tests()