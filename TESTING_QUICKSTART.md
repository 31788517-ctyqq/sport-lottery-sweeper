# 测试快速开始指南

## 🚀 5分钟内运行所有测试

### 第一步：环境检查
```bash
# 检查Node.js和Python
node --version  # 应该显示 18.x 或 20.x
python --version  # 应该显示 3.11+

# 检查依赖是否安装
cd frontend && npm list vitest playwright 2>/dev/null | head -5
cd ../backend && pip list | grep -E "pytest|coverage"
```

### 第二步：一键运行所有测试
```bash
# Linux/macOS
./scripts/run-all-tests.sh

# Windows
scripts\run-all-tests.bat
```

### 第三步：查看测试报告
```bash
# 前端覆盖率报告
open frontend/coverage/index.html

# 后端覆盖率报告
open backend/htmlcov/index.html

# E2E测试报告
open frontend/playwright-report/index.html
```

## 📋 常用测试命令

### 前端测试
```bash
cd frontend

# 运行所有单元测试
npm run test:run

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行组件测试
npm run test:components

# 运行API相关测试
npm run test:api

# 运行工具函数测试
npm run test:utils
```

### 后端测试
```bash
cd backend

# 运行所有单元测试
pytest tests/unit/ -v

# 运行单元测试带覆盖率
pytest tests/unit/ --cov=. --cov-report=html

# 运行集成测试
pytest tests/integration/ -v

# 运行特定测试文件
pytest tests/unit/api/test_auth.py -v
```

### 端到端测试
```bash
cd frontend

# 运行所有E2E测试
npm run test:e2e

# 以可视模式运行测试
npm run test:e2e:headed

# 调试模式
npm run test:e2e:debug
```

## 🧪 测试覆盖率检查

### 检查覆盖率阈值
```bash
# 运行覆盖率阈值检查
python scripts/check-coverage-thresholds.py

# 期望输出:
# ✅ 所有覆盖率检查通过
```

### 覆盖率目标
| 组件 | 语句 | 分支 | 函数 | 行 |
|------|------|------|------|-----|
| 前端 | ≥80% | ≥75% | ≥80% | ≥80% |
| 后端 | ≥80% | ≥70% | ≥80% | ≥80% |

## 🔧 故障排除

### 快速验证工具
项目提供了完整的验证工具套件，确保测试环境正确配置：

```bash
# 1. 快速检查测试环境（1分钟内）
python scripts/quick-test-check.py

# 2. 完整测试环境验证（3分钟内）
python scripts/validate-test-environment.py

# 3. CI/CD验证检查（5分钟内）
python scripts/validate-ci-checks.py

# 4. 运行完整验证套件（10分钟内）
python scripts/run-validation-suite.py

# 5. 生成统一测试报告
python scripts/generate-test-report.py
```

### 验证报告位置
| 验证类型 | 报告文件 | 描述 |
|----------|----------|------|
| 环境验证 | `test-reports/validation-suite-report.json` | 完整验证结果 |
| CI/CD检查 | `test-reports/ci-validation.json` | CI/CD配置检查 |
| 测试报告 | `test-reports/index.html` | 统一测试报告 |
| 覆盖率 | `test-reports/coverage/` | 聚合覆盖率报告 |

### 常见问题及解决方案

#### 1. "Cannot find module" 错误
```bash
# 重新安装依赖
cd frontend
rm -rf node_modules package-lock.json
npm ci
```

#### 2. 数据库连接失败
```bash
# 检查数据库配置
cd backend
cat .env.test

# 如果使用PostgreSQL，确保服务已启动
docker ps | grep postgres
```

#### 3. Playwright浏览器问题
```bash
# 重新安装浏览器
cd frontend
npx playwright install chromium

# 检查系统依赖
npx playwright install-deps
```

#### 4. 测试超时
```bash
# 增加超时时间
cd frontend
npm run test:e2e -- --timeout=60000

# 检查后端服务是否启动
curl http://localhost:8000/health
```

### 调试技巧

#### 前端测试调试
```bash
# 在浏览器中调试
npm run test:ui

# 监视模式
npm run test:watch
```

#### 后端测试调试
```bash
# 调试模式
pytest -v --pdb

# 输出详细堆栈
pytest -v --tb=long
```

#### E2E测试调试
```bash
# 调试模式（会打开浏览器）
npm run test:e2e:debug

# 慢速执行（观察操作）
npx playwright test --slowmo=1000
```

## 📊 测试报告生成

### 生成完整测试报告
```bash
# 运行完整CI流程
npm run test:ci

# 生成覆盖率汇总报告
python scripts/check-coverage-thresholds.py > coverage-report.txt
```

### 报告文件位置
| 报告类型 | 文件路径 | 描述 |
|----------|----------|------|
| 前端覆盖率 | `frontend/coverage/` | HTML覆盖率报告 |
| 后端覆盖率 | `backend/htmlcov/` | HTML覆盖率报告 |
| JUnit报告 | `frontend/test-results/` | XML格式测试结果 |
| Playwright报告 | `frontend/playwright-report/` | HTML交互式报告 |

## 🏗️ 添加新测试

### 前端测试文件结构
```
src/tests/unit/
├── components/        # 组件测试
│   ├── LoginForm.test.js
│   └── DataTable.test.js
├── api/              # API测试
│   ├── auth.test.js
│   └── sp.test.js
└── utils/            # 工具函数测试
    ├── format.test.js
    └── validate.test.js
```

### 创建新的组件测试
```javascript
// src/tests/unit/components/NewComponent.test.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import NewComponent from '@/components/NewComponent.vue'

describe('NewComponent', () => {
  it('应该正确渲染', () => {
    const wrapper = mount(NewComponent)
    expect(wrapper.text()).toContain('预期文本')
  })
})
```

### 后端测试文件结构
```
tests/
├── unit/              # 单元测试
│   ├── api/          # API测试
│   ├── models/       # 模型测试
│   └── services/     # 服务测试
└── integration/      # 集成测试
    ├── api/          # API集成测试
    └── database/     # 数据库集成测试
```

### 创建新的API测试
```python
# tests/unit/api/test_new_api.py
import pytest
from fastapi.testclient import TestClient

def test_new_endpoint_success(test_client: TestClient):
    response = test_client.get("/api/v1/new-endpoint")
    assert response.status_code == 200
    assert "data" in response.json()
```

## 🚨 紧急情况处理

### 测试大面积失败
```bash
# 1. 先运行单个测试确认问题
cd frontend
npm run test:run -- --run tests/unit/components/ProblemComponent.test.js

# 2. 如果前端服务问题，检查Mock数据
cat tests/fixtures/problem-data.json

# 3. 如果后端服务问题，检查测试数据库
cd backend
pytest tests/unit/api/test_problem_api.py -v --tb=short
```

### 覆盖率突然下降
```bash
# 1. 生成详细覆盖率报告
cd frontend
npm run test:coverage

# 2. 查看未覆盖的代码行
open frontend/coverage/lcov-report/index.html

# 3. 添加相应测试用例
```

## 📞 获取帮助

### 项目文档
- [TEST_INTEGRATION_PLAN.md](TEST_INTEGRATION_PLAN.md) - 完整测试集成规划
- [test-environment-setup.md](test-environment-setup.md) - 测试环境设置指南
- [API_VERIFICATION_GUIDE.md](API_VERIFICATION_GUIDE.md) - API验证指南

### 工具文档
- [Vitest](https://vitest.dev/guide/) - 前端测试框架
- [Playwright](https://playwright.dev/docs/intro) - 端到端测试
- [pytest](https://docs.pytest.org/) - 后端测试框架

### 联系支持
- **技术负责人**: 开发团队
- **测试问题**: 测试团队
- **紧急情况**: 运维团队

---

**最后更新**: 2026-01-28  
**适用版本**: v1.0.0+  
**维护状态**: 活跃维护