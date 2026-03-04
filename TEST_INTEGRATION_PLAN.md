# 竞彩足球扫盘系统 - 自动测试集成规划

## 📋 项目概述
- **项目名称**: sport-lottery-sweeper
- **技术栈**: Vue 3 + Vite + TypeScript (前端), FastAPI + PostgreSQL (后端)
- **现有测试**: 单元测试 (Vitest), 端到端测试 (Playwright), 后端测试 (pytest)
- **CI/CD**: GitHub Actions (已配置基础流水线)

## 🎯 目标
建立完整的自动化测试集成，实现：
1. 代码提交时自动运行相关测试
2. 测试覆盖率达标 (≥80%)
3. 快速反馈测试结果
4. 测试报告可视化
5. 测试环境与生产环境一致

## 📊 测试分层策略

### 1. 单元测试 (Unit Tests)
- **范围**: 前端组件、工具函数、后端模型、业务逻辑
- **工具**: Vitest (前端), pytest (后端)
- **覆盖率目标**: ≥85%
- **执行时机**: 每次提交、PR、定时任务

### 2. 集成测试 (Integration Tests)
- **范围**: API接口、数据库操作、外部服务集成
- **工具**: pytest + FastAPI TestClient, Playwright API testing
- **覆盖率目标**: ≥75%
- **执行时机**: PR合并前、每日构建

### 3. 端到端测试 (E2E Tests)
- **范围**: 完整用户流程、关键业务场景
- **工具**: Playwright (跨浏览器支持)
- **执行时机**: PR合并前、生产部署前

### 4. 性能测试 (Performance Tests)
- **范围**: API响应时间、页面加载性能、并发处理
- **工具**: k6, Lighthouse CI
- **执行时机**: 每周、发布前

## 🔧 工具链配置

### 前端测试配置
```javascript
// vitest.config.js (已存在)
{
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.js'],
    coverage: {
      provider: 'v8',
      thresholds: {
        statements: 80,
        branches: 75,
        functions: 80,
        lines: 80
      }
    }
  }
}
```

### 后端测试配置
```toml
# pyproject.toml (已配置)
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["backend"]
omit = ["*/tests/*", "*/venv/*", "*/__pycache__/*"]

[tool.coverage.report]
show_missing = true
skip_covered = false
fail_under = 80
```

### E2E测试配置
```javascript
// playwright.config.js (已存在)
{
  testDir: './tests/e2e',
  timeout: 30 * 1000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  }
}
```

## 🚀 CI/CD 流水线优化

### 现有流程分析
```yaml
当前流程:
1. 代码质量检查 (flake8, black, isort, eslint)
2. 后端测试 (单元+集成, PostgreSQL+Redis服务)
3. 前端测试 (单元+组件)
4. 安全扫描 (bandit, safety, npm audit)
5. 镜像构建 (main分支)
6. 部署 (staging/production)
```

### 优化建议

#### 1. 并行化执行
```yaml
# 将不依赖的测试并行执行
jobs:
  frontend-unit-tests:
    needs: [code-quality]
  
  backend-unit-tests:
    needs: [code-quality]
  
  e2e-tests:
    needs: [frontend-unit-tests, backend-unit-tests]
```

#### 2. 智能测试选择
- 基于文件变更运行相关测试
- 使用 `pytest --last-failed` 优先运行上次失败的测试
- Playwright 测试分组执行

#### 3. 测试报告整合
```yaml
steps:
  - name: 生成测试报告
    run: |
      # 合并覆盖率报告
      # 生成HTML测试报告
      # 上传到GitHub Pages
```

#### 4. 性能测试集成
```yaml
performance-tests:
  name: Performance Tests
  runs-on: ubuntu-latest
  steps:
    - name: 运行性能测试
      run: |
        k6 run tests/performance/api-load.js
        lighthouse-ci http://localhost:3000
```

## 📈 测试覆盖率监控

### 前端覆盖率
```json
{
  "statements": 80,
  "branches": 75,
  "functions": 80,
  "lines": 80
}
```

### 后端覆盖率
```json
{
  "statements": 80,
  "branches": 70,
  "functions": 80,
  "lines": 80
}
```

### 覆盖率报告工具
1. **Codecov**: 已集成，需优化配置
2. **SonarQube**: 可考虑集成代码质量分析
3. **GitHub Actions Artifacts**: 存储测试报告

## 🗄️ 测试数据管理

### 策略
1. **单元测试**: 使用 Mock/Stub
2. **集成测试**: 测试数据库 + 种子数据
3. **E2E测试**: 独立测试环境 + 自动化数据清理

### 测试数据库
```sql
-- tests/fixtures/test-data.sql
INSERT INTO users (id, username, password_hash, roles) 
VALUES 
  (1, 'test_admin', '$2b$12$...', 'admin'),
  (2, 'test_user', '$2b$12$...', 'user');
```

### 数据工厂
```python
# tests/factories/user_factory.py
class UserFactory:
    @staticmethod
    def create_admin():
        return User(
            username=f"admin_{random_string(8)}",
            password_hash=bcrypt.hashpw("password123"),
            roles=["admin"]
        )
```

## 🌐 测试环境管理

### 环境矩阵
| 环境 | 用途 | 数据库 | 外部服务 |
|------|------|--------|----------|
| CI | 自动化测试 | PostgreSQL容器 | Mock服务 |
| Staging | 集成测试 | 独立PostgreSQL | 模拟外部API |
| Production | 最终验证 | 生产数据库 | 真实外部API |

### Docker Compose 配置
```yaml
# docker-compose.test.yml
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: test_sport_lottery
  
  redis:
    image: redis:6-alpine
  
  backend:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/test_sport_lottery
```

## 📋 测试用例规范

### 命名规范
```
前端: src/tests/unit/[type]/[component].test.js
后端: tests/unit/[module]/test_[function].py
E2E: tests/e2e/[feature]/[scenario].spec.js
```

### 结构规范
```javascript
// 测试用例结构
describe('Component/Function', () => {
  beforeEach(() => {
    // 测试准备
  });
  
  it('应该完成某个行为', () => {
    // 执行 + 断言
  });
  
  afterEach(() => {
    // 清理
  });
});
```

### 断言库
- 前端: Vitest + Testing Library
- 后端: pytest + assert
- E2E: Playwright + expect

## 🔍 测试报告与监控

### 实时报告
1. **GitHub Actions Summary**: 测试结果摘要
2. **Codecov 评论**: PR覆盖率变化
3. **Slack 通知**: 测试失败告警

### 历史趋势
1. **覆盖率趋势图**: 监控覆盖率变化
2. **测试执行时间**: 优化测试性能
3. **失败率统计**: 识别不稳定测试

### 仪表板
```
测试仪表板 (建议):
- 总覆盖率: 85% ✓
- 单元测试: 890个 ✓
- 集成测试: 120个 ✓  
- E2E测试: 45个 ✓
- 平均执行时间: 12分钟
```

## 🛠️ 实施计划

### 第一阶段：基础优化 (1-2周)
1. 完善现有测试配置
2. 优化CI/CD并行执行
3. 统一测试报告格式
4. 建立测试数据管理

### 第二阶段：全面覆盖 (2-3周)
1. 补充关键功能测试
2. 集成性能测试
3. 建立测试监控
4. 优化测试执行速度

### 第三阶段：持续改进 (长期)
1. 智能测试选择
2. 测试质量分析
3. 自动化修复建议
4. 测试资产管理

## 📝 验收标准

### 功能性
- [x] 完整的测试执行脚本
- [x] 优化后的CI/CD流水线
- [x] 测试覆盖率检查机制
- [x] 详细的测试文档
- [x] 测试环境配置模板
- [ ] CI/CD流水线运行正常
- [ ] 测试覆盖率满足阈值要求
- [ ] 测试失败通知及时准确

### 性能性  
- [ ] 测试执行时间符合预期 (< 15分钟目标)
- [ ] 测试资源占用可控
- [ ] 并行执行效率 > 70%

### 可维护性
- [ ] 测试代码结构清晰
- [ ] 测试数据易于管理
- [ ] 测试环境一键搭建
- [ ] 测试报告易于分析

## 🔗 相关配置

### 环境变量
```bash
# .env.test
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_sport_lottery
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=test-secret-key
ENVIRONMENT=testing
```

### 脚本命令
```json
{
  "scripts": {
    "test:unit": "vitest run",
    "test:unit:watch": "vitest",
    "test:unit:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:ui": "playwright test --ui",
    "test:backend": "cd backend && pytest",
    "test:backend:coverage": "cd backend && pytest --cov",
    "test:ci": "npm run test:unit:coverage && npm run test:backend:coverage && npm run test:e2e"
  }
}
```

## 🚨 故障处理

### 常见问题
1. **测试不稳定**: 增加重试机制，优化异步等待
2. **环境差异**: 统一Docker环境，固定版本
3. **数据冲突**: 使用事务隔离，独立测试数据库
4. **执行超时**: 优化测试分组，增加超时配置

### 应急预案
```yaml
失败处理策略:
1. 首次失败: 自动重试 (max 2次)
2. 持续失败: 标记测试为flaky
3. 关键路径失败: 阻止部署，人工介入
4. 环境故障: 使用备份环境
```

## 📚 参考资料

### 项目文档
- [API 验证指南](API_VERIFICATION_GUIDE.md)
- [前端集成指南](FRONTEND_INTEGRATION_GUIDE.md)
- [配置设置指南](CONFIGURATION_SETUP.md)

### 工具文档
- [Vitest 官方文档](https://vitest.dev/)
- [Playwright 官方文档](https://playwright.dev/)
- [pytest 官方文档](https://docs.pytest.org/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

---

**最后更新**: 2026-01-28  
**负责人**: 开发团队  
**状态**: 规划阶段