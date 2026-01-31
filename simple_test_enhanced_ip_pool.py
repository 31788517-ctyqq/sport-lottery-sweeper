"""
简化测试脚本：验证增强IP池系统核心功能
"""
from crawler.integrated_ip_pool import IntegratedIPPool
from crawler.ip_proxy import IPProxyPool


def test_basic_integration():
    """测试基本集成"""
    print("🧪 开始测试增强IP池系统...")
    
    # 测试1: 创建集成IP池
    print("\n1️⃣  测试创建集成IP池...")
    try:
        pool = IntegratedIPPool({
            'min_quality_score': 0.2,
            'auto_expand_enabled': False,
            'monitoring_interval': 30
        })
        print("✅ 集成IP池创建成功")
    except Exception as e:
        print(f"❌ 集成IP池创建失败: {e}")
        return False
    
    # 测试2: 添加代理
    print("\n2️⃣  测试添加代理...")
    try:
        pool.add_proxy("127.0.0.1", 8080)
        pool.add_proxy("192.168.1.1", 8080)
        print("✅ 代理添加成功")
    except Exception as e:
        print(f"❌ 代理添加失败: {e}")
        return False
    
    # 测试3: 获取状态
    print("\n3️⃣  测试获取状态...")
    try:
        status = pool.get_status()
        print(f"✅ 状态获取成功 - 总代理数: {status['pool_status']['total_proxies']}")
    except Exception as e:
        print(f"❌ 状态获取失败: {e}")
        return False
    
    # 测试4: 创建增强版代理池
    print("\n4️⃣  测试增强版代理池...")
    try:
        enhanced_pool = IPProxyPool(min_proxy_count=3, max_proxy_count=20)
        sample_proxies = ["127.0.0.1:8080", "192.168.1.10:8080"]
        added = enhanced_pool.add_proxies_from_list(sample_proxies)
        print(f"✅ 增强版代理池创建成功 - 添加代理数: {added}")
        enhanced_pool.close()
    except Exception as e:
        print(f"❌ 增强版代理池测试失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！增强IP池系统功能正常")
    return True


def show_system_features():
    """展示系统特性"""
    print("\n🌟 增强IP池系统特性:")
    print("   • IP质量评估系统 - 多维度评估IP质量")
    print("   • 智能轮换策略 - 自适应代理选择算法")
    print("   • 实时监控系统 - 持续监控IP池健康状况")
    print("   • 自动扩展机制 - 智能检测并补充IP")
    print("   • 与现有系统集成 - 无缝集成到现有架构")
    print("   • 反检测策略 - 模拟真实用户行为")
    print("   • 详细报告 - 提供全面的监控报告")


if __name__ == "__main__":
    print("🚀 验证增强IP池系统")
    print("="*50)
    
    success = test_basic_integration()
    if success:
        show_system_features()
        print("\n✅ 增强IP池系统验证成功！")
    else:
        print("\n❌ 增强IP池系统验证失败！")