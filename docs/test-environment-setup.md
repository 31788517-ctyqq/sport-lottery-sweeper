# 测试环境设置指南

## 概述
本文档描述如何为竞彩足球扫盘系统设置完整的测试环境，包括单元测试、集成测试和端到端测试。

## 环境要求

### 硬件要求
- CPU: 2核以上
- 内存: 4GB以上
- 磁盘空间: 10GB以上

### 软件要求
- **操作系统**: Ubuntu 20.04+/macOS 10.15+/Windows 10+
- **Node.js**: 18.x 或 20.x
- **Python**: 3.11+
- **Docker**: 20.10+ (可选，用于容器化测试)
- **Git**: 2.30+

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-username/sport-lottery-sweeper.git
cd sport-lottery-sweeper
```

### 2. 安装前端依赖
```bash
cd frontend
npm ci  # 或 npm install
```

### 3. 安装后端依赖
```bash
cd backend
pip install -r requirements-dev.txt
pip install -r requirements.txt
```

### 4. 安装测试工具
```bash
# 前端测试工具
cd frontend
npx playwright install chromium

# 后端测试工具（已通过requirements-dev.txt安装）
# 无额外步骤
```

## 测试环境配置

### 前端测试环境
创建前端测试环境配置文件：

```bash
# frontend/.env.test
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_ENV=testing
VITE_USE_MOCK=true
```

### 后端测试环境
创建后端测试环境配置文件：

```bash
# backend/.env.test
DATABASE_URL=sqlite:///./test.db  # 使用SQLite进行单元测试
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=test-secret-key-for-local-testing
ENVIRONMENT=testing
DEBUG=true
LOG_LEVEL=INFO
```

## 数据库设置

### 测试数据库
1. **SQLite** (推荐用于单元测试):
   ```bash
   cd backend
   # 数据库文件会自动创建
   ```

2. **PostgreSQL** (用于集成测试):
   ```bash
   # 使用Docker启动PostgreSQL
   docker run --name test-postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=test_sport_lottery \
     -p 5432:5432 \
     -d postgres:13
   ```

### 初始化测试数据
```bash
# 运行测试数据初始化脚本
cd backend
python scripts/init_test_data.py
```

## 测试执行

### 运行所有测试
```bash
# 使用提供的脚本
./scripts/run-all-tests.sh  # Linux/macOS
scripts\run-all-tests.bat   # Windows
```

### 分阶段运行测试

#### 1. 前端单元测试
```bash
cd frontend
npm run test:run  # 运行测试
npm run test:watch  # 监视模式
npm run test:coverage  # 带覆盖率报告
```

#### 2. 后端单元测试
```bash
cd backend
pytest tests/unit/ -v  # 运行单元测试
pytest tests/unit/ --cov=. --cov-report=html  # 带覆盖率报告
```

#### 3. 后端集成测试
```bash
cd backend
pytest tests/integration/ -v  # 运行集成测试
```

#### 4. 端到端测试
```bash
cd frontend
npx playwright test tests/e2e/  # 运行E2E测试
npx playwright test --headed  # 带浏览器界面
```

## 测试数据管理

### 测试数据工厂
项目使用工厂模式生成测试数据：

```python
# tests/factories/user_factory.py
from backend.models.user import User
import factory

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.Sequence(lambda n: f"test{n}@example.com")
    password_hash = factory.LazyAttribute(lambda o: bcrypt.hashpw("password123"))
```

### 测试数据清理
每个测试用例会自动清理测试数据：
```python
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """自动清理测试数据"""
    yield
    # 测试结束后清理
    clean_test_database()
```

## 覆盖率报告

### 生成覆盖率报告
```bash
# 前端覆盖率
cd frontend
npm run test:coverage

# 后端覆盖率  
cd backend
pytest --cov=. --cov-report=html --cov-report=xml
```

### 查看覆盖率报告
1. **前端**: 打开 `frontend/coverage/index.html`
2. **后端**: 打开 `backend/htmlcov/index.html`
3. **综合报告**: 运行 `./scripts/check-coverage-thresholds.py`

## 持续集成

### GitHub Actions
项目已配置GitHub Actions工作流：
- **文件**: `.github/workflows/ci-cd-optimized.yml`
- **触发条件**: push到main/develop分支或PR
- **执行任务**:
  1. 代码质量检查
  2. 单元测试
  3. 集成测试
  4. 端到端测试
  5. 覆盖率检查
  6. 构建部署

### 本地CI模拟
```bash
# 运行完整CI流程
./scripts/run-ci-local.sh
```

## 故障排除

### 常见问题

#### 1. 前端测试报错 "Cannot find module"
```bash
# 清理并重新安装依赖
cd frontend
rm -rf node_modules package-lock.json
npm ci
```

#### 2. 后端测试数据库连接失败
```bash
# 检查数据库服务
cd backend
# 确保使用测试数据库配置
cp .env.test .env
```

#### 3. Playwright浏览器无法启动
```bash
# 重新安装浏览器
cd frontend
npx playwright install chromium
```

#### 4. 覆盖率报告未生成
```bash
# 检查测试是否正常运行
cd frontend
npm run test:run
# 如果测试失败，先修复测试
```

### 日志和调试

#### 启用详细日志
```bash
# 前端测试详细日志
cd frontend
npm run test:run -- --verbose

# 后端测试详细日志
cd backend
pytest -v --tb=long
```

#### 调试E2E测试
```bash
# 使用Playwright调试模式
cd frontend
npx playwright test --debug
```

## 测试最佳实践

### 1. 测试命名规范
- 单元测试: `test_[function]_[scenario].py`
- 集成测试: `test_integration_[feature].py`
- E2E测试: `[feature].spec.js`

### 2. 测试结构
```python
def test_function_success():
    # Arrange - 准备数据
    # Act - 执行操作
    # Assert - 验证结果
```

### 3. 测试独立性
- 每个测试应该独立运行
- 测试之间不共享状态
- 使用setup/teardown管理测试环境

### 4. 测试性能
- 单元测试: < 1秒
- 集成测试: < 10秒  
- E2E测试: < 30秒

## 扩展测试

### 性能测试
```bash
# 使用k6运行性能测试
k6 run tests/performance/api-load.js
```

### 安全测试
```bash
# 运行安全扫描
cd backend
bandit -r .
safety check
```

### 负载测试
```bash
# 使用Locust运行负载测试
locust -f tests/load/locustfile.py
```

## 资源链接

### 文档
- [Vitest官方文档](https://vitest.dev/)
- [Playwright官方文档](https://playwright.dev/)
- [pytest官方文档](https://docs.pytest.org/)
- [GitHub Actions文档](https://docs.github.com/en/actions)

### 工具
- [Codecov](https://about.codecov.io/)
- [SonarQube](https://www.sonarqube.org/)
- [Docker](https://www.docker.com/)

---

**最后更新**: 2026-01-28  
**维护者**: 测试团队  
**相关文档**: [TEST_INTEGRATION_PLAN.md](TEST_INTEGRATION_PLAN.md)