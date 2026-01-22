"""
快速启动后端 - 带详细错误捕获
"""
import sys
import os
import traceback

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("[Backend Quick Start]")
print("=" * 70)
print(f"工作目录: {os.getcwd()}")
print(f"Python: {sys.version}")
print("=" * 70)

try:
    print("\n[Step 1] Importing FastAPI and Uvicorn...")
    import fastapi
    import uvicorn
    print(f"   [OK] FastAPI: {fastapi.__version__}")
    print(f"   [OK] Uvicorn: {uvicorn.__version__}")
    
    print("\n[Step 2] Loading configuration...")
    from backend.config import settings
    print(f"   [OK] Project: {settings.PROJECT_NAME}")
    print(f"   [OK] Port: {settings.PORT}")
    
    print("\n[Step 3] Importing database...")
    try:
        from backend.database import engine
        print(f"   [OK] Database engine created")
    except Exception as e:
        print(f"   [WARN] Database warning: {e}")
        print(f"   [INFO] Continuing startup...")
    
    print("\n[Step 4] Loading API routes...")
    try:
        from backend.api import router
        print(f"   [OK] API routes loaded")
    except Exception as e:
        print(f"   [ERROR] API routes loading failed!")
        print(f"   Error: {e}")
        traceback.print_exc()
        print("\n[TIPS] Possible causes:")
        print("   1. Syntax errors in API modules")
        print("   2. Missing dependencies")
        print("   3. Circular import issues")
        sys.exit(1)
    
    print("\n[Step 5] Creating application instance...")
    try:
        from backend.main import app
        print(f"   [OK] Application created successfully")
    except Exception as e:
        print(f"   [ERROR] Application creation failed!")
        print(f"   Error: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("[SUCCESS] All checks passed! Starting server...")
    print("=" * 70)
    print(f"\n[URLs]")
    print(f"   - Home: http://localhost:{settings.PORT}/")
    print(f"   - API Docs: http://localhost:{settings.PORT}/docs")
    print(f"   - Health: http://localhost:{settings.PORT}/health")
    print("\n[CTRL+C] to stop server")
    print("=" * 70)
    
    # 启动服务器
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
    
except KeyboardInterrupt:
    print("\n\n" + "=" * 70)
    print("[STOPPED] Server stopped")
    print("=" * 70)
    
except Exception as e:
    print("\n\n" + "=" * 70)
    print("[FAILED] Startup failed!")
    print("=" * 70)
    print(f"\nError Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\nFull Traceback:")
    traceback.print_exc()
    print("\n" + "=" * 70)
    print("[TIPS] Troubleshooting:")
    print("   1. Check the error message above")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Check if database file exists")
    print("   4. Check for syntax errors in backend modules")
    print("=" * 70)
    input("\nPress Enter to exit...")
    sys.exit(1)
