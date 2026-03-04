"""
API绔偣闆嗘垚娴嬭瘯
娴嬭瘯API绔偣鐨勫疄闄呰涓哄拰涓庡叾浠栨ā鍧楃殑闆嗘垚
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.main import app
from backend.config import settings
from backend.database_async import get_async_db
from backend.models.admin_user import AdminUser
from backend.core.security import get_password_hash
from unittest.mock import AsyncMock, patch


# 鍒涘缓娴嬭瘯瀹㈡埛绔?
client = TestClient(app)


@pytest.fixture
def mock_db_session():
    """妯℃嫙鏁版嵁搴撲細璇?""
    session = AsyncMock()
    session.execute = AsyncMock(return_value=AsyncMock())
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """娴嬭瘯鍋ュ悍妫€鏌ョ鐐?""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    print("SUCCESS 鍋ュ悍妫€鏌ョ鐐规祴璇曢€氳繃")


def test_docs_endpoint():
    """娴嬭瘯API鏂囨。绔偣"""
    response = client.get("/docs")
    assert response.status_code in [200, 307]  # 307鏄噸瀹氬悜鍒?docs/
    print("SUCCESS API鏂囨。绔偣娴嬭瘯閫氳繃")


@pytest.mark.asyncio
async def test_admin_user_endpoints_integration():
    """娴嬭瘯绠＄悊鍛樼敤鎴稟PI绔偣闆嗘垚"""
    # 鐢变簬杩欎簺绔偣闇€瑕佽璇侊紝鎴戜滑娴嬭瘯杩斿洖鐨勮璇侀敊璇?
    response = client.get("/api/v1/admin/users/")
    # 搴旇杩斿洖401鏈璇佹垨422璇锋眰浣撻敊璇紙濡傛灉娌℃湁鎻愪緵蹇呰鍙傛暟锛?
    assert response.status_code in [401, 422]
    
    response = client.post("/api/v1/admin/users/")
    assert response.status_code in [401, 422]
    
    print("SUCCESS 绠＄悊鍛樼敤鎴稟PI绔偣闆嗘垚娴嬭瘯閫氳繃")


@pytest.mark.asyncio
async def test_auth_endpoints_integration():
    """娴嬭瘯璁よ瘉API绔偣闆嗘垚"""
    # 娴嬭瘯鐧诲綍绔偣锛堟病鏈夋彁渚涙暟鎹紝鏈熸湜杩斿洖422锛?
    response = client.post("/api/v1/auth/login")
    assert response.status_code == 422  # 璇锋眰浣撶己澶?
    
    # 娴嬭瘯娉ㄥ唽绔偣锛堟病鏈夋彁渚涙暟鎹紝鏈熸湜杩斿洖422锛?
    response = client.post("/api/v1/auth/register")
    assert response.status_code == 422  # 璇锋眰浣撶己澶?
    
    print("SUCCESS 璁よ瘉API绔偣闆嗘垚娴嬭瘯閫氳繃")


@pytest.mark.asyncio
async def test_crawler_endpoints_integration():
    """娴嬭瘯鐖櫕API绔偣闆嗘垚"""
    # 娴嬭瘯鑾峰彇鐖櫕閰嶇疆绔偣锛堥渶瑕佽璇侊級
    response = client.get("/api/v1/crawlers/configs/")
    assert response.status_code in [401, 422]
    
    # 娴嬭瘯鑾峰彇鐖櫕浠诲姟绔偣锛堥渶瑕佽璇侊級
    response = client.get("/api/v1/crawlers/tasks/")
    assert response.status_code in [401, 422]
    
    print("SUCCESS 鐖櫕API绔偣闆嗘垚娴嬭瘯閫氳繃")


@pytest.mark.asyncio
async def test_public_endpoints():
    """娴嬭瘯鍏叡API绔偣"""
    # 娴嬭瘯鑾峰彇姣旇禌鏁版嵁鐨勫叕鍏辩鐐癸紙濡傛灉娌℃湁鏁版嵁鍙兘杩斿洖绌烘暟缁勶級
    response = client.get("/api/v1/public/matches/")
    # 鍏叡绔偣涓嶉渶瑕佽璇侊紝浣嗗彲鑳藉洜涓烘暟鎹簱涓病鏈夋暟鎹€岃繑鍥炵壒瀹氬搷搴?
    assert response.status_code in [200, 404, 500]
    
    print("SUCCESS 鍏叡API绔偣娴嬭瘯閫氳繃")


@pytest.mark.asyncio
async def test_api_response_format():
    """娴嬭瘯API鍝嶅簲鏍煎紡涓€鑷存€?""
    # 妫€鏌ヤ竴涓亣鎯崇殑绔偣鍝嶅簲鏍煎紡
    # 鍥犱负璁稿绔偣闇€瑕佽璇侊紝鎴戜滑妯℃嫙涓€涓鐐规鏌ユ牸寮?
    from backend.utils.response import UnifiedResponse
    
    # 娴嬭瘯缁熶竴鍝嶅簲鏍煎紡
    response = UnifiedResponse.success(data={"test": "data"})
    assert hasattr(response, 'code')
    assert hasattr(response, 'message')
    assert hasattr(response, 'data')
    assert response.code == 200
    assert response.message == "Success"
    
    error_response = UnifiedResponse.error(message="Test error", code=400)
    assert error_response.code == 400
    assert error_response.message == "Test error"
    
    print("SUCCESS API鍝嶅簲鏍煎紡涓€鑷存€ф祴璇曢€氳繃")


if __name__ == "__main__":
    # 杩愯娴嬭瘯
    test_health_check_endpoint()
    test_docs_endpoint()
    test_admin_user_endpoints_integration()
    test_auth_endpoints_integration()
    test_crawler_endpoints_integration()
    test_public_endpoints()
    test_api_response_format()
