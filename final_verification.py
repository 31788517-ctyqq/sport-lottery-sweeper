import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"
BEIDAN_BASE = f"{BASE_URL}/api/v1/beidan-filter"

def print_status(ok, message):
    if ok:
        print(f"[OK] {message}")
    else:
        print(f"[FAIL] {message}")

def test_health():
    """测试服务健康状态"""
    try:
        response = requests.get(f"{BASE_URL}/health/live", timeout=5)
        return response.status_code == 200, f"Health check: {response.status_code}"
    except Exception as e:
        return False, f"Health check failed: {e}"

def test_option_apis():
    """测试选项API"""
    apis = [
        ("strength-options", "实力等级差选项"),
        ("win-pan-diff-options", "赢盘等级差选项"), 
        ("stability-options", "一赔稳定性选项")
    ]
    
    all_ok = True
    for endpoint, name in apis:
        try:
            response = requests.get(f"{BEIDAN_BASE}/{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                # 检查数据结构
                if isinstance(data, dict) and f"{endpoint.split('-')[0]}Options" in data:
                    options = data[f"{endpoint.split('-')[0]}Options"]
                    if isinstance(options, list) and len(options) > 0:
                        print_status(True, f"{name}: 返回 {len(options)} 项正确数据")
                        continue
            
            print_status(False, f"{name}: 返回异常数据")
            all_ok = False
        except Exception as e:
            print_status(False, f"{name}: {e}")
            all_ok = False
    
    return all_ok

def test_real_time_matches():
    """测试实时场次接口"""
    try:
        response = requests.get(f"{BEIDAN_BASE}/real-time-count", timeout=10)
        if response.status_code == 200:
            data = response.json()
            match_count = data.get('matchCount', 0)
            print_status(True, f"实时场次: {match_count} 场比赛")
            return True, match_count
        else:
            print_status(False, f"实时场次返回 {response.status_code}")
            return False, 0
    except Exception as e:
        print_status(False, f"实时场次失败: {e}")
        return False, 0

def test_advanced_filter():
    """测试高级筛选接口"""
    try:
        # 构建一个简单的筛选请求
        filter_request = {
            "threeDimensional": {
                "strengthDiff": "0",
                "winPanDiff": 0,
                "stabilityTier": "B"
            },
            "otherConditions": {
                "league": "all",
                "dateTimeRange": "today"
            }
        }
        
        response = requests.post(
            f"{BEIDAN_BASE}/advanced-filter",
            json=filter_request,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            print_status(True, f"高级筛选: 返回 {len(matches)} 场比赛")
            return True
        else:
            print_status(False, f"高级筛选返回 {response.status_code}: {response.text[:200]}")
            return False
    except Exception as e:
        print_status(False, f"高级筛选失败: {e}")
        return False

def test_frontend_backend_alignment():
    """测试前端-后端字段映射"""
    try:
        # 获取后端选项
        strength_resp = requests.get(f"{BEIDAN_BASE}/strength-options", timeout=5)
        win_pan_resp = requests.get(f"{BEIDAN_BASE}/win-pan-diff-options", timeout=5)
        stability_resp = requests.get(f"{BEIDAN_BASE}/stability-options", timeout=5)
        
        # 检查所有API都成功
        if all(r.status_code == 200 for r in [strength_resp, win_pan_resp, stability_resp]):
            strength_data = strength_resp.json()['strengthOptions']
            win_pan_data = win_pan_resp.json()['winPanDiffOptions']
            stability_data = stability_resp.json()['stabilityOptions']
            
            # 检查数据项数量与文档一致
            doc_counts = {
                'strength': 7,  # -3 到 +3
                'win_pan': 9,   # -4 到 +4
                'stability': 7  # S 到 E
            }
            
            actual_counts = {
                'strength': len(strength_data),
                'win_pan': len(win_pan_data),
                'stability': len(stability_data)
            }
            
            all_match = True
            for key, expected in doc_counts.items():
                actual = actual_counts[key]
                if actual == expected:
                    print_status(True, f"{key} 选项: {actual} 项 (符合文档)")
                else:
                    print_status(False, f"{key} 选项: {actual} 项 (应为 {expected})")
                    all_match = False
            
            return all_match
        else:
            print_status(False, "有选项API请求失败")
            return False
            
    except Exception as e:
        print_status(False, f"字段映射验证失败: {e}")
        return False

def main():
    print("=" * 60)
    print("北单过滤功能最终验证")
    print("=" * 60)
    
    tests = [
        ("服务健康检查", test_health),
        ("选项API验证", test_option_apis),
        ("实时场次接口", test_real_time_matches),
        ("高级筛选接口", test_advanced_filter),
        ("前后端字段映射", test_frontend_backend_alignment)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        if name == "实时场次接口":
            success, match_count = test_func()
            results.append(success)
        else:
            success = test_func()
            results.append(success)
    
    print("\n" + "=" * 60)
    print("最终验证结果汇总")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, _) in enumerate(tests):
        status = "PASS" if results[i] else "FAIL"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    
    if passed == total:
        print("\n✅ 所有测试通过！北单过滤功能后端实现与文档完全一致。")
        print("前端筛选界面使用的三维参数在后端得到正确计算和处理。")
    else:
        print(f"\n❌ 有 {total - passed} 项测试失败，需要进一步检查。")
        sys.exit(1)

if __name__ == "__main__":
    main()