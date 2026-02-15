"""
娴嬭瘯鍚庣妯″潡瀵煎叆
"""
import sys
import traceback

print("=" * 60)
print("鍚庣瀵煎叆娴嬭瘯")
print("=" * 60)

# 娴嬭瘯1: 瀵煎叆閰嶇疆
print("\n1锔忊儯 娴嬭瘯閰嶇疆瀵煎叆...")
try:
    from backend.config import settings
    print(f"   SUCCESS 閰嶇疆鍔犺浇鎴愬姛")
    print(f"   椤圭洰鍚? {settings.PROJECT_NAME}")
    print(f"   绔彛: {settings.PORT}")
    print(f"   涓绘満: {settings.HOST}")
except Exception as e:
    print(f"   [ERROR] 閰嶇疆瀵煎叆澶辫触: {e}")
    traceback.print_exc()
    sys.exit(1)

# 娴嬭瘯2: 瀵煎叆鏁版嵁搴?
print("\n2锔忊儯 娴嬭瘯鏁版嵁搴撳鍏?..")
try:
    from backend.database import engine
    print(f"   SUCCESS 鏁版嵁搴撴ā鍧楀姞杞芥垚鍔?)
except Exception as e:
    print(f"   [WARNING]  鏁版嵁搴撳鍏ヨ鍛? {e}")

# 娴嬭瘯3: 瀵煎叆API璺敱
print("\n3锔忊儯 娴嬭瘯API璺敱瀵煎叆...")
try:
    from backend.api import router
    print(f"   SUCCESS API璺敱鍔犺浇鎴愬姛")
except Exception as e:
    print(f"   [ERROR] API璺敱瀵煎叆澶辫触: {e}")
    traceback.print_exc()
    sys.exit(1)

# 娴嬭瘯4: 瀵煎叆涓诲簲鐢?
print("\n4锔忊儯 娴嬭瘯涓诲簲鐢ㄥ鍏?..")
try:
    from backend.main import app
    print(f"   SUCCESS 涓诲簲鐢ㄥ姞杞芥垚鍔?)
    print(f"   搴旂敤瀹炰緥: {app}")
except Exception as e:
    print(f"   [ERROR] 涓诲簲鐢ㄥ鍏ュけ璐? {e}")
    print("\n璇︾粏閿欒:")
    traceback.print_exc()
    sys.exit(1)

# 娴嬭瘯5: 妫€鏌vicorn
print("\n5锔忊儯 娴嬭瘯Uvicorn...")
try:
    import uvicorn
    print(f"   SUCCESS Uvicorn鐗堟湰: {uvicorn.__version__}")
except Exception as e:
    print(f"   [ERROR] Uvicorn鏈畨瑁? {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("SUCCESS 鎵€鏈夋祴璇曢€氳繃锛佸簲鐢ㄥ彲浠ュ惎鍔?)
print("=" * 60)
print("\n璇疯繍琛屼互涓嬪懡浠ゅ惎鍔ㄦ湇鍔″櫒:")
print("python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")

