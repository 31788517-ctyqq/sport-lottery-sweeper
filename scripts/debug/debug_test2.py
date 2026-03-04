#!/usr/bin/env python3
"""
调试测试失败原因
"""
import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import MagicMock, patch
from backend.database import get_db
from backend.services.sp_management_service import SPManagementService

# 创建模拟数据库会话
mock_db = MagicMock()

# 覆盖get_db依赖
def override_get_db():
    yield mock_db

app.dependency_overrides[get_db] = override_get_db

# 创建模拟服务
mock_service = MagicMock(spec=SPManagementService)

# 模拟分页响应
sample_source = {
    "id": 1,
    "source_id": "DS001",
    "name": "测试数据源1",
    "type": "api",
    "status": 1,
    "url": "https://api.example.com/data",
    "config": {"category": "match_data", "timeout": 30},
    "last_update": "2024-01-01T12:00:00",
    "error_rate": 0.0,
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00",
    "created_by": 1
}

mock_paginated = MagicMock()
mock_paginated.items = [MagicMock(**sample_source)]
mock_paginated.total = 1
mock_paginated.page = 1
mock_paginated.size = 10
mock_paginated.pages = 1

mock_service.get_data_sources.return_value = mock_paginated

# 模拟SPManagementService的构造函数
with patch('backend.api.v1.admin.data_source.SPManagementService', return_value=mock_service):
    # 创建测试客户端
    client = TestClient(app)
    
    # 测试特定路由
    print('测试/api/v1/admin/sources:')
    try:
        response = client.get('/api/v1/admin/sources')
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'成功: {data["success"]}')
            print(f'消息: {data["message"]}')
            if "data" in data and "items" in data["data"]:
                print(f'数据项数: {len(data["data"]["items"])}')
            else:
                print(f'数据结构: {data.keys()}')
                print(f'数据内容: {data}')
        else:
            print(f'错误响应: {response.text[:1000]}')
    except Exception as e:
        print(f'请求异常: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()