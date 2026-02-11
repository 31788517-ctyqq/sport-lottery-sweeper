#!/usr/bin/env python3
"""
诊断导入问题
"""
import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Python路径:")
for path in sys.path:
    print(f"  {path}")

print("\n1. 尝试导入 backend.core.exceptions 模块...")
try:
    import backend.core.exceptions
    print("   成功!")
    print(f"   模块位置: {backend.core.exceptions.__file__}")
except Exception as e:
    print(f"   失败: {e}")
    traceback.print_exc()

print("\n2. 尝试导入 backend.api.v1.matches 模块...")
try:
    import backend.api.v1.matches
    print("   成功!")
except Exception as e:
    print(f"   失败: {e}")
    traceback.print_exc()

print("\n3. 尝试直接导入 match_service.py 中使用的异常...")
try:
    from backend.core.exceptions import ValidationException, NotFoundException, BusinessException
    print("   成功!")
except Exception as e:
    print(f"   失败: {e}")
    traceback.print_exc()

print("\n4. 检查 backend.core.exceptions 中的导入...")
try:
    import backend.utils.exceptions
    print("   backend.utils.exceptions 导入成功")
    print(f"   类列表: {backend.utils.exceptions.__all__}")
except Exception as e:
    print(f"   失败: {e}")

print("\n5. 尝试重现完整的导入链...")
try:
    # 模拟启动时的导入顺序
    print("   从 backend.api.v1.__init__ 导入...")
    from backend.api.v1 import __init__ as v1_init
    print("   成功!")
except Exception as e:
    print(f"   失败: {e}")
    traceback.print_exc()

print("\n6. 检查是否存在循环导入...")
try:
    # 检查 matches 的导入依赖
    import inspect
    import backend.api.v1.matches
    print("   matches 导入成功，检查其导入...")
    source = inspect.getsource(backend.api.v1.matches)
    # 查找 import 语句
    import_lines = [line.strip() for line in source.split('\n') if line.strip().startswith('import') or line.strip().startswith('from')]
    for line in import_lines[:10]:  # 只显示前10个
        print(f"     {line}")
except Exception as e:
    print(f"   失败: {e}")

print("\n7. 检查文件是否存在...")
core_exceptions_path = os.path.join(os.path.dirname(__file__), 'backend', 'core', 'exceptions.py')
print(f"   {core_exceptions_path} 存在: {os.path.exists(core_exceptions_path)}")

utils_exceptions_path = os.path.join(os.path.dirname(__file__), 'backend', 'utils', 'exceptions.py')
print(f"   {utils_exceptions_path} 存在: {os.path.exists(utils_exceptions_path)}")