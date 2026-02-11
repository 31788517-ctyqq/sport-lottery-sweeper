import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告（如果有的话）
urllib3.disable_warnings(InsecureRequestWarning)

def test_api_endpoint():
    # 数据源DS041的URL
    url = "https://m.100qiu.com/api/dcListBasic?dateTime=26011"
    
    print(f"正在测试API端点: {url}")
    print("="*60)
    
    try:
        # 设置请求头，模拟真实浏览器请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://m.100qiu.com/'
        }
        
        # 发送请求
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应头部: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API端点可访问")
            print(f"响应内容预览: {response.text[:500]}...")  # 只显示前500字符
        else:
            print(f"❌ API端点访问失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    test_api_endpoint()