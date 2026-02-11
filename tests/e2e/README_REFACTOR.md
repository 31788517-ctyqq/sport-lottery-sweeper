# E2E测试重构计划

## 当前问题
- `test_datasource_management_e2e.py` (412KB) - 文件过大，难以维护
- 混合了多种测试场景在一个文件中
- 测试执行时间长，失败定位困难

## 重构目标
- 按功能模块拆分大文件
- 提高测试执行效率
- 增强测试可维护性
- 实现并行执行

## 拆分方案

### 1. 数据源管理模块拆分
**原文件**: `test_datasource_management_e2e.py` → **拆分为**:

```
tests/e2e/datasource/
├── __init__.py
├── conftest.py                 # 共享fixture和配置
├── test_datasource_crud.py     # CRUD操作测试 (~50KB)
├── test_datasource_workflow.py  # 完整工作流测试 (~80KB) 
├── test_datasource_health.py    # 健康检查测试 (~30KB)
├── test_datasource_batch.py     # 批量操作测试 (~40KB)
├── test_datasource_categories.py # 分类管理测试 (~35KB)
└── test_datasource_permissions.py # 权限测试 (~25KB)
```

### 2. 具体拆分内容规划

#### test_datasource_crud.py
- 创建数据源
- 读取数据源详情
- 更新数据源
- 删除数据源
- 列表查询和分页

#### test_datasource_workflow.py  
- 完整业务工作流（原文件的主要流程）
- 多步骤集成测试
- 端到端用户场景

#### test_datasource_health.py
- 数据源健康检测
- 连接测试
- 响应时间测试
- 可用性监控

#### test_datasource_batch.py
- 批量创建数据源
- 批量更新状态
- 批量删除
- 批量健康检查

#### test_datasource_categories.py
- 按分类筛选
- 分类统计
- 分类管理操作

#### test_datasource_permissions.py
- 权限验证
- 角色访问控制
- 认证token测试

### 3. 共享资源文件

#### conftest.py
```python
import pytest
import os
from typing import Dict, Any

@pytest.fixture(scope="session")
def base_url():
    return os.getenv("TEST_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def admin_headers():
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "demo-jwt-token")
    return {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }

@pytest.fixture
def base_api_url(base_url):
    return f"{base_url}/api/admin/v1"

# 其他共享fixture...
```

## 实施步骤

### Phase 1: 准备工作 (Day 1)
1. 创建新的目录结构
2. 提取共享fixture到conftest.py
3. 设置测试标记和分类

### Phase 2: 逐步拆分 (Day 2-3)
1. 先拆分最简单的测试文件（如权限测试）
2. 逐个迁移测试用例
3. 保持测试覆盖率不变

### Phase 3: 优化和验证 (Day 4)
1. 更新CI/CD配置支持并行执行
2. 验证所有测试通过
3. 性能对比测试

### Phase 4: 清理和优化 (Day 5)
1. 删除原大文件
2. 更新文档和导入路径
3. 优化测试执行时间

## 预期收益

### 维护性提升
- 单文件大小控制在50KB以内
- 测试逻辑更清晰
- 问题定位更容易

### 执行效率提升  
- 支持并行执行（预计节省60%时间）
- 可以只运行相关模块的测试
- 减少不必要的测试加载

### 团队协作改善
- 多人可以同时修改不同模块
- 代码审查更容易
- 新人上手更快

## 风险控制

### 回滚方案
- 保留原文件作为backup_original.py
- 分阶段提交，每步都可回滚
- 保持测试通过率100%

### 质量保证
- 每个拆分后的文件都要单独验证
- 保持原有的测试覆盖率
- 执行完整的回归测试
