#!/usr/bin/env python3
"""
检查所有运行中的服务端口
"""
import requests
import sys
from typing import Optional, Dict, Any

def check_port(port: int, path: str = "") -> Optional[Dict[str, Any]]:
    """检查指定端口的服务"""
    url = f"http://localhost:{port}{path}"
    
    try:
        response = requests.get(url, timeout=3, allow_redirects=True)
        
        # 尝试获取标题
        title = None
        content_type = response.headers.get('content-type', '')
        
        if 'text/html' in content_type:
            html = response.text.lower()
            if '<title>' in html:
                start = html.find('<title>') + 7
                end = html.find('</title>', start)
                if start < end:
                    title = response.text[start:end].strip()
        
        return {
            'port': port,
            'status_code': response.status_code,
            'content_type': content_type,
            'title': title,
            'url': url,
            'headers': dict(response.headers),
            'text_preview': response.text[:200] if response.text else ''
        }
    except Exception as e:
        return None

def main():
    print("=" * 80)
    print("当前运行的服务端口检查")
    print("=" * 80)
    
    # 已知的端口列表
    ports_to_check = [
        3000,  # 前端
        8000,  # 后端
        8001,  # 其他后端实例
        8080,  # httpd服务
        80,    # nginx
        443,   # nginx ssl
        5555,  # flower监控
        5432,  # postgres
        6379,  # redis
        27017, # mongo
    ]
    
    running_services = []
    
    for port in ports_to_check:
        print(f"\n检查端口 {port}...")
        
        # 尝试根路径
        result = check_port(port)
        if result:
            running_services.append(result)
            print(f"  [OK] 服务运行")
            print(f"    状态码: {result['status_code']}")
            if result['content_type']:
                print(f"    内容类型: {result['content_type']}")
            if result['title']:
                print(f"    标题: {result['title']}")
            print(f"    URL: {result['url']}")
        else:
            print(f"  [NO] 无服务")
    
    print(f"\n" + "=" * 80)
    print("总结：当前运行的服务")
    print("=" * 80)
    
    if not running_services:
        print("没有检测到运行的服务")
        return
    
    # 分类显示
    frontend = []
    backend = []
    database = []
    other = []
    
    for service in running_services:
        port = service['port']
        content_type = service['content_type']
        
        if port == 3000:
            frontend.append(service)
        elif port in [8000, 8001, 8080]:
            backend.append(service)
        elif port in [5432, 6379, 27017]:
            database.append(service)
        else:
            other.append(service)
    
    print(f"\n前端服务 ({len(frontend)}个):")
    for service in frontend:
        print(f"  • 端口 {service['port']}: {service['url']}")
        if service['title']:
            print(f"     标题: {service['title']}")
    
    print(f"\n后端API服务 ({len(backend)}个):")
    for service in backend:
        print(f"  • 端口 {service['port']}: {service['url']}")
        if 'json' in service['content_type'] or 'api' in service['text_preview'].lower():
            print(f"    看起来是API服务")
        if service['title']:
            print(f"     标题: {service['title']}")
    
    print(f"\n数据库服务 ({len(database)}个):")
    for service in database:
        print(f"  • 端口 {service['port']}: {service['url']}")
    
    print(f"\n其他服务 ({len(other)}个):")
    for service in other:
        print(f"  • 端口 {service['port']}: {service['url']}")
    
    print(f"\n" + "=" * 80)
    print("访问建议:")
    print("=" * 80)
    print("1. 前端开发界面: http://localhost:3000")
    print("2. 后端API文档 (端口8000): http://localhost:8000/docs")
    print("3. 后端API文档 (端口8001): http://localhost:8001/docs")
    print("4. 其他服务 (端口8080): http://localhost:8080")

if __name__ == "__main__":
    main()