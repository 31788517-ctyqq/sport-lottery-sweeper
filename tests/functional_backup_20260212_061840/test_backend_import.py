"""
测试后端模块导入
"""
import sys
import traceback

print("=" * 60)
print("后端导入测试")
print("=" * 60)

# 测试1: 导入配置
print("\n1️⃣ 测试配置导入...")
try:
    from backend.config import settings
    print(f"   [OK] 配置加载成功")
    print(f"   项目名: {settings.PROJECT_NAME}")
    print(f"   端口: {settings.PORT}")
    print(f"   主机: {settings.HOST}")
except Exception as e:
    print(f"   [ERROR] 配置导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# 测试2: 导入数据库
print("\n2️⃣ 测试数据库导入...")
try:
    from backend.database import engine
    print(f"   [OK] 数据库模块加载成功")
except Exception as e:
    print(f"   [WARNING]  数据库导入警告: {e}")

# 测试3: 导入API路由
print("\n3️⃣ 测试API路由导入...")
try:
    from backend.api import router
    print(f"   [OK] API路由加载成功")
except Exception as e:
    print(f"   [ERROR] API路由导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# 测试4: 导入主应用
print("\n4️⃣ 测试主应用导入...")
try:
    from backend.main import app
    print(f"   [OK] 主应用加载成功")
    print(f"   应用实例: {app}")
except Exception as e:
    print(f"   [ERROR] 主应用导入失败: {e}")
    print("\n详细错误:")
    traceback.print_exc()
    sys.exit(1)

# 测试5: 检查uvicorn
print("\n5️⃣ 测试Uvicorn...")
try:
    import uvicorn
    print(f"   [OK] Uvicorn版本: {uvicorn.__version__}")
except Exception as e:
    print(f"   [ERROR] Uvicorn未安装: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("[OK] 所有测试通过！应用可以启动")
print("=" * 60)
print("\n请运行以下命令启动服务器:")
print("python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
