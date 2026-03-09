# Backend 测试说明

## 快速开始

### 1. 安装依赖
```bash
cd backend
pip install -r requirements-dev.txt
pip install -r requirements.txt
```

### 2. 运行测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/unit/api/test_auth.py::TestPasswordUtils -v
pytest tests/unit/core/test_security.py -v

# 运行带覆盖率的测试
pytest tests/unit/ --cov=. --cov-report=html --cov-report=term-missing
```

### 3. 测试结构调整

当前测试文件需要以下项目文件支持：

#### 必需的项目文件结构：
```
backend/
├── main.py                    # FastAPI应用入口
├── api/
│   └── v1/
│       └── auth.py           # 认证API路由
├── schemas/
│   └── user.py              # 用户数据模型
├── services/
│   └── auth_service.py      # 认证业务逻辑
├── models/
│   └── user.py              # 用户数据库模型
├── core/
│   ├── security.py           # 安全工具函数
│   └── response.py           # 统一响应格式
└── tests/
    ├── conftest.py           # 测试配置和fixtures
    └── unit/
        └── api/
            └── test_auth.py  # 认证测试（已创建）
```

### 4. 待创建的关键文件

#### `backend/tests/conftest.py` - 测试配置
```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.user import User
from backend.database import Base, engine

@pytest.fixture(scope="session")
def test_app():
    return app

@pytest.fixture(scope="session")
def test_client(test_app):
    return TestClient(test_app)

@pytest.fixture
async def db_session():
    # 创建测试数据库表
    Base.metadata.create_all(bind=engine)
    yield
    # 清理测试数据
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123"
    }
```

#### `backend/api/v1/auth.py` - 基础API结构
```python
from fastapi import APIRouter, Depends, HTTPException
from backend.services.auth_service import AuthenticationService

router = APIRouter()

@router.post("/register")
async def register_user():
    pass

@router.post("/login")
async def login_user():
    pass
```

### 5. 当前测试状态

✅ **已完成：**
- 测试文件结构和用例设计
- 单元测试逻辑编写
- Pytest配置和覆盖率报告

⚠️ **需要修复：**
- 导入路径和实际项目结构匹配
- 创建必要的fixtures
- 实现被测试的API端点

### 6. 临时运行测试的方法

由于项目结构可能不完整，可以创建最小化的mock版本来测试：

```bash
# 创建临时的最小化实现来测试
mkdir -p backend/api/v1
mkdir -p backend/services
mkdir -p backend/schemas
mkdir -p backend/models
mkdir -p backend/core

# 然后创建上述必需的基础文件
```

### 7. 建议的开发顺序

1. **第一步：** 创建基础项目结构文件
2. **第二步：** 实现核心API端点
3. **第三步：** 修复测试导入路径
4. **第四步：** 运行完整测试套件
5. **第五步：** 配置CI/CD流水线