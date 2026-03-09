"""
探索竞彩网API的脚本
"""
import requests
import json
from datetime import datetime, timedelta


def explore_sporttery_api():
    """
    探索竞彩网的API端点和参数
    """
    print("探索竞彩网API端点...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.sporttery.cn/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Origin': 'https://www.sporttery.cn'
    }
    
    # 尝试不同的API端点和参数组合
    base_url = "https://webapi.sporttery.cn"
    
    # 根据公开信息，竞彩足球的API可能使用如下端点
    possible_endpoints = [
        "/gateway/jc/football/home/multiMatchRecommendCompList.do",
        "/gateway/jc/football/matchLive/roundInfoList.do",
        "/gateway/jc/football/info/getHighlightList.do",
        "/gateway/jc/football/schedule/basketballScheduleList.do",  # 这个是篮球，但可能有相似的足球端点
        "/gateway/jc/football/schedule/footballScheduleList.do",    # 猜测的足球端点
        "/gateway/jc/football/data/matchMainPage.do",              # 猜测的端点
        "/gateway/jc/football/matchMainPage.do",                   # 猜测的端点
        "/gateway/jc/zq/weekOddsDetail.do",                       # 之前尝试过的
        "/gateway/jc/zq/scheduleList.do",                         # 猜测的端点
        "/gateway/jc/match/scheduleList.do",                      # 猜测的端点
    ]
    
    # 尝试一些可能的参数
    possible_params = [
        {'date': (datetime.now() + timedelta(days=0)).strftime('%Y-%m-%d'), 'provinceId': ''},
        {'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'), 'provinceId': ''},
        {'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'), 'provinceId': ''},
        {'issueNumber': '0', 'playType': '0'},  # 期次和玩法类型
        {'playType': '0', 'issueFlag': '0'},    # 玩法类型和期次标志
        {'playType': '0'},                      # 仅玩法类型
        {'date': datetime.now().strftime('%Y-%m-%d')},  # 仅日期
        {}  # 空参数
    ]
    
    for endpoint in possible_endpoints:
        print(f"\n尝试端点: {endpoint}")
        
        for params in possible_params:
            print(f"  参数: {params}")
            
            try:
                response = requests.get(base_url + endpoint, headers=headers, params=params, timeout=10)
                
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  响应结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        
                        # 检查是否包含错误信息
                        if 'success' in data and data['success'] is False:
                            print(f"  错误信息: {data.get('errorMessage', 'Unknown error')}")
                        elif 'errorCode' in data and data['errorCode'] != '0':
                            print(f"  错误代码: {data.get('errorCode', 'Unknown error')}, 信息: {data.get('errorMessage', 'No message')}")
                        elif 'result' in data or ('value' in data and data['value']):
                            print("  ✅ 找到可能的有效数据!")
                            
                            # 打印部分数据内容
                            if 'result' in data:
                                print(f"  Result keys: {list(data['result'].keys()) if isinstance(data['result'], dict) else 'Not a dict'}")
                            if 'value' in data:
                                print(f"  Value keys: {list(data['value'].keys()) if isinstance(data['value'], dict) else 'Not a dict'}")
                                
                            return endpoint, params, data
                        else:
                            print("  数据格式不符合预期")
                            
                    except json.JSONDecodeError:
                        print(f"  非JSON响应: {response.text[:200]}...")
                else:
                    print(f"  请求失败")
                    
            except requests.RequestException as e:
                print(f"  请求异常: {str(e)}")
            except Exception as e:
                print(f"  处理响应时异常: {str(e)}")
    
    print("\n未找到有效的API端点")
    return None, None, None


if __name__ == "__main__":
    endpoint, params, data = explore_sporttery_api()
    
    if endpoint:
        print(f"\n找到可能的API端点: {endpoint}")
        print(f"参数: {params}")
        print(f"响应示例: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
    else:
        print("\n未能找到有效的API端点")