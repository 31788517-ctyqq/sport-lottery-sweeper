"""
北单赛程管理模块端到端测试脚本
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

def test_get_beidan_schedules():
    """测试获取北单赛程列表功能"""
    print("\n🔍 开始测试获取北单赛程列表功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/beidan-schedules/", headers=HEADERS, params={
            "page": 1,
            "size": 10,
            "days": 5
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 北单赛程列表获取成功")
                print(f"   返回记录数: {len(data['data']['items'])}")
                return True
            else:
                print(f"❌ 北单赛程列表获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 北单赛程列表获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 北单赛程列表获取异常: {e}")
        return False

def test_get_leagues():
    """测试获取联赛列表功能"""
    print("\n🏆 开始测试获取联赛列表功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/beidan-schedules/leagues", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 联赛列表获取成功")
                print(f"   返回联赛数: {len(data['data']['items'])}")
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

def test_toggle_publish():
    """测试切换发布状态功能"""
    print("\n📢 开始测试切换发布状态功能...")
    
    try:
        # 首先获取一个赛程
        response = requests.get(f"{BASE_URL}/api/admin/v1/beidan-schedules/", headers=HEADERS, params={
            "page": 1,
            "size": 1,
            "days": 5
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data['data']['items']:
                match_id = data['data']['items'][0]['id']
                
                # 切换发布状态
                response = requests.put(
                    f"{BASE_URL}/api/admin/v1/beidan-schedules/{match_id}/publish",
                    headers=HEADERS,
                    params={"publish": True}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print("✅ 切换发布状态成功")
                        return True
                    else:
                        print(f"❌ 切换发布状态失败: {data.get('message')}")
                        return False
                else:
                    print(f"❌ 切换发布状态HTTP错误: {response.status_code}")
                    return False
            else:
                print("❌ 没有找到可供测试的赛程")
                return False
        else:
            print(f"❌ 获取赛程列表HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 切换发布状态异常: {e}")
        return False

def test_delete_beidan_schedule():
    """测试删除北单赛程功能"""
    print("\n🗑️  开始测试删除北单赛程功能...")
    
    try:
        # 首先获取一个赛程
        response = requests.get(f"{BASE_URL}/api/admin/v1/beidan-schedules/", headers=HEADERS, params={
            "page": 1,
            "size": 1,
            "days": 5
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data['data']['items']:
                match_id = data['data']['items'][0]['id']
                
                # 删除赛程
                response = requests.delete(
                    f"{BASE_URL}/api/admin/v1/beidan-schedules/{match_id}",
                    headers=HEADERS
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print("✅ 删除北单赛程成功")
                        return True
                    else:
                        print(f"❌ 删除北单赛程失败: {data.get('message')}")
                        return False
                else:
                    print(f"❌ 删除北单赛程HTTP错误: {response.status_code}")
                    return False
            else:
                print("❌ 没有找到可供删除的赛程")
                return False
        else:
            print(f"❌ 获取赛程列表HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 删除北单赛程异常: {e}")
        return False

def test_get_beidan_stats():
    """测试获取北单赛程统计数据功能"""
    print("\n📊 开始测试获取北单赛程统计数据功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/v1/beidan-schedules/stats", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data["data"]
                print(f"✅ 北单赛程统计数据获取成功")
                print(f"   总赛程数: {stats['totalMatches']}")
                print(f"   已发布: {stats['publishedMatches']}")
                print(f"   未开奖: {stats['scheduledMatches']}")
                print(f"   已开奖: {stats['finishedMatches']}")
                return True
            else:
                print(f"❌ 北单赛程统计数据获取失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 北单赛程统计数据获取HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 北单赛程统计数据获取异常: {e}")
        return False

def test_filter_beidan_schedules():
    """测试北单赛程筛选功能"""
    print("\n🔍 开始测试北单赛程筛选功能...")
    
    try:
        # 测试按天数筛选
        response = requests.get(f"{BASE_URL}/api/admin/v1/beidan-schedules/", headers=HEADERS, params={
            "page": 1,
            "size": 10,
            "days": 3
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 北单赛程筛选功能测试成功")
                print(f"   筛选结果记录数: {len(data['data']['items'])}")
                return True
            else:
                print(f"❌ 北单赛程筛选功能测试失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 北单赛程筛选功能测试HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 北单赛程筛选功能测试异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("🎯 开始执行北单赛程管理模块端到端测试...")
    
    # 获取认证token
    if not get_auth_token():
        print("❌ 无法获取认证token，测试终止")
        return False
    
    # 运行测试用例
    results = []
    
    # 测试获取赛程列表
    results.append(("获取赛程列表", test_get_beidan_schedules()))
    
    # 测试获取联赛列表
    results.append(("获取联赛列表", test_get_leagues()))
    
    # 测试统计数据
    results.append(("统计数据", test_get_beidan_stats()))
    
    # 测试筛选功能
    results.append(("筛选功能", test_filter_beidan_schedules()))
    
    # 测试切换发布状态
    results.append(("切换发布状态", test_toggle_publish()))
    
    # 由于删除会影响数据，所以最后测试
    results.append(("删除赛程", test_delete_beidan_schedule()))
    
    # 输出测试结果摘要
    print("\n📋 测试结果摘要:")
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试均通过！北单赛程管理模块端到端功能正常。")
        return True
    else:
        print("\n⚠️  部分测试未通过，请检查相关功能。")
        return False

if __name__ == "__main__":
    run_tests()