"""
检查500彩票网的响应头部和内容，分析反爬虫机制
"""
import requests
from bs4 import BeautifulSoup
import time
import random

def check_500_headers():
    # 设置不同的User-Agent来模拟真实访问
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    print("正在检查500彩票网的响应头部...")
    
    try:
        # 先访问主页
        homepage_url = "https://www.500.com/"
        print(f"1. 访问主页: {homepage_url}")
        response_home = requests.get(homepage_url, headers=headers, timeout=10)
        print(f"   状态码: {response_home.status_code}")
        print(f"   响应头部: Server={response_home.headers.get('Server')}, Set-Cookie={bool(response_home.headers.get('Set-Cookie'))}")
        
        # 等待一段时间
        time.sleep(random.uniform(1, 3))
        
        # 访问竞彩足球页面
        url = "https://trade.500.com/jczq/"
        print(f"\n2. 访问竞彩足球页面: {url}")
        
        # 使用session保持会话
        session = requests.Session()
        session.headers.update(headers)
        
        # 先访问页面
        response = session.get(url, timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应头部: Server={response.headers.get('Server')}, Content-Type={response.headers.get('Content-Type')}")
        print(f"   Set-Cookie数量: {len(response.cookies)}")
        
        # 检查是否有反爬虫机制
        content = response.text.lower()
        if 'cloudflare' in content or 'ddos' in content or 'security' in content or 'verify' in content:
            print("   检测到可能的反爬虫机制")
        else:
            print("   未明显检测到反爬虫机制")
        
        # 检查页面长度
        print(f"   页面长度: {len(content)} 字符")
        
        # 检查是否有JavaScript重定向或验证代码
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        print(f"   JavaScript脚本数量: {len(scripts)}")
        
        # 检查特定的反爬虫脚本
        suspicious_scripts = []
        for script in scripts:
            if script.string:
                if 'captcha' in script.string.lower() or 'verify' in script.string.lower() or 'challenge' in script.string.lower():
                    suspicious_scripts.append(script.string[:100] + "...")
        
        if suspicious_scripts:
            print(f"   发现可疑脚本: {len(suspicious_scripts)} 个")
            for i, script in enumerate(suspicious_scripts):
                print(f"     {i+1}. {script}")
        else:
            print("   未发现明显的反爬虫脚本")
        
        # 检查是否有iframe或隐藏元素
        iframes = soup.find_all('iframe')
        hidden_divs = soup.find_all(lambda tag: tag.name == 'div' and 'display:none' in tag.get('style', ''))
        print(f"   iframe数量: {len(iframes)}, 隐藏div数量: {len(hidden_divs)}")
        
        # 检查页面结构
        tables = soup.find_all('table')
        divs = soup.find_all('div')
        print(f"   表格数量: {len(tables)}, div数量: {len(divs)}")
        
        # 检查是否有比赛相关的class
        match_classes = ['jczq', 'match', 'vs', 'team', 'odds', 'time']
        found_classes = []
        for class_name in match_classes:
            elements = soup.find_all(class_=lambda x: x and class_name in x.lower())
            if elements:
                found_classes.append((class_name, len(elements)))
        
        print(f"   潜在比赛相关元素: {found_classes}")
        
        # 检查是否有AJAX请求的迹象
        ajax_indicators = ['ajax', 'fetch', 'xmlhttprequest', 'post', 'get']
        ajax_found = []
        for script in scripts:
            if script.string:
                for indicator in ajax_indicators:
                    if indicator in script.string.lower():
                        ajax_found.append(indicator)
                        break
        
        print(f"   AJAX请求指示器: {list(set(ajax_found))}")
        
        return response.status_code, content, session
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None, None, None

if __name__ == "__main__":
    check_500_headers()