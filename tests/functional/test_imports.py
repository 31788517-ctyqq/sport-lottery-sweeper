#!/usr/bin/env python3
"""
测试后端关键导入
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 测试后端导入 ===")

# 测试关键导入
try:
    from backend.schemas import Match
    print("✓ 成功导入 backend.schemas.Match")
except ImportError as e:
    print(f"✗ 导入 backend.schemas.Match 失败: {e}")

try:
    from backend.models import Match as ModelMatch
    print("✓ 成功导入 backend.models.Match")
except ImportError as e:
    print(f"✗ 导入 backend.models.Match 失败: {e}")

try:
    from backend.models import FootballMatch
    print("✓ 成功导入 backend.models.FootballMatch")
except ImportError as e:
    print(f"✗ 导入 backend.models.FootballMatch 失败: {e}")

try:
    from backend.utils.response import UnifiedResponse
    print("✓ 成功导入 backend.utils.response.UnifiedResponse")
except ImportError as e:
    print(f"✗ 导入 UnifiedResponse 失败: {e}")

try:
    from backend.schemas.response import UnifiedResponse as SchemaUnifiedResponse
    print("✓ 成功导入 backend.schemas.response.UnifiedResponse")
except ImportError as e:
    print(f"✗ 导入 backend.schemas.response.UnifiedResponse 失败: {e}")

try:
    from backend.api.v1.draw_prediction import router
    print("✓ 成功导入 draw_prediction 路由")
except ImportError as e:
    print(f"✗ 导入 draw_prediction 路由失败: {e}")
    # 尝试诊断
    try:
        from backend.models.draw_feature import DrawFeature
        print("  ...但可以导入 DrawFeature")
    except ImportError as e2:
        print(f"  ...DrawFeature 导入也失败: {e2}")

print("=== 导入测试完成 ===")