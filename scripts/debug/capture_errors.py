#!/usr/bin/env python3
"""
捕获测试错误信息
"""
import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr

# 导入测试类
sys.path.insert(0, '.')
from backend.tests.unit.api.admin.test_data_source import TestDataSourceAPI

# 创建测试实例
test_instance = TestDataSourceAPI()

# 运行setup fixture
print("运行setup fixture...")
try:
    # 获取生成器
    gen = test_instance.setup()
    next(gen)  # 前进到yield
    print("setup fixture 成功")
except Exception as e:
    print(f"setup fixture 失败: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)

# 测试特定方法
test_methods = [
    'test_get_data_sources_success',
    'test_get_data_sources_with_filters',
    'test_get_single_data_source_success',
    'test_create_data_source_success',
    'test_batch_delete_data_sources_success',
    'test_batch_delete_data_sources_empty_list',
    'test_batch_health_check_success'
]

for method_name in test_methods:
    print(f"\n{'='*60}")
    print(f"测试方法: {method_name}")
    print('='*60)
    
    try:
        method = getattr(test_instance, method_name)
        
        # 捕获输出
        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            try:
                method()
                print(f"✓ 测试通过")
            except AssertionError as e:
                print(f"✗ 断言失败: {e}")
                print(f"  详细错误:")
                traceback.print_exc()
            except Exception as e:
                print(f"✗ 异常: {type(e).__name__}: {e}")
                traceback.print_exc()
        
        output = f.getvalue()
        if output:
            print(f"输出: {output[:500]}...")
            
    except Exception as e:
        print(f"调用测试方法失败: {type(e).__name__}: {e}")
        traceback.print_exc()

# 清理
print("\n清理...")
try:
    next(gen)  # 执行teardown
    print("清理成功")
except StopIteration:
    print("生成器已结束")
except Exception as e:
    print(f"清理失败: {e}")