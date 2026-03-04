"""
测试从89ip.cn获取IP的功能
"""
import time
from crawler.ip_proxy import IPProxyPool


def test_89ip_integration():
    """测试89ip集成"""
    print("="*60)
    print("测试: 89ip.cn IP获取集成")
    print("="*60)
    
    # 创建IP代理池
    pool = IPProxyPool(min_proxy_count=5, max_proxy_count=100)
    
    # 获取初始状态
    initial_status = pool.get_proxy_count()
    print(f"初始IP池状态: 总计={initial_status['total']}, 活跃={initial_status['active']}, 失败={initial_status['failed']}")
    
    # 从89ip.cn获取IP
    print("\n[INSPECT] 开始从89ip.cn获取IP...")
    start_time = time.time()
    
    try:
        # 获取前2页的IP，不进行验证（为了快速测试）
        added_count = pool.fetch_ips_from_89ip(pages=2, validate=False)
        elapsed = time.time() - start_time
        
        print(f"[OK] 从89ip.cn获取完成，耗时: {elapsed:.2f}秒")
        print(f"[TREND] 成功添加: {added_count} 个IP")
        
        # 获取更新后的状态
        updated_status = pool.get_proxy_count()
        print(f"[ANALYTICS] 更新后IP池状态: 总计={updated_status['total']}, 活跃={updated_status['active']}, 失败={updated_status['failed']}")
        
        # 显示新增的IP
        if added_count > 0:
            print(f"\n[LOG] 新增IP列表:")
            new_proxies = pool.proxies[-added_count:]  # 获取最新添加的代理
            for i, proxy in enumerate(new_proxies):
                print(f"   {i+1}. {proxy.address}")
        
        # 如果添加了IP，可以尝试验证几个
        if added_count > 0:
            print(f"\n[INSPECT] 验证前3个IP的可用性...")
            verified_count = 0
            for proxy in pool.proxies[-min(3, added_count):]:  # 验证最后3个
                print(f"   验证 {proxy.address}...")
                if pool.validate_proxy(proxy):
                    pool.mark_proxy_good(proxy)
                    verified_count += 1
                    print(f"   [OK] {proxy.address} 验证成功")
                else:
                    pool.mark_proxy_failed(proxy)
                    print(f"   [ERROR] {proxy.address} 验证失败")
            
            print(f"[TREND] 验证结果: {verified_count}/3 个IP可用")
            
            # 更新最终状态
            final_status = pool.get_proxy_count()
            print(f"[ANALYTICS] 最终IP池状态: 总计={final_status['total']}, 活跃={final_status['active']}, 失败={final_status['failed']}")
    
    except Exception as e:
        print(f"[ERROR] 获取IP时出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 关闭IP池
    pool.close()
    print(f"\n[FINISH] 测试完成")


def test_continuous_fetch():
    """测试连续获取IP"""
    print("\n" + "="*60)
    print("测试: 连续获取IP")
    print("="*60)
    
    pool = IPProxyPool(min_proxy_count=5, max_proxy_count=200)
    
    # 初始状态
    initial_status = pool.get_proxy_count()
    print(f"初始IP池状态: {initial_status}")
    
    # 连续获取多次
    total_added = 0
    for i in range(2):  # 获取2次
        print(f"\n第 {i+1} 次获取...")
        added = pool.fetch_ips_from_89ip(pages=1, validate=False)
        total_added += added
        print(f"本次添加: {added} 个IP")
        
        current_status = pool.get_proxy_count()
        print(f"当前状态: {current_status}")
        
        # 短暂等待
        time.sleep(2)
    
    print(f"\n[TREND] 总共添加了 {total_added} 个IP")
    
    # 最终状态
    final_status = pool.get_proxy_count()
    print(f"最终IP池状态: {final_status}")
    
    pool.close()
    print(f"\n[FINISH] 连续获取测试完成")


def main():
    """主函数"""
    print("[ROCKET] 开始测试89ip.cn IP获取功能")
    
    # 运行基本测试
    test_89ip_integration()
    
    # 运行连续获取测试
    test_continuous_fetch()
    
    print("\n[SUCCESS] 所有测试完成！")


if __name__ == "__main__":
    main()