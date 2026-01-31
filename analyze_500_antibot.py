"""
分析500彩票网的反爬虫机制
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import re

def analyze_antibot_mechanisms():
    # 设置真实浏览器的headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.500.com/',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Cache-Control': 'max-age=0'
    }
    
    url = "https://trade.500.com/jczq/"
    
    print("正在分析500彩票网的反爬虫机制...")
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        # 模拟真实用户访问流程
        print("\n1. 访问主页建立会话...")
        homepage_resp = session.get("https://www.500.com/", timeout=10)
        print(f"   主页状态: {homepage_resp.status_code}")
        
        # 检查是否有cookie设置
        cookies_before = len(session.cookies)
        print(f"   Cookie数量(访问主页后): {cookies_before}")
        
        time.sleep(random.uniform(1, 3))
        
        print("\n2. 访问竞彩足球页面...")
        response = session.get(url, timeout=15)
        print(f"   状态码: {response.status_code}")
        
        cookies_after = len(session.cookies)
        print(f"   Cookie数量(访问后): {cookies_after}")
        
        # 检查响应内容
        content = response.text
        print(f"   页面长度: {len(content)} 字符")
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 检查是否有JavaScript挑战
        scripts = soup.find_all('script')
        print(f"\n3. 分析JavaScript脚本...")
        print(f"   总共 {len(scripts)} 个脚本")
        
        challenge_scripts = []
        for i, script in enumerate(scripts):
            if script.string:
                script_text = script.string.lower()
                
                # 检查是否有反爬虫相关的关键词
                anti_bot_keywords = [
                    'challenge', 'verify', 'captcha', 'security', 'bot', 'robot',
                    'ddos', 'proof', 'work', 'timeout', 'redirect', 'block'
                ]
                
                for keyword in anti_bot_keywords:
                    if keyword in script_text:
                        print(f"   发现反爬虫关键词 '{keyword}' 在脚本 {i+1}")
                        challenge_scripts.append({
                            'index': i+1,
                            'keyword': keyword,
                            'snippet': script.string[:200] + ("..." if len(script.string) > 200 else "")
                        })
        
        if not challenge_scripts:
            print("   未发现明显的反爬虫JavaScript")
        
        # 检查meta标签中的指令
        meta_tags = soup.find_all('meta')
        print(f"\n4. 分析meta标签...")
        print(f"   总共 {len(meta_tags)} 个meta标签")
        
        for meta in meta_tags:
            if 'name' in meta.attrs and 'robots' in meta.attrs.get('name', ''):
                print(f"   Robots指令: {meta.attrs}")
        
        # 检查是否有隐藏或动态加载的内容
        print(f"\n5. 检查隐藏内容...")
        
        # 检查CSS样式中隐藏的内容
        hidden_elements = soup.find_all(lambda tag: tag.name in ['div', 'span', 'p'] and 
                                       any(hide_word in tag.get('style', '') for hide_word in ['display:none', 'visibility:hidden', 'opacity:0']))
        print(f"   隐藏元素数量: {len(hidden_elements)}")
        
        # 检查是否有延迟加载的内容
        lazy_elements = soup.find_all(lambda tag: any(lazy_attr in tag.attrs for lazy_attr in ['data-src', 'data-original']))
        print(f"   延迟加载元素数量: {len(lazy_elements)}")
        
        # 检查页面中是否有比赛相关数据（可能以JSON形式嵌入）
        print(f"\n6. 搜索嵌入的JSON数据...")
        
        # 搜索可能包含比赛数据的script标签
        json_scripts = []
        for script in scripts:
            if script.string and ('match' in script.string.lower() or 'game' in script.string.lower() or 'odds' in script.string.lower()):
                # 搜索JSON数据
                json_matches = re.findall(r'(\{[^{}]*match[^{}]*\}|\[[^\[\]]*\{[^\{\}]*match[^\{\}]*\}[^\[\]]*\])', script.string, re.IGNORECASE)
                if json_matches:
                    json_scripts.extend(json_matches)
        
        print(f"   找到 {len(json_scripts)} 个可能的JSON数据片段")
        
        # 检查页面是否包含动态加载提示
        loading_indicators = soup.find_all(string=re.compile(r'加载|loading|正在获取|请稍候', re.IGNORECASE))
        print(f"   加载提示文本: {len(loading_indicators)} 个")
        
        # 检查是否有iframe（可能用于验证）
        iframes = soup.find_all('iframe')
        print(f"   iframe数量: {len(iframes)}")
        
        for i, iframe in enumerate(iframes):
            src = iframe.get('src', '无src')
            print(f"     iframe {i+1}: {src}")
        
        # 输出一些关键信息供分析
        print(f"\n7. 页面特征摘要:")
        print(f"   - WAF服务器: {response.headers.get('Server', 'Unknown')}")
        print(f"   - 内容编码: {response.encoding}")
        print(f"   - 响应大小: {len(content)} 字节")
        
        # 检查是否包含比赛数据
        match_data_indicators = [
            'match', 'vs', 'team', 'jczq', 'odds', 'bet', '竞彩', '足球'
        ]
        
        found_indicators = {}
        for indicator in match_data_indicators:
            count = content.lower().count(indicator)
            if count > 0:
                found_indicators[indicator] = count
        
        print(f"   - 数据指示器: {found_indicators}")
        
        # 分析响应时间（可能表明服务器在进行额外验证）
        start_time = time.time()
        response = session.get(url, timeout=10)
        end_time = time.time()
        
        print(f"   - 二次请求响应时间: {end_time - start_time:.2f}秒")
        
        return {
            'status_code': response.status_code,
            'has_challenge_scripts': len(challenge_scripts) > 0,
            'hidden_elements': len(hidden_elements),
            'json_scripts': len(json_scripts),
            'data_indicators': found_indicators,
            'cookies_before': cookies_before,
            'cookies_after': cookies_after
        }
        
    except Exception as e:
        print(f"分析过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = analyze_antibot_mechanisms()
    if result:
        print(f"\n=== 分析结果 ===")
        print(f"状态码: {result['status_code']}")
        print(f"包含挑战脚本: {result['has_challenge_scripts']}")
        print(f"隐藏元素数: {result['hidden_elements']}")
        print(f"JSON脚本数: {result['json_scripts']}")
        print(f"数据指示器: {result['data_indicators']}")
        print(f"Cookies数量变化: {result['cookies_before']} -> {result['cookies_after']}")