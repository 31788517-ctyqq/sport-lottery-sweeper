"""
启动时间基准测试脚本
比较不同启动方式的性能差异
"""
import time
import subprocess
import sys
import os
from datetime import datetime

def benchmark_startup(script_name, description):
    """基准测试指定启动脚本的启动时间"""
    print(f"\n🧪 测试: {description}")
    print(f"📄 脚本: {script_name}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # 运行脚本并捕获输出
        cmd = [sys.executable, f"scripts/{script_name}.py"]
        env = os.environ.copy()
        # 设置超时时间以避免长时间等待
        result = subprocess.run(cmd, timeout=10, capture_output=True, text=True, cwd=".", env=env)
        
        total_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ 状态: 成功启动")
            print(f"⏱️  启动时间: {total_time:.2f}秒")
        else:
            print(f"❌ 状态: 启动失败")
            print(f"⏱️  尝试时间: {total_time:.2f}秒")
            print(f"📝 错误输出: {result.stderr[:200]}...")  # 只显示前200字符
            
    except subprocess.TimeoutExpired:
        total_time = time.time() - start_time
        print(f"⏱️  启动时间: {total_time:.2f}秒")
        print(f"⏰ 状态: 超时 (超过10秒，但可能仍在后台运行)")
    except Exception as e:
        total_time = time.time() - start_time
        print(f"❌ 状态: 异常 - {e}")
        print(f"⏱️  尝试时间: {total_time:.2f}秒")

def main():
    """运行基准测试"""
    print("🚀 竞彩足球扫盘系统 - 启动时间基准测试")
    print("="*60)
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试不同的启动脚本
    test_scripts = [
        ("optimal_start", "最优启动脚本 (精简版)"),
        ("fast_start", "快速启动脚本"), 
        ("quick_start", "快速启动脚本 (原始版)"),
    ]
    
    results = []
    
    for script, desc in test_scripts:
        try:
            benchmark_startup(script, desc)
            # 简单延时避免资源冲突
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n⚠️  测试被用户中断")
            break
        except Exception as e:
            print(f"\n⚠️  测试 {script} 时出错: {e}")
    
    print("\n" + "="*60)
    print("📈 基准测试完成")
    print("💡 性能优化建议:")
    print("   1. 使用精简版启动脚本进行开发")
    print("   2. 延迟导入非必需模块")
    print("   3. 使用内存缓存减少重复计算")
    print("   4. 按需加载功能模块")


if __name__ == "__main__":
    main()