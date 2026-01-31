"""
竞彩赛程管理模块端到端测试脚本
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

def test_get_lottery_schedules():
    """测试获取竞彩赛程列表功能"""
    print("\n🔍 开始测试获取竞彩赛程列表功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/lottery-schedules/", headers=HEADERS, params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 竞彩赛程列表获取成功")
                print(f"   返回记录数: {len(data['data']['items'])}")
                return True
            else:
                print(f"❌ 竞彩赛程列表获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 竞彩赛程列表获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 竞彩赛程列表获取异常: {e}")
        return False

def test_create_lottery_schedule():
    """测试创建竞彩赛程功能"""
    print("\n📝 开始测试创建竞彩赛程功能...")
    
    try:
        # 准备测试数据
        current_time = datetime.now() + timedelta(days=1)  # 设置明天的时间
        schedule_data = {
            "league_name": "测试联赛",
            "home_team": "测试主队",
            "away_team": "测试客队",
            "match_time": current_time.strftime('%Y-%m-%d %H:%M:%S'),
            "status": "pending",
            "score": None
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/v1/lottery-schedules/", 
                                headers=HEADERS, json=schedule_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 竞彩赛程创建成功")
                print(f"   创建赛程ID: {data['data']['id']}")
                return True, data['data']['id']
            else:
                print(f"❌ 竞彩赛程创建失败: {data.get('message')}")
                return False, None
        else:
            print(f"❌ 竞彩赛程创建HTTP错误: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ 竞彩赛程创建异常: {e}")
        return False, None

def test_update_lottery_schedule(schedule_id):
    """测试更新竞彩赛程功能"""
    print(f"\n✏️  开始测试更新竞彩赛程功能 (ID: {schedule_id})...")
    
    try:
        # 准备更新数据
        update_data = {
            "league_name": "更新联赛",
            "home_team": "更新主队",
            "away_team": "更新客队",
            "match_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "running",
            "score": "1-0"
        }
        
        response = requests.put(f"{BASE_URL}/api/admin/v1/lottery-schedules/{schedule_id}", 
                              headers=HEADERS, json=update_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 竞彩赛程更新成功")
                return True
            else:
                print(f"❌ 竞彩赛程更新失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 竞彩赛程更新HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 竞彩赛程更新异常: {e}")
        return False

def test_delete_lottery_schedule(schedule_id):
    """测试删除竞彩赛程功能"""
    print(f"\n🗑️  开始测试删除竞彩赛程功能 (ID: {schedule_id})...")
    
    try:
        response = requests.delete(f"{BASE_URL}/api/admin/v1/lottery-schedules/{schedule_id}", 
                                  headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 竞彩赛程删除成功")
                return True
            else:
                print(f"❌ 竞彩赛程删除失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 竞彩赛程删除HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 竞彩赛程删除异常: {e}")
        return False

def test_get_schedule_stats():
    """测试获取赛程统计数据功能"""
    print("\n📊 开始测试获取赛程统计数据功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/lottery-schedules/stats", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data["data"]
                print(f"✅ 赛程统计数据获取成功")
                print(f"   总赛程数: {stats['totalMatches']}")
                print(f"   未开始: {stats['pendingMatches']}")
                print(f"   进行中: {stats['runningMatches']}")
                print(f"   已结束: {stats['finishedMatches']}")
                return True
            else:
                print(f"❌ 赛程统计数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 赛程统计数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 赛程统计数据获取异常: {e}")
        return False

def test_filter_lottery_schedules():
    """测试赛程筛选功能"""
    print("\n🔍 开始测试赛程筛选功能...")
    
    try:
        # 测试按状态筛选
        response = requests.get(f"{BASE_URL}/api/admin/v1/lottery-schedules/", headers=HEADERS, params={
            "page": 1,
            "size": 10,
            "status": "pending"
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 赛程筛选功能测试成功")
                print(f"   筛选结果记录数: {len(data['data']['items'])}")
                return True
            else:
                print(f"❌ 赛程筛选功能测试失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 赛程筛选功能测试HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 赛程筛选功能测试异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("🎯 开始执行竞彩赛程管理模块端到端测试...")
    
    # 获取认证token
    if not get_auth_token():
        print("❌ 无法获取认证token，测试终止")
        return False
    
    # 运行测试用例
    results = []
    
    # 测试获取赛程列表
    results.append(("获取赛程列表", test_get_lottery_schedules()))
    
    # 测试统计数据
    results.append(("统计数据", test_get_schedule_stats()))
    
    # 测试创建赛程
    success, schedule_id = test_create_lottery_schedule()
    results.append(("创建赛程", success))
    
    if success and schedule_id:
        # 测试更新赛程
        results.append(("更新赛程", test_update_lottery_schedule(schedule_id)))
        
        # 测试筛选功能
        results.append(("筛选功能", test_filter_lottery_schedules()))
        
        # 测试删除赛程
        results.append(("删除赛程", test_delete_lottery_schedule(schedule_id)))
    
    # 输出测试结果摘要
    print("\n📋 测试结果摘要:")
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试均通过！竞彩赛程管理模块端到端功能正常。")
        return True
    else:
        print("\n⚠️  部分测试未通过，请检查相关功能。")
        return False

if __name__ == "__main__":
    run_tests()