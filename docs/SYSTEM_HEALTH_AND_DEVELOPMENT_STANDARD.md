# 体育彩票扫盘系统健康度与开发规范标准
**版本**: 2.0  
**最后更新**: 2026-02-07  
**文档ID**: SHDS-STD-2026-v2.0

## 目录索引

### 核心开发规范
- [一、系统概述](#一系统概述)
- [二、架构规范](#二架构规范)
- [三、代码规范](#三代码规范)
- [四、API设计规范](#四api设计规范)
- [五、数据库规范](#五数据库规范)
- [六、安全规范](#六安全规范)
- [七、性能规范](#七性能规范)
- [八、日志规范](#八日志规范)
- [九、错误处理规范](#九错误处理规范)
- [十、测试规范](#十测试规范)
- [十一、部署规范](#十一部署规范)
- [十二、文件存储规范](#十二文件存储规范)

### 管理体系
- [十三、测试管理体系](#十三测试管理体系)
- [十四、问题修复追踪系统](#十四问题修复追踪系统)
- [十五、前端路由规范](#十五前端路由规范)
- [十六、多IDE开发环境规范](#十六多ide开发环境规范)
- [十七、项目开发经验教训与最佳实践](#十七项目开发经验教训与最佳实践)

### AI开发规范
- [十八、AI托管开发规范](#十八ai托管开发规范)

### 前端设计规范
- [十九、前端UI设计规范 - 莫兰迪色风格指南](#十九前端ui设计规范---莫兰迪色风格指南)
- [二十、前端开发最佳实践与约束规范](#二十前端开发最佳实践与约束规范)

### 测试与流程规范
- [二十一、端到端测试规范与自动化](#二十一端到端测试规范与自动化)
- [二十二、功能规划与开发流程](#二十二功能规划与开发流程)

### 附录
- [二十三、快速参考指南](#二十三快速参考指南)
- [二十四、文档修订记录](#二十四文档修订记录)

---

## 一、系统概述

### 1.1 项目背景

竞彩足球扫盘系统是一个专业的足球数据采集、分析和预测平台，为竞彩足球提供全面的数据支持与智能决策辅助。

### 1.2 技术栈

- **前端**: Vue 3 + Vite + TypeScript + Element Plus
- **后端**: Python 3.11 + FastAPI + Uvicorn
- **数据库**: SQLite (开发环境) / PostgreSQL (生产环境)
- **缓存**: Redis 7+
- **异步任务**: Celery + Redis/RabbitMQ
- **部署**: Docker + Docker Compose + Nginx

### 1.3 系统架构

```
+-------------------+       +-------------------+       +-------------------+
|  Frontend (Vue)   |       |  Backend (FastAPI)|       |  Database (Postgres)|
+-------------------+       +-------------------+       +-------------------+
|  Vite             |       |  Uvicorn          |       |  Redis            |
|  TypeScript       |       |  Celery           |       |  PostgreSQL       |
|  Element Plus     |       |  SQLAlchemy       |       |  Redis            |
+-------------------+       +-------------------+       +-------------------+

```

## 二、架构规范

### 2.1 项目结构

```
backend/
├── main.py
├── app/
│   ├── __init__.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── user.py
│   │   └── data.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── data.py
│   │   └── admin.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── data_service.py
│   │   └── admin_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   └── logger.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── data_fetch.py
│   │   └── data_process.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── logging.py
│   └── tests/
│       ├── __init__.py
│       ├── unit/
│       │   ├── __init__.py
│       │   ├── test_user.py
│       │   ├── test_data.py
│       │   └── test_admin.py
│       ├── integration/
│       │   ├── __init__.py
│       │   ├── test_user_api.py
│       │   ├── test_data_api.py
│       │   └── test_admin_api.py
│       └── e2e/
│           ├── __init__.py
│           ├── test_user_login.py
│           ├── test_data_fetch.py
│           └── test_admin_dashboard.py
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── assets/
│   │   ├── logo.png
│   │   └── styles.css
│   ├── components/
│   │   ├── __init__.py
│   │   ├── UserCard.vue
│   │   ├── DataChart.vue
│   │   └── AdminPanel.vue
│   ├── views/
│   │   ├── __init__.py
│   │   ├── Home.vue
│   │   ├── User.vue
│   │   ├── Data.vue
│   │   └── Admin.vue
│   ├── router/
│   │   ├── __init__.py
│   │   └── index.js
│   ├── store/
│   │   ├── __init__.py
│   │   ├── user.js
│   │   ├── data.js
│   │   └── admin.js
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.js
│   │   ├── api.js
│   │   └── logger.js
│   ├── App.vue
│   └── main.js
.gitignore
.env
.env.example
.env.production
README.md
PROJECT_STANDARDS.md
ROUTING_RULES.md
STARTUP_CONFIG.md
```

### 2.2 依赖管理

```
# backend/requirements.txt
fastapi
uvicorn
sqlalchemy
celery
redis
pydantic
python-dotenv
bandit

# frontend/package.json
{
  "name": "sport-lottery-sweeper",
  "version": "1.0.0",
  "description": "体育彩票扫盘系统",
  "main": "src/main.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "serve": "vite preview",
    "lint": "eslint . --ext .js,.vue",
    "format": "prettier --write .",
    "test": "vitest",
    "test:unit": "vitest run",
    "test:integration": "vitest run --config vitest.integration.config.js",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "vue": "^3.2.31",
    "element-plus": "^2.2.22",
    "axios": "^1.1.3"
  },
  "devDependencies": {
    "vite": "^4.0.0",
    "vitest": "^0.24.0",
    "eslint": "^8.29.0",
    "eslint-plugin-vue": "^9.5.0",
    "prettier": "^2.7.1",
    "playwright": "^1.27.1"
  }
}

```

## 三、代码规范

### 3.1 代码风格

- **Python**:
  - 使用 `snake_case` 命名变量、函数和方法
  - 使用 `PascalCase` 命名类
  - 代码缩进使用4个空格
  - 行长度限制为88个字符
  - 使用 `black` 和 `isort` 进行代码格式化

- **JavaScript/TypeScript**:
  - 使用 `camelCase` 命名变量、函数和方法
  - 使用 `PascalCase` 命名类和组件
  - 代码缩进使用2个空格
  - 行长度限制为88个字符
  - 使用 `ESLint` 和 `Prettier` 进行代码格式化

- **HTML/CSS**:
  - 使用 `kebab-case` 命名类和ID
  - 使用 `snake_case` 命名属性
  - 使用 `Prettier` 进行代码格式化

### 3.2 代码注释

- **Python**:
  - 使用 `#` 进行单行注释
  - 使用 `"""` 进行多行注释和文档字符串

- **JavaScript/TypeScript**:
  - 使用 `//` 进行单行注释
  - 使用 `/** */` 进行多行注释和文档字符串

- **HTML/CSS**:
  - 使用 `/* */` 进行多行注释

### 3.3 代码组织

- **Python**:
  - 每个模块一个文件
  - 使用 `__init__.py` 文件标识包
  - 使用 `if __name__ == "__main__":` 作为脚本入口

- **JavaScript/TypeScript**:
  - 每个组件一个文件
  - 使用 `index.js` 文件标识模块入口
  - 使用 `main.js` 文件作为应用入口

- **HTML/CSS**:
  - 每个页面一个文件
  - 使用 `main.css` 文件作为全局样式入口

## 四、API设计规范

### 4.1 API版本控制

```
/api/v1/

```

### 4.2 API路由设计

```
/api/v1/
├── admin/
│   ├── users/
│   ├── data/
│   └── admin/
├── user/
│   ├── profile/
│   └── settings/
├── data/
│   ├── fetch/
│   └── process/
└── auth/
    ├── login/
    └── logout/

```

### 4.3 API请求/响应格式

```
# 请求示例
GET /api/v1/admin/users

# 响应示例
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
]

```

## 五、数据库规范

### 5.1 数据库设计

```
# backend/models/user.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

```

### 5.2 数据库迁移

```
# backend/alembic/versions/20260127_120000_initial_migration.py
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260127_120000'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('username', sa.String(), unique=True, index=True),
        sa.Column('email', sa.String(), unique=True, index=True),
        sa.Column('hashed_password', sa.String()),
        sa.Column('role', sa.String()),
    )

def downgrade():
    op.drop_table('users')

```

### 5.3 数据库文件位置规范

为确保数据库文件管理的一致性和可维护性，项目采用以下规范：

1. **主数据库文件位置**：
   - 数据库文件应位于项目根目录，文件名为 `sport_lottery.db`
   - 这是项目的唯一权威数据库文件，所有数据操作都应基于此文件

2. **硬链接使用规范**：
   - 为保持向后兼容性，可在 `backend/` 和 `data/` 目录下创建硬链接指向根目录的数据库文件
   - 硬链接确保多个路径指向同一物理文件，避免数据不一致
   - 创建硬链接命令（Windows）：`mklink /H "backend\sport_lottery.db" "sport_lottery.db"`

3. **代码引用规范**：
   - 所有数据库访问应通过 `backend.database.DATABASE_PATH` 配置
   - 禁止在代码中硬编码数据库路径（如 `"backend/sport_lottery.db"`）
   - 现有脚本应逐步迁移到使用统一配置

4. **健康检查**：
   - 定期运行 `check_database_paths.py` 验证所有数据库访问路径是否一致
   - 检查硬链接状态，确保没有创建冗余的数据库副本

5. **部署注意事项**：
   - 生产环境中，数据库文件位置应根据部署环境调整
   - 通过环境变量 `DATABASE_URL` 覆盖默认数据库路径
   - 确保数据库文件有适当的备份策略

```

## 六、安全规范

### 6.1 认证与授权

```
# backend/utils/auth.py
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .database import get_db
from .models.user import User

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

```

### 6.2 数据加密

```
# backend/utils/encryption.py
from cryptography.fernet import Fernet

SECRET_KEY = Fernet.generate_key()
cipher_suite = Fernet(SECRET_KEY)

def encrypt(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt(data: str) -> str:
    return cipher_suite.decrypt(data.encode()).decode()

```

## 七、性能规范

### 7.1 缓存策略

```
# backend/utils/cache.py
from redis import Redis
from fastapi import Depends

redis_client = Redis(host="localhost", port=6379, db=0)

def get_cache():
    return redis_client

```

### 7.2 数据库优化

```
# backend/utils/database.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .models import Base

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```

## 八、日志规范

```
# backend/utils/logger.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

```

## 九、错误处理规范

```
# backend/utils/error_handling.py
from fastapi import HTTPException
from fastapi.responses import JSONResponse

def handle_exception(exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

```

## 十、测试规范

```
# backend/tests/unit/test_user.py
import pytest
from sqlalchemy.orm import Session
from ..utils.database import get_db
from ..models.user import User

@pytest.fixture
def db_session():
    db = get_db()
    yield db
    db.close()

def test_create_user(db_session: Session):
    user = User(username="testuser", email="test@example.com", hashed_password="hashed_password", role="user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.username == "testuser"

```

## 十一、部署规范

```
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    command: pnpm run dev
    volumes:
      - ./frontend:/app
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: sport_lottery
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - db_data:/var/lib/postgresql/data

  redis:
    image: redis:7

volumes:
  db_data:

```

## 十二、文件存储规范

```
uploads/
├── avatars/
├── crawler_configs/
├── exports/
└── temp/

```

## 十三、测试管理体系

```
# backend/tests/unit/test_user.py
import pytest
from sqlalchemy.orm import Session
from ..utils.database import get_db
from ..models.user import User

@pytest.fixture
def db_session():
    db = get_db()
    yield db
    db.close()

def test_create_user(db_session: Session):
    user = User(username="testuser", email="test@example.com", hashed_password="hashed_password", role="user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.username == "testuser"

```

## 十四、问题修复追踪系统

```
# docs/issue_fix_records/2026/01_January_issues.md
### [1]: 数据库连接超时
- **分类**: bug
- **发现时间**: 2026-01-27 12:00
- **发现人员**: 张三
- **问题描述**: 数据库连接在高并发情况下频繁超时
- **根本原因**: 数据库连接池配置不当
- **解决方案**: 增加连接池大小，优化数据库查询
- **修复时间**: 2026-01-27 14:00
- **修复人员**: 李四
- **验证方法**: 压力测试
- **验证结果**: 通过
- **相关文件**: backend/utils/database.py
- **关联PR/Commit**: https://github.com/your-repo/your-project/pull/1
- **备注**: 无

```

## 十五、前端路由规范

```
# frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import User from '../views/User.vue'
import Data from '../views/Data.vue'
import Admin from '../views/Admin.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/user',
    name: 'User',
    component: User
  },
  {
    path: '/data',
    name: 'Data',
    component: Data
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router

```

## 十六、多IDE开发环境规范

### 16.1 开发环境一致性要求

#### 16.1.1 统一开发环境配置

为确保在不同IDE和账号下开发的一致性，所有开发者必须遵守以下配置规范：

- **编程语言版本**：
  - Python: 3.11.x (推荐 3.11.7)
  - Node.js: 18.x 或 20.x (推荐 20.5.1)
  - npm: >= 9.0
  - pnpm: >= 8.0

- **代码格式化工具**：
  - Python: black, isort, flake8 (配置文件: [.flake8](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/.flake8), [setup.cfg](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/setup.cfg))
  - JavaScript/TypeScript: ESLint, Prettier (配置文件: [.eslintrc.js](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/frontend/.eslintrc.js), [.prettierrc.js](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/frontend/.prettierrc.js))

- **代码风格**：
  - Python: 使用 snake_case 命名，遵循 PEP 8 规范
  - JavaScript/TypeScript: 使用 camelCase 命名
  - HTML/CSS: 使用 kebab-case 命名
  - 文件命名: 组件文件使用 PascalCase，其他文件使用 kebab-case

#### 16.1.2 环境验证脚本

项目提供环境验证脚本，所有开发者在开始工作前必须运行：

```bash
# 验证开发环境
python scripts/validate_dev_environment.py

# 验证依赖项
python scripts/check_dependencies.py

# 验证配置文件
python scripts/validate_config.py
```

### 16.2 IDE配置规范

#### 16.2.1 通用IDE设置

无论使用哪种IDE，都必须配置以下设置：

- **字符编码**: UTF-8
- **行结束符**: LF (Unix/Linux-style)，避免使用 CRLF
- **缩进**: 使用空格，Python 4个空格，JavaScript/TypeScript 2个空格
- **制表符宽度**: 与缩进宽度相同
- **自动去除行尾空白**: 启用
- **显示不可打印字符**: 可选，但推荐启用

#### 16.2.2 特定IDE插件/扩展要求

**VSCode**:
- Python (Microsoft)
- Vetur 或 Volar (Vue开发)
- ESLint
- Prettier
- GitLens
- indent-rainbow

**JetBrains系列**:
- 安装 Python 和 JavaScript 插件
- 配置代码格式化规则与项目保持一致
- 安装 Vue.js 插件支持前端开发

**其他IDE**:
- 确保IDE支持项目使用的代码格式化工具
- 配置IDE以识别项目根目录的配置文件

### 16.3 Git工作流规范

#### 16.3.1 分支管理策略

- **主分支**: `main` - 用于生产环境的稳定代码
- **开发分支**: `develop` - 用于集成开发中的功能
- **功能分支**: `feature/{feature-name}` - 开发新功能
- **修复分支**: `hotfix/{issue-id}-{brief-description}` - 修复紧急问题
- **发布分支**: `release/{version}` - 准备发布版本

#### 16.3.2 提交信息规范

所有IDE和账号都必须遵循以下提交信息格式：

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

其中 `<type>` 必须是以下之一：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

示例：
```
feat(api): 添加用户认证接口

- 实现JWT认证机制
- 添加登录和登出功能
- 更新API文档

Closes #123
```

#### 16.3.3 多账号协作规范

- **账号标识**: 每个开发者在提交时必须使用自己专属的账号信息
- **协作记录**: 在代码中添加注释标明修改者和时间戳，如 `// AI_WORKING: {username} @{timestamp}`
- **冲突预防**: 定期同步远程仓库，避免大规模冲突
- **代码审查**: 所有代码变更必须经过至少一名其他开发者的审查

### 16.4 代码审查规范

#### 16.4.1 审查流程

1. **自动检查**: 提交前运行自动化检查脚本
2. **自审**: 提交者自我审查代码质量和功能完整性
3. **同伴审查**: 至少一名其他开发者审查代码
4. **合并前验证**: 确保所有测试通过，代码符合规范

#### 16.4.2 审查重点

- 代码逻辑正确性
- 符合项目架构设计
- 遵循编码规范
- 适当添加注释和文档
- 安全性考虑
- 性能影响评估

### 16.5 多AI协同开发规范

#### 16.5.1 AI工作标识

当使用AI辅助开发时，必须在代码中明确标识AI身份和操作时间：

- **工作标记**: `// AI_WORKING: {ai-name} @{timestamp}`
- **完成标记**: `// AI_DONE: {ai-name} @{timestamp}`
- **锁定机制**: 修改文件前检查并创建锁文件，避免冲突

#### 16.5.2 协同操作流程

1. **锁检查**: 使用 `scripts/locks/check_lock.py` 检查文件锁状态
2. **创建锁**: 确认无人操作后创建锁文件
3. **执行修改**: 进行代码修改
4. **释放锁**: 完成后删除锁文件

#### 16.5.3 操作间隔

- 连续操作同一文件时，两次操作间至少间隔5秒
- 多AI协作时，每个AI完成一次操作后应等待其他AI完成操作

### 16.6 测试与验证规范

#### 16.6.1 本地测试要求

在提交代码前，所有开发者必须运行以下测试：

```bash
# 后端测试
cd backend && python -m pytest tests/unit/

# 前端测试
cd frontend && npm run test

# 集成测试
python scripts/run_integration_tests.py
```

#### 16.6.2 环境隔离

- **开发环境**: 本地开发和功能测试
- **测试环境**: 集成测试和功能验证
- **预发布环境**: 发布前最终验证

### 16.7 问题追踪与记录

#### 16.7.1 问题分类与记录

- **问题分类**: 按照 [十四、问题修复追踪系统](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/SYSTEM_HEALTH_AND_DEVELOPMENT_STANDARD.md#L1268-L1327) 中的分类标准记录问题
- **修复记录**: 遵循问题修复记录格式，确保信息完整
- **搜索历史**: 修复前必须搜索历史记录，避免重复工作

#### 16.7.2 知识共享

- **解决方案归档**: 将常见问题解决方案归档到 `docs/solutions/`
- **最佳实践分享**: 定期总结和分享开发最佳实践
- **培训材料**: 为新加入的开发者准备培训材料

## 十七、项目开发经验教训与最佳实践

### 17.1 开发过程中的弯路与问题

#### 17.1.1 启动脚本混乱
- **问题描述**: 项目中存在大量重复的启动脚本，如[start_backend.py](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/start_backend.py)、[backend_start.py](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/backend_start.py)、[start_backend_debug.py](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/start_backend_debug.py)、[start_backend_simple.py](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/start_backend_simple.py)等多个版本，导致开发者难以确定使用哪个脚本
- **根本原因**: 缺乏统一的启动脚本规范，开发者各自创建满足特定需求的脚本
- **解决方案**: 
  - 统一使用[backend/main.py](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/backend/main.py)作为主启动入口
  - 通过命令行参数支持不同启动模式（如调试模式、生产模式）
  - 将环境配置集中到.env文件中管理

#### 17.1.2 配置文件冗余
- **问题描述**: 存在多个环境配置文件（[.env](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/.env)、[.env.backup](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/.env.backup)、[.env.example](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/.env.example)、[.env.local](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/.env.local)、[.env.production](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/.env.production)等），且内容不一致
- **根本原因**: 缺乏配置管理规范，不同开发者维护各自的配置文件
- **解决方案**:
  - 维护单一权威的[.env.example](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/.env.example)文件作为模板
  - 通过[validate_env_config.py](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/scripts/validate_env_config.py)验证配置完整性
  - 在[README.md](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/README.md)中明确配置使用说明

#### 17.1.3 重复的测试文件
- **问题描述**: 项目中存在大量功能相似的测试文件，如[test_*.py](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/backend/tests/unit/api/test_admin.py)、[test_*_fix.py](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/backend/tests/unit/api/test_admin.py)、[test_*_final.py](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/backend/tests/unit/api/test_admin.py)等，表明测试迭代过程中未清理废弃文件
- **根本原因**: 缺乏测试文件管理规范，开发者倾向于创建新文件而不是修改现有测试
- **解决方案**:
  - 按照[测试管理体系](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/SYSTEM_HEALTH_AND_DEVELOPMENT_STANDARD.md#L1031-L1128)规范组织测试文件
  - 定期清理冗余测试文件
  - 使用版本控制系统跟踪测试文件演进

#### 17.1.4 文档分散且不一致
- **问题描述**: 项目文档分散在多个MD文件中，如[PROJECT_STANDARDS.md](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/PROJECT_STANDARDS.md)、[ROUTING_RULES.md](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/ROUTING_RULES.md)、[STARTUP_CONFIG.md](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/STARTUP_CONFIG.md)等，内容可能相互矛盾
- **根本原因**: 缺乏统一的文档管理策略，文档更新滞后于代码变化
- **解决方案**:
  - 将核心开发规范集中到本文件中
  - 建立文档更新与代码变更的关联机制
  - 定期审核文档一致性

### 17.2 开发规范缺失导致的问题

#### 17.2.1 缺乏代码审查流程
- **问题表现**: 代码质量参差不齐，错误处理不一致，安全漏洞未被及时发现
- **改进措施**:
  - 实施强制代码审查制度
  - 建立审查清单，涵盖安全性、性能、可维护性等方面
  - 使用自动化工具辅助审查

#### 17.2.2 版本控制不规范
- **问题表现**: 提交信息不规范，分支管理混乱，导致问题追溯困难
  - **改进措施**:
  - 采用Git Flow或GitHub Flow工作流
  - 规范提交信息格式，采用约定式提交规范
  - 定期清理废弃分支

#### 17.2.3 缺乏架构约束
- **问题表现**: 代码结构随项目发展变得混乱，模块职责不清，依赖关系复杂
- **改进措施**:
  - 制定架构约束规则，限制模块间的依赖关系
  - 定期进行架构评审
  - 使用架构分析工具监控架构健康度

### 17.3 最佳实践建议

#### 17.3.1 项目初始化阶段
- **制定开发规范**: 在项目开始时就确立编码规范、测试策略、文档标准等
- **搭建基础设施**: 配置CI/CD、代码质量检查、自动化测试等基础设施
- **建立文档体系**: 创建项目结构说明、开发指南、部署手册等基础文档

#### 17.3.2 开发过程管理
- **迭代规划**: 每个迭代开始前明确需求和验收标准
- **代码规范**: 严格执行编码规范，使用自动化工具保证一致性
- **持续集成**: 每次提交都进行自动化构建和测试
- **知识沉淀**: 记录开发过程中遇到的问题和解决方案

#### 17.3.3 质量保障措施
- **多层次测试**: 单元测试、集成测试、端到端测试相结合
- **自动化检查**: 代码质量、安全漏洞、性能指标等自动化检查
- **监控告警**: 生产环境运行状态监控和异常告警

#### 17.3.4 团队协作规范
- **沟通机制**: 建立有效的沟通渠道和会议机制
- **知识共享**: 定期技术分享，建立团队知识库
- **责任明确**: 明确每个人的职责和任务分工

### 17.4 避免重复错误的机制

#### 17.4.1 建立问题知识库
- 记录常见问题及其解决方案
- 按类别组织问题（如配置问题、部署问题、性能问题等）
- 定期更新和维护知识库

#### 17.4.2 实施防错机制
- 使用lint工具防止代码规范问题
- 使用类型检查工具防止类型错误
- 使用预提交钩子防止低级错误提交

#### 17.4.3 建立反馈循环
- 定期回顾开发过程中的问题
- 收集团队成员的改进建议
- 持续优化开发流程和规范

## 十八、AI托管开发规范 {#ai-guidelines}

### 18.1 AI开发角色与职责

#### 18.1.1 AI开发者标识
- **主开发者**: `coder1` - 负责核心功能开发和架构设计
- **辅助开发者**: `coder2` - 负责辅助功能和测试
- **系统管理员**: `sysop` - 负责部署和运维任务
- **质量保证**: `qa_bot` - 负责自动化测试和质量检查

#### 18.1.2 操作权限分配
- **代码修改权限**: `coder1`、`coder2` 可以修改代码文件
- **部署权限**: `sysop` 可以执行部署和运维操作
- **测试权限**: `qa_bot` 可以运行测试和报告结果
- **所有AI**: 必须遵循文件锁机制和协作协议

### 18.2 AI开发工作流

#### 18.2.1 任务接收与解析
1. **任务接收**: AI从中央任务系统接收开发任务
2. **需求解析**: 分析任务需求，识别涉及的模块和文件
3. **依赖检查**: 检查任务与其他正在进行的任务是否存在冲突
4. **环境准备**: 确保开发环境符合要求

#### 18.2.2 开发执行流程
1. **锁检查**: 使用 `scripts/locks/check_lock.py` 检查文件锁状态
2. **创建锁**: 确认无人操作后创建 `.lock` 文件
3. **代码修改**: 进行必要的代码修改
4. **本地测试**: 运行相关测试确保修改正确
5. **代码审查**: 自动进行代码规范检查
6. **提交修改**: 生成符合规范的提交信息
7. **释放锁**: 删除 `.lock` 文件

#### 18.2.3 任务完成与交接
1. **功能验证**: 确保修改的功能正常工作
2. **文档更新**: 更新相关文档和注释
3. **测试执行**: 运行相关测试套件
4. **结果报告**: 向任务系统报告完成状态
5. **交接确认**: 通知下一个环节的AI或开发者

### 18.3 AI协作协议

#### 18.3.1 文件访问协议
- **互斥访问**: 同一文件同时只能有一个AI访问
- **锁机制**: 访问前必须获取文件锁，访问后必须释放
- **超时处理**: 文件锁超过30 minutes未释放则视为超时，其他AI可接管
- **冲突解决**: 如遇冲突，按优先级顺序处理（紧急修复 > 功能开发 > 重构）

#### 18.3.2 通信协议
- **状态广播**: AI在开始重要操作前必须广播状态
- **进度更新**: 定期更新任务进度到中央系统
- **错误上报**: 遇到错误立即上报并请求协助
- **完成通知**: 任务完成后通知相关方

### 18.4 AI开发工具链

#### 18.4.1 自动化工具集
```
# 项目根目录/scripts/ai_tools/
├── task_receiver.py          # 任务接收器
├── requirement_analyzer.py   # 需求分析器
├── dependency_checker.py     # 依赖检查器
├── code_generator.py         # 代码生成器
├── test_runner.py            # 测试运行器
├── deployment_manager.py     # 部署管理器
├── quality_checker.py        # 质量检查器
└── progress_tracker.py       # 进度跟踪器
```

#### 18.4.2 状态管理系统
```
# 项目根目录/scripts/status/
├── ai_status.json            # AI状态信息
├── task_queue.json           # 任务队列
├── file_locks/               # 文件锁目录
│   ├── backend_main.py.lock
│   ├── frontend_app.js.lock
│   └── ...
└── operation_log.txt         # 操作日志
```

### 18.5 AI开发质量保证

#### 18.5.1 自动化质量检查
- **代码规范检查**: 使用 `black`, `flake8`, `eslint` 等工具
- **安全漏洞扫描**: 使用 `bandit`, `npm audit` 等工具
- **依赖安全检查**: 检查第三方库的安全问题
- **性能基准测试**: 确保修改不降低系统性能

#### 18.5.2 测试策略
- **单元测试**: 修改后自动运行相关单元测试
- **集成测试**: 验证模块间交互
- **回归测试**: 确保修改不影响现有功能
- **性能测试**: 验证系统性能指标

### 18.6 AI部署与运维

#### 18.6.1 部署流程
1. **环境检查**: 验证目标环境状态
2. **备份现有版本**: 创建当前版本的备份
3. **部署新版本**: 部署新代码和配置
4. **服务重启**: 重启相关服务
5. **健康检查**: 验证服务正常运行
6. **监控启动**: 启动监控和告警

#### 18.6.2 监控与告警
- **系统健康度**: CPU、内存、磁盘使用率
- **服务可用性**: API响应时间、错误率
- **业务指标**: 用户活动、数据处理量
- **日志分析**: 自动分析日志中的错误和异常

### 18.7 AI故障处理

#### 18.7.1 常见故障类型
- **代码故障**: 功能错误、性能问题
- **部署故障**: 服务不可用、配置错误
- **依赖故障**: 第三方服务不可用
- **资源故障**: 内存不足、磁盘满

#### 18.7.2 故障处理流程
1. **故障检测**: 通过监控系统自动检测故障
2. **故障分析**: 分析故障原因和影响范围
3. **应急处理**: 执行预定义的应急处理方案
4. **恢复验证**: 验证故障是否已解决
5. **根因分析**: 分析故障根本原因
6. **预防措施**: 制定预防措施防止再次发生

### 18.8 AI开发最佳实践

#### 18.8.1 开发实践
- **小步快跑**: 每次提交只做最小必要修改
- **测试驱动**: 先写测试再写功能代码
- **文档同步**: 代码和文档同步更新
- **渐进式改进**: 避免大规模重构

#### 18.8.2 协作实践
- **透明开发**: 所有操作都记录在案
- **及时沟通**: 遇到问题及时上报
- **知识共享**: 将学到的知识贡献给知识库
- **持续学习**: 不断优化AI的行为模式

## 二十三、快速参考指南 {#quick-reference}

### 23.1 常用命令速查

| 用途 | 命令 |
|------|------|
| 启动后端 | `python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000` |
| 启动前端 | `cd frontend && pnpm run dev` |
| 运行单元测试 | `python -m pytest tests/unit/` |
| 运行集成测试 | `python -m pytest tests/integration/` |
| 运行E2E测试 | `npx playwright test` |
| 检查代码格式 | `black . && isort .` |
| 运行安全扫描 | `bandit -r .` |

### 23.2 常见问题解决方案

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证数据库连接字符串格式
   - 确认用户名密码正确

2. **API认证失败**
   - 检查JWT token是否过期
   - 验证token格式是否正确
   - 确认用户权限设置

3. **前端组件样式冲突**
   - 使用CSS Modules或scoped CSS
   - 避免全局样式污染
   - 检查Element Plus版本兼容性

### 23.3 联系方式

- 项目经理: [联系人]
- 技术负责人: [联系人]
- 开发团队: [联系方式]

---

## 二十四、文档修订记录 {#revision-history}

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| 1.0 | 2026-01-27 | [作者] | 初始版本 |
| 1.1 | 2026-01-28 | [作者] | 添加测试管理体系 |
| 1.2 | 2026-01-29 | [作者] | 添加问题修复追踪系统 |
| 1.3 | 2026-01-30 | [作者] | 添加前端路由规范 |
| 1.4 | 2026-01-31 | [作者] | 添加多IDE开发环境规范 |
| 1.5 | 2026-02-07 | [作者] | 添加经验教训章节，优化文档结构 |
| 1.6 | 2026-02-07 | [作者] | 添加AI托管开发规范，优化文档结构 |
| 2.0 | 2026-02-07 | [作者] | 添加前端UI设计规范、前端开发最佳实践、端到端测试规范、功能规划流程，升级为版本2.0 |

## 二十一、前端UI设计规范 - 莫兰迪色风格指南

### 21.1 设计理念

莫兰迪色系是一种以灰色调为基础，融入淡雅色彩的配色方案，具有柔和、高级、舒适的视觉效果。在本项目中，我们采用莫兰迪色系来提升界面的整体质感和用户体验。

### 21.2 莫兰迪色系主色调

#### 21.2.1 主要颜色定义

| 颜色名称 | 色值 | 用途 |
|---------|------|------|
| 莫兰迪灰 | #8B8680 | 主要文字色、边框色 |
| 莫兰迪蓝 | #9FB1C4 | 次要文字色、提示色 |
| 莫兰迪粉 | #D4B3A1 | 按钮背景色、强调色 |
| 莫兰迪绿 | #AABEAD | 成功状态色 |
| 莫兰迪黄 | #D4CDB0 | 警告状态色 |
| 莫兰迪红 | #C6A1A6 | 错误状态色 |
| 莫兰迪紫 | #B7A2CD | 特殊功能色 |

#### 21.2.2 辅助颜色定义

| 颜色名称 | 色值 | 用途 |
|---------|------|------|
| 淡莫兰迪灰 | #D6D2CB | 背景色、分割线 |
| 深莫兰迪灰 | #6B6763 | 重要文字色 |
| 柔和白 | #F6F5F4 | 页面背景色 |

### 21.3 组件颜色应用规范

#### 21.3.1 按钮组件

```css
/* 主要按钮 */
.primary-btn {
  background-color: #D4B3A1; /* 莫兰迪粉 */
  border-color: #D4B3A1;
  color: white;
}

/* 次要按钮 */
.secondary-btn {
  background-color: transparent;
  border-color: #8B8680; /* 莫兰迪灰 */
  color: #8B8680;
}

/* 成功按钮 */
.success-btn {
  background-color: #AABEAD; /* 莫兰迪绿 */
  border-color: #AABEAD;
  color: white;
}

/* 警告按钮 */
.warning-btn {
  background-color: #D4CDB0; /* 莫兰迪黄 */
  border-color: #D4CDB0;
  color: #6B6763;
}

/* 危险按钮 */
.danger-btn {
  background-color: #C6A1A6; /* 莫兰迪红 */
  border-color: #C6A1A6;
  color: white;
}
```

#### 21.3.2 卡片组件

```css
/* 筛选器卡片 */
.filter-card {
  background-color: #F6F5F4; /* 柔和白 */
  border: 1px solid #D6D2CB; /* 淡莫兰迪灰 */
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(139, 134, 128, 0.1);
}

/* 内容卡片 */
.content-card {
  background-color: white;
  border: 1px solid #D6D2CB;
  border-radius: 12px;
  padding: 20px;
}
```

#### 21.3.3 表格组件

```css
/* 表格头部 */
.table-header {
  background-color: #F6F5F4;
  color: #6B6763;
  font-weight: 500;
}

/* 表格行 */
.table-row:nth-child(even) {
  background-color: #FDFDFC;
}

.table-row:hover {
  background-color: #F6F5F4;
}

/* 表格边框 */
.table-border {
  border-color: #D6D2CB;
}
```

### 21.4 标签和状态指示器

#### 21.4.1 状态标签

```css
/* 在线状态 */
.status-online {
  background-color: rgba(170, 190, 173, 0.2); /* 莫兰迪绿+透明度 */
  border: 1px solid #AABEAD;
  color: #6B6763;
}

/* 离线状态 */
.status-offline {
  background-color: rgba(214, 179, 161, 0.2); /* 莫兰迪粉+透明度 */
  border: 1px solid #D4B3A1;
  color: #6B6763;
}

/* 运行中状态 */
.status-running {
  background-color: rgba(159, 177, 196, 0.2); /* 莫兰迪蓝+透明度 */
  border: 1px solid #9FB1C4;
  color: #6B6763;
}
```

### 21.5 字体和排版规范

#### 21.5.1 字体颜色

- **主要文字**: #6B6763 (深莫兰迪灰) - 用于标题和重要内容
- **次要文字**: #8B8680 (莫兰迪灰) - 用于描述和辅助信息
- **占位符文字**: #BFB8B1 - 用于输入框占位符
- **链接文字**: #9FB1C4 (莫兰迪蓝) - 用于链接和可点击文本

#### 21.5.2 字体大小

- **主标题**: 24px, 字重 600
- **副标题**: 20px, 字重 500
- **正文**: 14px, 字重 400
- **辅助文字**: 12px, 字重 400

### 21.6 应用示例

#### 21.6.1 数据表格示例

``vue
<template>
  <el-table :data="tableData" class="morandi-table">
    <el-table-column prop="name" label="数据源名称" />
    <el-table-column prop="status" label="状态">
      <template #default="{ row }">
        <el-tag :class="getStatusClass(row.status)">
          {{ row.status }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="操作">
      <template #default="{ row }">
        <el-button type="primary" size="small">编辑</el-button>
        <el-button type="danger" size="small">删除</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<style lang="scss">
.morandi-table {
  // 使用莫兰迪色系的表格样式
  th {
    background-color: #F6F5F4;
    color: #6B6763;
    font-weight: 500;
  }

  td {
    border-bottom: 1px solid #D6D2CB;
  }

  tr:nth-child(even) {
    background-color: #FDFDFC;
  }

  tr:hover {
    background-color: #F6F5F4 !important;
  }
}
</style>
```

#### 21.6.2 表单卡片示例

``vue
<template>
  <div class="morandi-form-card">
    <h3>添加数据源</h3>
    <el-form :model="form" label-width="120px">
      <el-form-item label="数据源名称">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" class="morandi-primary-btn">保存</el-button>
        <el-button class="morandi-secondary-btn">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style lang="scss">
.morandi-form-card {
  background-color: #F6F5F4;
  border: 1px solid #D6D2CB;
  border-radius: 12px;
  padding: 24px;
  margin: 20px;

  h3 {
    color: #6B6763;
    margin-bottom: 20px;
  }
}

.morandi-primary-btn {
  background-color: #D4B3A1;
  border-color: #D4B3A1;
  color: white;
}

.morandi-secondary-btn {
  background-color: transparent;
  border-color: #8B8680;
  color: #8B8680;
}
</style>
```

### 21.7 注意事项

1. **色彩协调性**: 所有颜色搭配应保持整体协调，避免过多鲜艳颜色破坏莫兰迪色系的柔和感
2. **可读性**: 确保文字与背景之间有足够的对比度，保证内容可读性
3. **一致性**: 同一类型的组件应使用相同的颜色规范，确保界面风格统一
4. **适应性**: 在暗色模式下，应使用相应的莫兰迪色系变体
5. **无障碍设计**: 遵循WCAG 2.1标准，确保颜色使用对色盲用户友好

## 二十二、功能规划与开发流程

### 24.1 功能规划阶段

#### 24.1.1 需求收集与分析
- **用户故事**: 使用标准模板编写用户故事，包括角色、目标和价值
- **功能分解**: 将大功能拆分为小的可交付单元
- **优先级排序**: 根据业务价值和技术复杂度排序

```
# 示例：用户故事模板
## 作为 [用户角色]，我希望 [功能目标]，以便 [业务价值]

### 接受条件
- 条件1
- 条件2
- 条件3

### 技术需求
- 需要的API
- 需要的UI组件
- 需要的数据库表
```

#### 24.1.2 技术可行性评估
- **架构影响**: 评估新功能对现有架构的影响
- **性能考量**: 分析功能对系统性能的影响
- **安全评估**: 识别潜在的安全风险

### 24.2 开发阶段

#### 24.2.1 开发任务分解
- **前端任务**: UI组件开发、状态管理、API集成
- **后端任务**: API开发、数据模型设计、业务逻辑实现
- **测试任务**: 单元测试、集成测试、端到端测试

#### 24.2.2 开发流程
1. **分支创建**: 基于develop分支创建功能分支
2. **编码实现**: 遵循编码规范进行开发
3. **自测验证**: 开发完成后进行基本功能验证
4. **代码审查**: 提交Pull Request进行代码审查

### 24.3 测试阶段

#### 24.3.1 测试计划
- **单元测试**: 覆盖核心业务逻辑，覆盖率不低于80%
- **集成测试**: 验证模块间交互，包括API和数据库
- **端到端测试**: 验证完整用户场景，覆盖主要功能路径

#### 24.3.2 自动化测试执行
- **测试触发**: 代码提交后自动触发相关测试
- **测试报告**: 生成详细的测试报告和覆盖率报告
- **测试结果通知**: 测试失败时自动通知相关人员

### 24.4 部署阶段

#### 24.4.1 部署流程
1. **预发布环境**: 自动部署到预发布环境进行验证
2. **手动验证**: QA团队在预发布环境进行手动验证
3. **生产部署**: 验证通过后自动部署到生产环境
4. **健康检查**: 部署后进行系统健康检查

#### 24.4.2 回滚机制
- **一键回滚**: 出现严重问题时可快速回滚到上一版本
- **数据保护**: 回滚过程中保护用户数据不丢失
- **通知机制**: 回滚操作自动通知相关人员

### 24.5 监控与反馈

#### 24.5.1 功能监控
- **使用情况**: 监控新功能的使用情况和用户接受度
- **性能指标**: 监控功能相关的性能指标
- **错误日志**: 收集功能相关的错误日志

#### 24.5.2 用户反馈收集
- **反馈渠道**: 提供便捷的用户反馈渠道
- **数据分析**: 分析用户使用行为数据
- **改进计划**: 根据反馈制定功能改进计划

## 二十三、前端开发最佳实践与约束规范

### 23.1 组件开发规范

#### 23.1.1 组件设计原则
- **单一职责原则**: 每个组件只负责一个功能点，避免功能过于复杂
- **组件命名规范**: 使用帕斯卡命名法（PascalCase），如 `DataSourceTable.vue`、`TaskManagerCard.vue`
- **Props验证**: 所有props必须定义类型、默认值和必要性
- **事件命名**: 使用 kebab-case 命名自定义事件，如 `data-updated`、`item-deleted`

```vue
<!-- 示例：组件Props验证 -->
<script setup>
defineProps({
  // 必需的字符串
  title: {
    type: String,
    required: true
  },
  // 带默认值的数字
  limit: {
    type: Number,
    default: 10
  },
  // 可选的对象
  config: {
    type: Object,
    required: false,
    default: () => ({})
  }
})
</script>
```

#### 22.1.2 组件生命周期管理
- **资源清理**: 在 `onUnmounted` 中清理定时器、取消网络请求、移除事件监听器
- **状态管理**: 避免在组件外部维护复杂的状态，使用 Pinia 或组合式 API 管理状态

```javascript
// 示例：组件中资源清理
import { onMounted, onUnmounted } from 'vue'

let intervalId = null

onMounted(() => {
  intervalId = setInterval(() => {
    // 执行定时任务
  }, 1000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
```

### 22.2 类型安全与验证

#### 22.2.1 TypeScript 使用规范
- **接口定义**: 为所有复杂的 props、state 和 API 响应定义接口
- **类型推断**: 合理利用 TypeScript 的类型推断，减少冗余类型标注
- **联合类型**: 对于多态数据使用联合类型和类型守卫

```typescript
// 示例：接口定义
interface DataSource {
  id: string;
  sourceId: string; // 业务标识符，如 DS001
  name: string;
  status: 'online' | 'offline' | 'running';
  url: string;
  lastUpdate: Date;
}

// 类型守卫
function isOnline(source: DataSource): boolean {
  return source.status === 'online'
}
```

#### 22.2.2 运行时验证
- **API 响应验证**: 使用 Zod 或类似库验证 API 响应格式
- **用户输入验证**: 在提交前验证用户输入，提供即时反馈

### 22.3 状态管理规范

#### 22.3.1 Pinia Store 设计
- **模块化**: 按功能划分 Store，避免单个 Store 过于庞大
- **同步方法**: Store 中的方法应为同步的，异步操作使用 Actions
- **状态命名**: 使用名词命名状态，动词命名 Action

```javascript
// 示例：Pinia Store
import { defineStore } from 'pinia'

export const useDataSourceStore = defineStore('dataSource', {
  state: () => ({
    sources: [],
    loading: false,
    error: null
  }),
  
  getters: {
    onlineSources: (state) => state.sources.filter(s => s.status === 'online'),
    sourceById: (state) => (id) => state.sources.find(s => s.id === id)
  },
  
  actions: {
    async fetchSources() {
      this.loading = true
      try {
        const response = await api.get('/datasources')
        this.sources = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    }
  }
})
```

#### 22.3.2 组件状态管理
- **响应式数据**: 合理使用 ref/reactive，简单值用 ref，对象用 reactive
- **计算属性**: 复杂逻辑使用 computed，避免在模板中直接计算

### 22.4 API 调用与错误处理

#### 22.4.1 统一 API 层
- **API 封装**: 创建统一的 API 调用层，封装错误处理和请求拦截
- **类型安全**: 为所有 API 调用提供类型定义

```javascript
// 示例：API 层封装
import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 处理未授权错误
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

#### 22.4.2 错误处理策略
- **优雅降级**: 对于非关键功能，提供降级方案
- **用户反馈**: 错误信息应友好且有意义，避免显示技术性错误
- **日志记录**: 记录错误到监控系统，便于后续排查

### 22.5 调试辅助工具

#### 22.5.1 开发工具配置
- **Vue DevTools**: 安装并配置 Vue DevTools，便于调试组件状态
- **Source Maps**: 确保生产环境构建包含 Source Maps 以便调试
- **ESLint/Prettier**: 配置严格的代码规范，提前发现问题

#### 22.5.2 日志规范
- **结构化日志**: 使用结构化日志格式，包含上下文信息
- **日志级别**: 合理使用 info、warn、error 等不同级别
- **敏感信息**: 避免在日志中记录敏感信息（如密码、token）

```javascript
// 示例：结构化日志
function logEvent(event, context) {
  console.log(`[${new Date().toISOString()}] ${event}`, {
    component: context.component,
    userId: context.userId,
    additionalInfo: context.info
  })
}
```

### 22.6 测试策略

#### 22.6.1 单元测试
- **组件测试**: 测试组件渲染、props、emit 事件
- **工具函数测试**: 测试独立的工具函数和业务逻辑
- **API 测试**: Mock API 调用，测试各种响应情况

#### 22.6.2 集成测试
- **页面流程测试**: 测试用户在页面间的交互流程
- **状态管理测试**: 测试 Store 的状态变化和 Actions

#### 22.6.3 E2E 测试
- **关键路径**: 覆盖主要用户使用路径
- **自动化 CI**: 集成到 CI/CD 流程中，自动运行测试

### 22.7 代码审查清单

#### 22.7.1 审查要点
- [ ] 组件是否遵循单一职责原则
- [ ] Props 是否有适当的类型验证
- [ ] 是否正确处理了异步操作和错误
- [ ] 是否在组件销毁时清理了资源
- [ ] 是否使用了适当的 TypeScript 类型
- [ ] 是否遵循了 UI 设计规范（莫兰迪色风格）
- [ ] 是否添加了必要的注释和文档

#### 22.7.2 性能检查
- [ ] 避免不必要的重新渲染
- [ ] 合理使用虚拟滚动处理大数据列表
- [ ] 图片和其他资源是否经过优化
- [ ] 组件是否进行了适当的懒加载

### 22.8 前端性能优化

#### 22.8.1 渲染优化
- **虚拟滚动**: 对于大量数据的列表使用虚拟滚动
- **防抖节流**: 对于频繁触发的事件（如搜索、滚动）使用防抖或节流
- **图片懒加载**: 使用原生 `loading="lazy"` 或 Vue 指令实现图片懒加载

#### 22.8.2 包体积优化
- **代码分割**: 使用动态导入实现代码分割
- **Tree Shaking**: 移除未使用的代码
- **第三方库**: 评估第三方库的必要性，优先选择轻量级替代品

## 二十一、端到端测试规范与自动化

### 21.1 端到端测试策略

#### 21.1.1 测试范围定义
- **核心业务流程**: 用户登录、数据源配置、数据抓取、数据分析等主要功能
- **跨模块交互**: 前后端数据传递、状态同步、API调用链路
- **用户场景**: 模拟真实用户使用场景，覆盖主要操作路径
- **异常处理**: 网络中断、服务器错误、数据异常等情况

#### 23.1.2 测试工具选择
- **Playwright**: 用于浏览器自动化测试，支持多浏览器环境
- **测试框架**: Jest + Playwright，提供断言和测试组织能力
- **测试数据管理**: 使用工厂模式生成测试数据，确保测试环境纯净

```javascript
// 示例：Playwright测试配置
// playwright.config.js
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    baseURL: 'http://localhost:3000',
    headless: true,
    viewport: { width: 1280, height: 720 },
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
```

### 23.2 端到端测试开发规范

#### 23.2.1 测试用例编写
- **页面对象模型(POM)**: 封装页面元素和操作，提高可维护性
- **测试数据分离**: 将测试数据与测试逻辑分离，便于管理
- **断言策略**: 使用明确的断言验证预期结果，避免模糊验证

```javascript
// 示例：页面对象模型
// pages/login.page.js
class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('#username');
    this.passwordInput = page.locator('#password');
    this.loginButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.error-message');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}
```

#### 23.2.2 测试执行策略
- **并行执行**: 合理配置测试并行度，提高执行效率
- **环境隔离**: 每个测试使用独立的测试数据，避免相互干扰
- **失败重试**: 对于不稳定测试提供重试机制

### 23.3 端到端测试自动化流程

#### 23.3.1 CI/CD集成
- **触发时机**: 代码提交、Pull Request、定时任务
- **执行环境**: Docker容器化测试环境，确保环境一致性
- **报告生成**: 自动生成测试报告，包含截图、视频和日志

#### 23.3.2 测试环境管理
- **数据重置**: 每次测试前重置数据库到初始状态
- **服务启动**: 自动启动前端、后端、数据库等依赖服务
- **资源清理**: 测试完成后清理临时资源

```
# 示例：GitHub Actions配置
name: End-to-End Tests
on: [push, pull_request]
jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright Browsers
        run: npx playwright install --with-deps
      - name: Start application
        run: npm run dev &
      - name: Run E2E tests
        run: npx playwright test
```

### 23.4 端到端测试监控与报告

#### 23.4.1 测试指标
- **测试覆盖率**: 记录端到端测试覆盖的核心业务路径
- **执行时间**: 监控测试执行时间变化趋势
- **稳定性**: 统计测试通过率和失败重试情况

#### 23.4.2 失败分析
- **自动分析**: 自动分析失败原因，区分功能性问题和环境问题
- **错误归类**: 按照错误类型分类，便于问题定位
- **告警机制**: 关键测试失败时自动通知相关人员

## 二十二、前端开发最佳实践与约束规范

### 22.1 组件开发规范

#### 22.1.1 组件设计原则
- **用户故事**: 使用标准模板编写用户故事，包括角色、目标和价值
- **功能分解**: 将大功能拆分为小的可交付单元
- **优先级排序**: 根据业务价值和技术复杂度排序

```
# 示例：用户故事模板
## 作为 [用户角色]，我希望 [功能目标]，以便 [业务价值]

### 接受条件
- 条件1
- 条件2
- 条件3

### 技术需求
- 需要的API
- 需要的UI组件
- 需要的数据库表
```

#### 24.1.2 技术可行性评估
- **架构影响**: 评估新功能对现有架构的影响
- **性能考量**: 分析功能对系统性能的影响
- **安全评估**: 识别潜在的安全风险

### 24.2 开发阶段

#### 24.2.1 开发任务分解
- **前端任务**: UI组件开发、状态管理、API集成
- **后端任务**: API开发、数据模型设计、业务逻辑实现
- **测试任务**: 单元测试、集成测试、端到端测试

#### 24.2.2 开发流程
1. **分支创建**: 基于develop分支创建功能分支
2. **编码实现**: 遵循编码规范进行开发
3. **自测验证**: 开发完成后进行基本功能验证
4. **代码审查**: 提交Pull Request进行代码审查

### 24.3 测试阶段

#### 24.3.1 测试计划
- **单元测试**: 覆盖核心业务逻辑，覆盖率不低于80%
- **集成测试**: 验证模块间交互，包括API和数据库
- **端到端测试**: 验证完整用户场景，覆盖主要功能路径

#### 24.3.2 自动化测试执行
- **测试触发**: 代码提交后自动触发相关测试
- **测试报告**: 生成详细的测试报告和覆盖率报告
- **测试结果通知**: 测试失败时自动通知相关人员

### 24.4 部署阶段

#### 24.4.1 部署流程
1. **预发布环境**: 自动部署到预发布环境进行验证
2. **手动验证**: QA团队在预发布环境进行手动验证
3. **生产部署**: 验证通过后自动部署到生产环境
4. **健康检查**: 部署后进行系统健康检查

#### 24.4.2 回滚机制
- **一键回滚**: 出现严重问题时可快速回滚到上一版本
- **数据保护**: 回滚过程中保护用户数据不丢失
- **通知机制**: 回滚操作自动通知相关人员

### 24.5 监控与反馈

#### 24.5.1 功能监控
- **使用情况**: 监控新功能的使用情况和用户接受度
- **性能指标**: 监控功能相关的性能指标
- **错误日志**: 收集功能相关的错误日志

#### 24.5.2 用户反馈收集
- **反馈渠道**: 提供便捷的用户反馈渠道
- **数据分析**: 分析用户使用行为数据
- **改进计划**: 根据反馈制定功能改进计划
