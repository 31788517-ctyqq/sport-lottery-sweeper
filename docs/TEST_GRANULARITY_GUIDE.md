# 前端和后端测试颗粒度提升指导

> **版本**: 1.0  
> **创建日期**: 2026-02-12  
> **适用范围**: sport-lottery-sweeper 项目  

## 概述

本文档提供前端(Vue 3)和后端(FastAPI)测试颗粒度提升的具体方法和流程，帮助团队实现从粗粒度测试向精细化测试的演进，提高测试覆盖率、可靠性和可维护性。

## 1. 测试颗粒度等级定义

### 1.1 后端测试颗粒度

#### Level 1: 单元测试 (Unit Tests)
- **范围**: 单个函数、方法、类
- **隔离程度**: 完全隔离，使用mock/stub
- **执行时间**: < 100ms
- **覆盖率目标**: 80%+

#### Level 2: 集成测试 (Integration Tests)  
- **范围**: 模块间交互、数据库连接、外部API调用
- **隔离程度**: 部分隔离，真实依赖
- **执行时间**: 100ms - 2s
- **覆盖率目标**: 关键路径100%

#### Level 3: API测试 (API Tests)
- **范围**: 完整API端点测试
- **隔离程度**: 真实服务，测试数据库
- **执行时间**: 200ms - 5s
- **覆盖率目标**: 所有公开API

#### Level 4: 契约测试 (Contract Tests)
- **范围**: 前后端接口契约验证
- **隔离程度**: 模拟客户端/服务端
- **执行时间**: 100ms - 1s
- **覆盖率目标**: 所有API契约

### 1.2 前端测试颗粒度

#### Level 1: 组件单元测试 (Component Unit Tests)
- **范围**: 单个Vue组件渲染和逻辑
- **隔离程度**: 完全隔离，模拟props和emit
- **执行时间**: < 50ms
- **覆盖率目标**: 80%+

#### Level 2: 组件集成测试 (Component Integration Tests)
- **范围**: 组件间交互、插槽、provide/inject
- **隔离程度**: 部分隔离，真实子组件
- **执行时间**: 50ms - 500ms
- **覆盖率目标**: 复杂组件100%

#### Level 3: 页面测试 (Page Tests)
- **范围**: 完整页面功能和路由
- **隔离程度**: 真实路由和服务
- **执行时间**: 500ms - 2s
- **覆盖率目标**: 所有页面

#### Level 4: E2E测试 (End-to-End Tests)
- **范围**: 完整用户流程和业务流程
- **隔离程度**: 真实应用环境
- **执行时间**: 2s - 30s
- **覆盖率目标**: 核心业务流程

## 2. 后端测试颗粒度提升方法

### 2.1 现有问题分析

当前后端测试存在以下问题：
- 测试方法过于宽泛，一个测试包含多个断言
- 缺乏独立的单元测试，过度依赖数据库
- Mock使用不当，测试不够隔离
- 测试命名不规范，难以定位具体问题

### 2.2 具体实施流程

#### 步骤1: 梳理测试目标和范围
```python
# 示例：用户认证模块的测试分层
# Level 1: 单元测试 - 密码验证函数
def test_validate_password_strength():
    # 测试各种密码强度情况
    
# Level 2: 集成测试 - 用户创建流程  
def test_user_creation_with_database():
    # 测试用户创建涉及数据库的操作
    
# Level 3: API测试 - 注册接口
def test_register_endpoint():
    # 测试完整的注册API
    
# Level 4: 契约测试 - 注册接口契约
def test_register_contract():
    # 测试API输入输出格式契约
```

#### 步骤2: 重构现有测试文件

**Before (粗粒度)**:
```python
# tests/test_auth.py - 原有粗粒度测试
def test_auth_flow():
    # 一个测试包含登录、验证、权限检查等多个功能
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 权限验证
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    
    # 角色检查
    user_data = response.json()
    assert user_data["role"] == "user"
```

**After (细粒度)**:
```python
# tests/unit/test_auth_utils.py - 单元测试
def test_validate_login_credentials_success():
    """测试有效的登录凭据验证"""
    credentials = {"username": "test@example.com", "password": "validpass123"}
    result = validate_login_credentials(credentials)
    assert result.is_valid == True

def test_validate_login_credentials_invalid_password():
    """测试无效密码的凭据验证"""
    credentials = {"username": "test@example.com", "password": "wrongpass"}
    result = validate_login_credentials(credentials)
    assert result.is_valid == False

# tests/integration/test_auth_service.py - 集成测试
def test_authenticate_user_with_database():
    """测试用户认证与数据库的交互"""
    # 准备测试数据
    test_user = create_test_user()
    
    # 执行认证
    auth_result = authenticate_user(test_user.email, "correct_password")
    
    # 验证结果
    assert auth_result.user.id == test_user.id
    assert auth_result.token is not None

# tests/api/test_auth.py - API测试
def test_login_endpoint_success(client):
    """测试登录API成功场景"""
    login_data = {"username": "test@example.com", "password": "validpass123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_endpoint_invalid_credentials(client):
    """测试登录API无效凭据场景"""
    login_data = {"username": "test@example.com", "password": "wrongpass"}
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 401
```

#### 步骤3: 建立测试命名规范

```python
# 命名格式: test_{模块}_{场景}_{预期结果}
# 示例:
test_user_create_success_with_valid_data()
test_user_create_fails_with_duplicate_email()
test_user_create_validation_error_missing_required_field()
```

#### 步骤4: 完善Mock和Fixture策略

```python
# conftest.py - 共享fixtures
@pytest.fixture
def mock_external_api():
    """模拟外部API调用"""
    with patch('app.services.external_api.call'):
        yield

@pytest.fixture
def test_db():
    """测试数据库fixture"""
    db = create_test_database()
    yield db
    db.drop_all()

# 使用示例
def test_user_service_with_mock_external_api(mock_external_api, test_db):
    """使用mock的集成测试"""
    # 测试逻辑
```

### 2.3 测试工具和配置

#### pytest配置优化
```ini
# pytest.ini
[tool:pytest]
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
markers =
    unit: 单元测试
    integration: 集成测试
    api: API测试
    slow: 慢速测试
```

#### 测试数据库配置
```python
# tests/conftest.py
@pytest.fixture(scope="session")
def test_database_url():
    return "sqlite:///./test_sport_lottery.db"

@pytest.fixture(autouse=True)
def setup_test_db(test_database_url):
    # 设置测试数据库
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
```

## 3. 前端测试颗粒度提升方法

### 3.1 现有问题分析

当前前端测试存在以下问题：
- 过度依赖E2E测试，单元测试覆盖不足
- 组件测试缺乏props和事件模拟
- 测试缺乏用户行为模拟
- 测试文件组织混乱，难以维护

### 3.2 具体实施流程

#### 步骤1: 建立前端测试分层架构

```
frontend/tests/
├── unit/
│   ├── components/          # 组件单元测试
│   │   ├── admin/
│   │   └── common/
│   ├── composables/         # 组合式函数测试
│   ├── utils/              # 工具函数测试
│   └── store/              # 状态管理测试
├── integration/
│   ├── component-interactions/  # 组件交互测试
│   └── api-integration/    # API集成测试
├── e2e/
│   ├── pages/              # 页面级E2E测试
│   └── workflows/          # 业务流程E2E测试
└── fixtures/               # 测试数据和mock
```

#### 步骤2: 重构组件测试

**Before (粗粒度)**:
```javascript
// 原有测试 - 测试整个页面
it('should render admin panel correctly', () => {
  const wrapper = mount(AdminPanel)
  expect(wrapper.find('.stats-card').exists()).toBe(true)
  expect(wrapper.find('.filter-section').exists()).toBe(true)
  expect(wrapper.find('.results-section').exists()).toBe(true)
  // 一个测试验证太多内容
})
```

**After (细粒度)**:
```javascript
// tests/unit/components/admin/StatsCard.spec.js
import { mount } from '@vue/test-utils'
import StatsCard from '@/components/admin/StatsCard.vue'

describe('StatsCard', () => {
  // Level 1: 组件单元测试
  it('renders stats data correctly', () => {
    const props = {
      title: 'Total Users',
      value: 1500,
      icon: 'users'
    }
    const wrapper = mount(StatsCard, { props })
    
    expect(wrapper.text()).toContain('Total Users')
    expect(wrapper.text()).toContain('1500')
    expect(wrapper.find('.icon-users').exists()).toBe(true)
  })
  
  it('emits click event when clicked', async () => {
    const wrapper = mount(StatsCard, {
      props: { title: 'Test', value: 100 }
    })
    
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })
  
  it('applies custom CSS classes', () => {
    const wrapper = mount(StatsCard, {
      props: { 
        title: 'Test', 
        value: 100,
        cssClass: 'custom-style'
      }
    })
    
    expect(wrapper.classes()).toContain('custom-style')
  })
})

// tests/integration/component-interactions/AdminPanelInteractions.spec.js
import { mount } from '@vue/test-utils'
import AdminPanel from '@/views/admin/AdminPanel.vue'
import StatsCard from '@/components/admin/StatsCard.vue'

describe('AdminPanel Component Interactions', () => {
  // Level 2: 组件集成测试
  it('coordinates between StatsCard and FilterSection', async () => {
    const wrapper = mount(AdminPanel)
    
    // 模拟StatsCard点击事件
    const statsCard = wrapper.findComponent(StatsCard)
    await statsCard.vm.$emit('click')
    
    // 验证FilterSection收到通知并更新
    expect(wrapper.find('.filter-section').text()).toContain('Active')
  })
  
  it('passes filter criteria to ResultsSection', async () => {
    const wrapper = mount(AdminPanel)
    
    // 设置过滤器
    await wrapper.find('input[name="search"]').setValue('test')
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证结果区域接收到过滤条件
    expect(wrapper.find('.results-section').props('filters')).toMatchObject({
      search: 'test'
    })
  })
})
```

#### 步骤3: 完善Composables测试

```javascript
// tests/unit/composables/useAuth.spec.js
import { renderHook } from '@testing-library/vue'
import { useAuth } from '@/composables/useAuth.js'

describe('useAuth', () => {
  it('provides login function', () => {
    const { result } = renderHook(() => useAuth())
    
    expect(typeof result.current.login).toBe('function')
  })
  
  it('handles successful login', async () => {
    const { result } = renderHook(() => useAuth())
    
    // Mock API调用
    vi.mock('@/api/auth', () => ({
      login: vi.fn().mockResolvedValue({ token: 'fake-token' })
    }))
    
    await result.current.login('test@example.com', 'password')
    
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user.email).toBe('test@example.com')
  })
})
```

#### 步骤4: 优化API集成测试

```javascript
// tests/integration/api-integration/adminApi.spec.js
import { renderHook } from '@testing-library/vue'
import { useAdminApi } from '@/composables/useAdminApi.js'
import { server } from '../mocks/server'
import { rest } from 'msw'

describe('Admin API Integration', () => {
  beforeEach(() => {
    server.use(
      rest.get('/api/v1/admin/stats', (req, res, ctx) => {
        return res(ctx.json({ totalUsers: 1000, activeMatches: 50 }))
      })
    )
  })
  
  it('fetches admin statistics successfully', async () => {
    const { result } = renderHook(() => useAdminApi())
    
    const stats = await result.current.fetchStats()
    
    expect(stats.totalUsers).toBe(1000)
    expect(stats.activeMatches).toBe(50)
  })
  
  it('handles API errors gracefully', async () => {
    server.use(
      rest.get('/api/v1/admin/stats', (req, res, ctx) => {
        return res(ctx.status(500))
      })
    )
    
    const { result } = renderHook(() => useAdminApi())
    
    await expect(result.current.fetchStats()).rejects.toThrow()
  })
})
```

### 3.3 前端测试工具和配置

#### Vitest配置
```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80
      }
    }
  }
})
```

#### MSW (Mock Service Worker) 配置
```javascript
// tests/mocks/server.js
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)

server.listen()

setTimeout(() => {
  server.close()
}, 100)
```

## 4. 实施计划和里程碑

### 4.1 Phase 1: 基础建设 (Week 1-2)
- [ ] 建立测试目录结构
- [ ] 配置测试工具和CI集成
- [ ] 创建测试规范和模板
- [ ] 培训团队成员

### 4.2 Phase 2: 后端测试重构 (Week 3-4)
- [ ] 梳理现有后端测试
- [ ] 按颗粒度分层重构
- [ ] 建立Mock和Fixture策略
- [ ] 达到单元测试覆盖率80%

### 4.3 Phase 3: 前端测试重构 (Week 5-6)
- [ ] 梳理现有前端测试
- [ ] 按颗粒度分层重构
- [ ] 完善组件和API测试
- [ ] 达到组件测试覆盖率80%

### 4.4 Phase 4: E2E测试优化 (Week 7-8)
- [ ] 优化现有E2E测试
- [ ] 建立页面对象和业务流程测试
- [ ] 实现核心业务流程全覆盖
- [ ] 性能测试和稳定性改进

### 4.5 Phase 5: 持续改进 (Ongoing)
- [ ] 定期测试评审
- [ ] 覆盖率监控和告警
- [ ] 测试性能优化
- [ ] 新功能测试规范执行

## 5. 质量门禁和度量指标

### 5.1 质量门禁标准

| 测试类型 | 覆盖率目标 | 执行时间上限 | 失败率阈值 |
|---------|-----------|-------------|----------|
| 单元测试 | ≥ 80% | < 5分钟 | < 1% |
| 集成测试 | ≥ 90% | < 10分钟 | < 2% |
| API测试 | 100% | < 15分钟 | 0% |
| 组件测试 | ≥ 80% | < 5分钟 | < 1% |
| E2E测试 | 核心流程100% | < 30分钟 | < 5% |

### 5.2 度量指标仪表板

```javascript
// 建议的度量指标
const metrics = {
  testCoverage: {
    unit: 'line-coverage',
    integration: 'branch-coverage',
    e2e: 'scenario-coverage'
  },
  testPerformance: {
    avgExecutionTime: 'by-test-type',
    flakyTests: 'failure-rate-tracking',
    parallelization: 'efficiency-ratio'
  },
  testQuality: {
    assertionDensity: 'assertions-per-test',
    testIsolation: 'dependency-mock-ratio',
    maintainability: 'test-complexity-score'
  }
}
```

## 6. 最佳实践和建议

### 6.1 测试编写原则
1. **AAA模式**: Arrange-Act-Assert
2. **单一职责**: 每个测试只验证一个行为
3. **独立性**: 测试之间不应有依赖
4. **可读性**: 测试名称清晰描述行为
5. **快速执行**: 优化测试执行速度

### 6.2 常见陷阱避免
- ❌ 测试中包含业务逻辑
- ❌ 过度使用sleep/wait
- ❌ 忽略边界条件和异常情况
- ❌ 测试代码重复度高
- ❌ 忽视测试数据的清理

### 6.3 团队协作建议
- 代码审查包含测试审查
- 定期测试驱动开发(TDD)实践
- 建立测试技术分享机制
- 新人入职测试规范培训

## 7. 工具和参考资源

### 7.1 推荐工具链
- **后端**: pytest, pytest-cov, factory-boy, httpx
- **前端**: Vitest, @vue/test-utils, Testing Library, MSW
- **E2E**: Playwright, Cypress
- **CI/CD**: GitHub Actions, coverage reporting

### 7.2 学习资源
- [Testing Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Vue Testing Guide](https://vuejs.org/guide/scaling-up/testing.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Test Driven Development](https://www.amazon.com/dp/0321146530)

## 8. 附录

### 8.1 测试文件模板

#### 后端单元测试模板
```python
"""
测试文件: tests/unit/{module}/test_{functionality}.py
"""
import pytest
from unittest.mock import Mock, patch
from app.{module}.{functionality} import {FunctionalityClass}

class Test{FunctionalityClass}:
    """{FunctionalityClass} 单元测试"""
    
    def test_{method}_success(self):
        """测试{method}成功场景"""
        # Arrange
        obj = {FunctionalityClass}()
        
        # Act
        result = obj.{method}(test_data)
        
        # Assert
        assert result == expected_result
    
    def test_{method}_failure(self):
        """测试{method}失败场景"""
        # Arrange
        obj = {FunctionalityClass}()
        
        # Act & Assert
        with pytest.raises(ExpectedException):
            obj.{method}(invalid_data)
```

#### 前端组件测试模板
```javascript
/**
 * 测试文件: tests/unit/components/{component}.spec.js
 */
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import { ComponentName } from '@/components/{component}.vue'

describe('ComponentName', () => {
  it('renders correctly with props', () => {
    const props = { /* test props */ }
    const wrapper = mount(ComponentName, { props })
    
    expect(wrapper.exists()).toBe(true)
  })
  
  it('emits events when interacted', async () => {
    const wrapper = mount(ComponentName)
    
    await wrapper.trigger('click')
    
    expect(wrapper.emitted()).toHaveProperty('event-name')
  })
})
```

---

**文档维护**: 本文档应与项目测试实践同步更新，建议每季度review一次。  
**联系**: 如有疑问，请联系测试团队负责人。