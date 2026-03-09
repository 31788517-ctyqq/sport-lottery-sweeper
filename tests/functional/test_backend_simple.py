#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
绠€鍖栫増鍚庣鍚姩娴嬭瘯
楠岃瘉淇鍚庣殑鏍稿績鍔熻兘
"""
import sys
import os
import traceback

# 璁剧疆鐜 - 娣诲姞椤圭洰鏍圭洰褰曞埌Python璺緞
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ['PYTHONPATH'] = project_root

def test_imports():
    """娴嬭瘯鍏抽敭妯″潡瀵煎叆"""
    print("[INSPECT] 娴嬭瘯妯″潡瀵煎叆...")
    
    tests = [
        ("鏁版嵁搴撳紩鎿?, "from backend.core.database import engine, Base"),
        ("鍩虹妯″瀷", "from backend.models.base import Base"),
        ("鐖櫕鏃ュ織妯″瀷", "from backend.models.crawler_logs import CrawlerTaskLog"),
        ("鐖櫕浠诲姟妯″瀷", "from backend.models.crawler_tasks import CrawlerTask"),
        ("鏁版嵁婧愭ā鍨?, "from backend.models.data_sources import CrawlerConfig"),
        ("棰勬祴妯″瀷", "from backend.models.predictions import Prediction"),
        ("璧旂巼妯″瀷", "from backend.models.odds import Odds"),
        ("姣旇禌妯″瀷", "from backend.models.match import Match"),
        ("鐢ㄦ埛妯″瀷", "from backend.models.user import User"),
        ("绠＄悊鍛樻ā鍨?, "from backend.models.admin_user import AdminUser"),
        ("鎯呮姤妯″瀷", "from backend.models.intelligence import Intelligence"),
        ("鍦洪妯″瀷", "from backend.models.venues import Venue"),
        ("缁樺埗鐗瑰緛妯″瀷", "from backend.models.draw_feature import DrawFeature"),
        ("缁樺埗棰勬祴妯″瀷", "from backend.models.draw_prediction import DrawPrediction"),
    ]
    
    failed = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  SUCCESS {name}")
        except Exception as e:
            print(f"  [ERROR] {name}: {str(e)[:100]}")
            failed.append((name, str(e)))
    
    return failed

def test_database_connection():
    """娴嬭瘯鏁版嵁搴撹繛鎺?""
    print("\n[INSPECT] 娴嬭瘯鏁版嵁搴撹繛鎺?..")
    try:
        from backend.core.database import engine, Base
        from sqlalchemy import text
        
        # 灏濊瘯杩炴帴
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("  SUCCESS 鏁版嵁搴撹繛鎺ユ垚鍔?)
        
        # 灏濊瘯鍒涘缓琛紙濡傛灉瀛樺湪鍒欎笉鍒涘缓锛?
        Base.metadata.create_all(bind=engine)
        print("  SUCCESS 琛ㄧ粨鏋勫悓姝ユ垚鍔?)
        
        return True
    except Exception as e:
        print(f"  [ERROR] 鏁版嵁搴撹繛鎺ュけ璐? {e}")
        traceback.print_exc()
        return False

def test_api_routes():
    """娴嬭瘯API璺敱娉ㄥ唽"""
    print("\n[INSPECT] 娴嬭瘯API璺敱...")
    try:
        from backend.main import app
        routes = [route.path for route in app.routes]
        
        # 妫€鏌ュ叧閿矾鐢辨槸鍚﹀瓨鍦?
        key_routes = [
            "/admin/crawler/sources",
            "/admin/crawler/tasks",
            "/admin/crawler/configs",
            "/crawler-alert/rules",
            "/monitoring/dashboard/overview",
            "/sp-management/data-sources",
            "/draw-prediction/patterns",
            "/auth/login",
        ]
        
        missing = []
        for route in key_routes:
            if not any(r.startswith(route) for r in routes):
                missing.append(route)
            else:
                print(f"  SUCCESS {route}")
        
        if missing:
            print(f"  [ERROR] 缂哄け璺敱: {missing}")
            return False
        else:
            print(f"  SUCCESS 鎵€鏈夊叧閿矾鐢卞凡娉ㄥ唽 (鍏?{len(routes)} 涓矾鐢?")
            return True
    except Exception as e:
        print(f"  [ERROR] API璺敱娴嬭瘯澶辫触: {e}")
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("[TARGET] 鍚庣鍚姩楠岃瘉娴嬭瘯")
    print("="*60)
    
    # 娴嬭瘯1: 妯″潡瀵煎叆
    failed_imports = test_imports()
    if failed_imports:
        print(f"\n[ERROR] 鏈?{len(failed_imports)} 涓ā鍧楀鍏ュけ璐?)
        return False
    
    # 娴嬭瘯2: 鏁版嵁搴撹繛鎺?
    if not test_database_connection():
        print("\n[ERROR] 鏁版嵁搴撹繛鎺ュけ璐?)
        return False
    
    # 娴嬭瘯3: API璺敱
    if not test_api_routes():
        print("\n[ERROR] API璺敱娉ㄥ唽涓嶅畬鏁?)
        return False
    
    print("\n" + "="*60)
    print("[SUCCESS] 鎵€鏈夋祴璇曢€氳繃锛佸悗绔簲璇ュ彲浠ユ甯稿惎鍔?)
    print("="*60)
    print("\n[LOG] 淇鎬荤粨:")
    print("  1. SUCCESS 淇浜嗘墍鏈?Enum 鍒楃殑 SQLAlchemy 鍏煎鎬?)
    print("  2. SUCCESS 瑙ｅ喅浜?crawler_task_logs 琛ㄩ噸澶嶅畾涔夐棶棰?)
    print("  3. SUCCESS 淇浜?draw_prediction 瀵煎叆璺緞閿欒")
    print("  4. SUCCESS 绉婚櫎浜嗘墍鏈?PostgreSQL 鐗规湁绫诲瀷瀵煎叆")
    print("  5. SUCCESS 琛ュ厖浜嗙己澶辩殑 imports")
    print("\n[ROCKET] 鍙互灏濊瘯杩愯: start_backend.bat")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

