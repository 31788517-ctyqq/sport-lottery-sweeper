"""
验证异步测试配置的脚本
"""
import subprocess
import sys
import os

def run_tests():
    """运行异步测试验证"""
    print("[INSPECT] 验证异步测试配置...")
    
    # 首先检查pytest是否已安装
    try:
        import pytest
        print("[OK] pytest 已安装")
    except ImportError:
        print("[ERROR] pytest 未安装，请先运行: pip install pytest pytest-asyncio")
        return False
    
    try:
        import pytest_asyncio
        print("[OK] pytest-asyncio 已安装")
    except ImportError:
        print("[ERROR] pytest-asyncio 未安装，请运行: pip install pytest-asyncio")
        return False
    
    # 尝试运行一个简单的异步测试
    test_code = '''
import pytest
import asyncio

@pytest.mark.asyncio
async def test_basic_async():
    await asyncio.sleep(0.01)  # 模拟异步操作
    assert 1 == 1

if __name__ == "__main__":
    asyncio.run(test_basic_async())
'''
    
    # 写入临时测试文件
    with open("temp_async_test.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    try:
        # 使用pytest运行测试
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "temp_async_test.py::test_basic_async",
            "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("[OK] 异步测试配置验证成功！")
            print("输出:", result.stdout.strip())
        else:
            print("[ERROR] 异步测试配置有问题")
            print("错误输出:", result.stderr.strip())
            return False
            
    finally:
        # 清理临时文件
        if os.path.exists("temp_async_test.py"):
            os.remove("temp_async_test.py")
    
    print("\n[OK] 所有异步测试配置检查完成！")
    print("现在您的测试环境已准备好运行异步测试。")
    return True

if __name__ == "__main__":
    run_tests()