"""
简单测试89ip.cn IP获取功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.ip_fetcher_89ip import Ip89Fetcher

def test_89ip_fetcher():
    """测试89ip获取器"""
    print("="*60)
    print("测试: 89ip.cn IP获取器")
    print("="*60)
    
    fetcher = Ip89Fetcher()
    
    # 尝试获取第一页的IP
    print("正在获取第一页IP...")
    soup = fetcher.fetch_page(1)
    
    if soup:
        print("✅ 成功获取页面")
        
        # 解析IP列表
        ips = fetcher.parse_ip_list(soup)
        
        print(f"解析到 {len(ips)} 个IP地址:")
        for i, (ip, port) in enumerate(ips[:10]):  # 只显示前10个
            print(f"  {i+1}. {ip}:{port}")
        
        if len(ips) > 10:
            print(f"  ... 还有 {len(ips)-10} 个IP")
    else:
        print("❌ 获取页面失败")
        print("可能原因:")
        print("  - 网络连接问题")
        print("  - 89ip.cn网站结构发生变化")
        print("  - 网站有反爬虫机制")
    
    print("\n测试完成")


def test_ip_validation():
    """测试IP验证功能"""
    print("\n" + "="*60)
    print("测试: IP验证功能")
    print("="*60)
    
    fetcher = Ip89Fetcher()
    
    # 测试一些示例IP（这些IP可能不可用，仅用于测试验证功能）
    test_ips = [
        ("8.8.8.8", "53"),   # Google DNS，通常不可作为HTTP代理
        ("1.1.1.1", "80"),    # Cloudflare DNS，通常不可作为HTTP代理
    ]
    
    for ip, port in test_ips:
        print(f"验证 {ip}:{port} ...")
        try:
            is_valid = fetcher.validate_ip_port(ip, port, timeout=5)
            print(f"  结果: {'✅ 可用' if is_valid else '❌ 不可用'}")
        except Exception as e:
            print(f"  错误: {str(e)}")
    
    print("\nIP验证测试完成")


if __name__ == "__main__":
    test_89ip_fetcher()
    test_ip_validation()