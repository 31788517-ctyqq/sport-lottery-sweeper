#!/usr/bin/env python
"""测试修复的导入问题"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("测试导入 Match 从 backend.models.match...")
try:
    from backend.models.match import Match
    print("✓ 成功从 backend.models.match 导入 Match")
except ImportError as e:
    print(f"✗ 失败: {e}")

print("\n测试导入 Match 从 backend.schemas.match...")
try:
    from backend.schemas.match import Match
    print("✓ 成功从 backend.schemas.match 导入 Match")
except ImportError as e:
    print(f"✗ 失败: {e}")

print("\n测试导入 UnifiedResponse...")
try:
    from backend.utils.response import UnifiedResponse
    print("✓ 成功导入 UnifiedResponse")
except ImportError as e:
    print(f"✗ 失败: {e}")

print("\n测试导入 DrawFeature...")
try:
    from backend.models.draw_feature import DrawFeature
    print("✓ 成功导入 DrawFeature")
except ImportError as e:
    print(f"✗ 失败: {e}")

print("\n测试导入 backend.api.models...")
try:
    import backend.api.models
    print("✓ 成功导入 backend.api.models")
except ImportError as e:
    print(f"✗ 失败: {e}")

print("\n测试导入 matches.py 中的模型...")
try:
    from backend.models.matches import FootballMatch
    print("✓ 成功导入 FootballMatch")
except ImportError as e:
    print(f"✗ 失败: {e}")

print("\n检查所有 Base 导入是否一致...")
try:
    from backend.models.base import Base as Base1
    from backend.database import Base as Base2
    print(f"Base1 id: {id(Base1)}")
    print(f"Base2 id: {id(Base2)}")
    if Base1 is Base2:
        print("✓ Base 实例相同")
    else:
        print("✗ Base 实例不同 - 这可能会导致表冲突")
except Exception as e:
    print(f"✗ 检查失败: {e}")