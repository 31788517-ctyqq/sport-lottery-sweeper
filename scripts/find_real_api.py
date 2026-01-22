"""查找竞彩网真实API"""
import asyncio
import sys
import io
import json
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import aiohttp


async def test_webapi():
    """测试webapi.sporttery.cn的各种端点"""
    print("="*80)
    print("测试 webapi.sporttery.cn API")
    print("="*80)
    
    # 可能的API端点
    apis = [
        # 足球相关
        "https://webapi.sporttery.cn/gateway/jc/football/getMatchList.qry",
        "https://webapi.sporttery.cn/gateway/jc/football/getMatchDetail.qry",
        "https://webapi.sporttery.cn/gateway/football/getMatchResultList.qry",
        "https://webapi.sporttery.cn/gateway/jc/football/list.qry",
        "https://webapi.sporttery.cn/gateway/jc/football/match.qry",
        
        # 通用接口
        "https://webapi.sporttery.cn/gateway/jc/getMatchList",
        "https://webapi.sporttery.cn/api/match/list",
        "https://webapi.sporttery.cn/api/football/matches",
        
        # 静态资源
        "https://static.sporttery.cn/res_1_0/jcw/default/index/sy_zxkj.js",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.sporttery.cn/',
        'Origin': 'https://www.sporttery.cn',
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for api in apis:
            try:
                print(f"\n测试: {api}")
                timeout = aiohttp.ClientTimeout(total=10)
                
                async with session.get(api, timeout=timeout) as resp:
                    print(f"  状态码: {resp.status}")
                    
                    if resp.status == 200:
                        content_type = resp.headers.get('Content-Type', '')
                        print(f"  内容类型: {content_type}")
                        
                        if 'json' in content_type:
                            try:
                                data = await resp.json()
                                print(f"  ✅ JSON响应")
                                print(f"  数据键: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                                
                                # 显示部分数据
                                if isinstance(data, dict):
                                    for key, value in list(data.items())[:5]:
                                        print(f"    {key}: {str(value)[:100]}")
                                
                                # 保存
                                filename = api.split('/')[-1] + '.json'
                                with open(f'debug/{filename}', 'w', encoding='utf-8') as f:
                                    json.dump(data, f, ensure_ascii=False, indent=2)
                                print(f"  💾 已保存: debug/{filename}")
                                
                            except Exception as e:
                                print(f"  ⚠️  JSON解析失败: {e}")
                        else:
                            text = await resp.text()
                            print(f"  内容长度: {len(text)}")
                            if len(text) < 500:
                                print(f"  内容: {text[:200]}")
                    
                    elif resp.status == 404:
                        print(f"  ❌ 404 - 接口不存在")
                    elif resp.status == 403:
                        print(f"  ❌ 403 - 禁止访问")
                    else:
                        print(f"  ⚠️  状态码: {resp.status}")
                        
            except asyncio.TimeoutError:
                print(f"  ❌ 超时")
            except Exception as e:
                print(f"  ❌ 错误: {type(e).__name__}: {e}")


async def test_with_params():
    """测试带参数的API"""
    print("\n" + "="*80)
    print("测试带参数的API")
    print("="*80)
    
    # 测试可能的API参数
    from_date = datetime.now().strftime('%Y-%m-%d')
    to_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    
    test_cases = [
        {
            'url': 'https://webapi.sporttery.cn/gateway/jc/football/getMatchList.qry',
            'params': {
                'poolCode': 'had',  # 胜平负
                'startDate': from_date,
                'endDate': to_date,
            }
        },
        {
            'url': 'https://webapi.sporttery.cn/gateway/jc/football/getMatchList.qry',
            'params': {
                'poolCode': 'hhad',  # 让球胜平负
            }
        },
        {
            'url': 'https://webapi.sporttery.cn/gateway/jc/football/list.qry',
            'params': {}
        },
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.sporttery.cn/',
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for case in test_cases:
            try:
                url = case['url']
                params = case['params']
                print(f"\n测试: {url}")
                print(f"  参数: {params}")
                
                timeout = aiohttp.ClientTimeout(total=10)
                async with session.get(url, params=params, timeout=timeout) as resp:
                    print(f"  状态码: {resp.status}")
                    
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            print(f"  ✅ 成功获取JSON")
                            
                            # 分析响应结构
                            if isinstance(data, dict):
                                print(f"  响应键: {list(data.keys())}")
                                
                                # 查找比赛数据
                                for key in ['data', 'matchList', 'list', 'matches', 'result']:
                                    if key in data:
                                        value = data[key]
                                        print(f"  找到 '{key}': {type(value)}")
                                        if isinstance(value, list):
                                            print(f"    列表长度: {len(value)}")
                                            if len(value) > 0:
                                                print(f"    第一项: {list(value[0].keys()) if isinstance(value[0], dict) else type(value[0])}")
                                
                                # 保存完整响应
                                filename = f"api_test_{datetime.now().strftime('%H%M%S')}.json"
                                with open(f'debug/{filename}', 'w', encoding='utf-8') as f:
                                    json.dump(data, f, ensure_ascii=False, indent=2)
                                print(f"  💾 已保存: debug/{filename}")
                                
                        except Exception as e:
                            text = await resp.text()
                            print(f"  ⚠️  响应内容: {text[:200]}")
                    else:
                        print(f"  ❌ 状态码: {resp.status}")
                        text = await resp.text()
                        print(f"  错误信息: {text[:200]}")
                        
            except Exception as e:
                print(f"  ❌ 错误: {e}")


async def analyze_js_files():
    """分析JavaScript文件查找API端点"""
    print("\n" + "="*80)
    print("分析JavaScript文件")
    print("="*80)
    
    js_urls = [
        "https://static.sporttery.cn/res_1_0/common/js/commonV1.js",
        "https://static.sporttery.cn/res_1_0/jcw/default/index/sy_zxkj.js",
    ]
    
    async with aiohttp.ClientSession() as session:
        for js_url in js_urls:
            try:
                print(f"\n获取: {js_url}")
                async with session.get(js_url) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        print(f"  ✅ 文件大小: {len(text)} 字符")
                        
                        # 查找API端点
                        import re
                        api_patterns = [
                            r'https?://[^\s\'"]+/api/[^\s\'"]+',
                            r'https?://webapi\.sporttery\.cn[^\s\'"]+',
                            r'/gateway/[^\s\'"]+',
                        ]
                        
                        found_apis = set()
                        for pattern in api_patterns:
                            matches = re.findall(pattern, text)
                            found_apis.update(matches)
                        
                        if found_apis:
                            print(f"  找到 {len(found_apis)} 个API端点:")
                            for api in sorted(found_apis)[:10]:
                                print(f"    - {api}")
                        else:
                            print(f"  未找到API端点")
                            
                    else:
                        print(f"  ❌ 状态码: {resp.status}")
                        
            except Exception as e:
                print(f"  ❌ 错误: {e}")


async def main():
    print("\n" + "🔍"*40)
    print("查找竞彩网真实API")
    print("🔍"*40 + "\n")
    
    try:
        # 测试各种API端点
        await test_webapi()
        
        # 测试带参数的API
        await test_with_params()
        
        # 分析JS文件
        await analyze_js_files()
        
        print("\n" + "="*80)
        print("✅ 测试完成")
        print("="*80)
        
        print("\n💡 下一步:")
        print("  1. 查看 debug/ 目录下保存的JSON文件")
        print("  2. 找到成功返回数据的API")
        print("  3. 更新 backend/scrapers/sources/sporttery.py")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
