# 项目测试目录结构说明

## 概述

本文档详细说明了项目中测试文件的组织结构，旨在帮助开发者更好地理解如何编写、组织和运行测试。

## 目录结构

```
tests/
├── unit/                 # 单元测试
│   ├── models/           # 数据模型单元测试
│   │   ├── test_user.py
│   │   ├── test_match.py
│   │   └── ...
│   ├── api/              # API单元测试
│   │   ├── test_auth_api.py
│   │   ├── test_match_api.py
│   │   └── ...
│   ├── services/         # 服务层单元测试
│   │   ├── test_auth_service.py
│   │   ├── test_match_service.py
│   │   └── ...
│   └── schemas/          # 数据模式单元测试
│       ├── test_user_schema.py
│       └── ...
├── integration/          # 集成测试
│   ├── database/         # 数据库集成测试
│   │   ├── test_user_db_ops.py
│   │   └── ...
│   ├── api/              # API集成测试
│   │   ├── test_auth_integration.py
│   │   └── ...
│   └── services/         # 服务间集成测试
│       ├── test_auth_match_integration.py
│       └── ...
├── e2e/                 # 端到端测试
│   ├── api/              # API端到端测试
│   │   └── test_complete_api_workflow.py
│   └── scenarios/        # 业务场景端到端测试
│       ├── test_complete_workflow.py
│       └── test_user_journey.py
└── functional/          # 功能测试
    ├── test_backend_alive.py
    ├── test_user_management.py
    ├── test_sporttery_detailed.py
    └── ...
```

## 测试类型说明

### 1. 单元测试 (Unit Tests)

**目的**: 验证单个函数、类或模块的独立功能。

**特点**:
- 快速执行
- 隔离性强
- 易于定位问题

**文件命名**: `test_[module_name].py`

**放置位置**:
- `tests/unit/models/` - 模型类的测试
- `tests/unit/api/` - API路由和控制器的测试
- `tests/unit/services/` - 服务层函数的测试
- `tests/unit/schemas/` - 数据模式验证的测试

### 2. 集成测试 (Integration Tests)

**目的**: 验证多个模块之间的交互和数据流转。

**特点**:
- 涉及多个组件
- 模拟真实环境
- 检查接口兼容性

**文件命名**: `test_[component1]_[component2]_integration.py`

**放置位置**:
- `tests/integration/database/` - 数据库操作的集成测试
- `tests/integration/api/` - API之间的交互测试
- `tests/integration/services/` - 服务之间的交互测试

### 3. 端到端测试 (End-to-End Tests)

**目的**: 验证完整的业务流程和用户旅程。

**特点**:
- 模拟真实用户操作
- 涵盖多个系统组件
- 验证整体功能

**文件命名**: `test_[user_journey_name].py`

**放置位置**:
- `tests/e2e/scenarios/` - 业务场景测试
- `tests/e2e/api/` - API端到端测试

### 4. 功能测试 (Functional Tests)

**目的**: 验证特定功能的正确性，可能跨越多种测试类型。

**特点**:
- 验证特定功能点
- 可能结合多种测试方法
- 针对特定业务逻辑

## 运行测试

### 运行特定类型的测试

```bash
# 运行单元测试
python tests/functional/run_tests.py unit

# 运行集成测试
python tests/functional/run_tests.py integration

# 运行端到端测试
python tests/functional/run_tests.py e2e

# 运行功能测试
python tests/functional/run_tests.py functional
```

### 运行所有测试

```bash
# 运行所有测试
python tests/functional/run_tests.py all

# 运行带覆盖率的测试
python tests/functional/run_tests.py coverage
```

### 使用pytest直接运行

```bash
# 运行特定目录的测试
pytest tests/unit/

# 运行特定文件的测试
pytest tests/unit/test_user.py

# 运行带详细输出的测试
pytest tests/unit/ -v

# 运行带覆盖率的测试
pytest tests/ --cov=.
```

## 编写测试的最佳实践

### 1. 测试命名规范

- 使用描述性的测试函数名，例如 `test_create_user_with_valid_data_returns_success`
- 使用一致的前缀，如 `test_`

### 2. 测试结构

每个测试应遵循 AAA 模式：

```python
def test_example():
    # Arrange (准备)
    # 设置测试所需的初始状态和数据
    
    # Act (执行)
    # 执行要测试的操作
    
    # Assert (断言)
    # 验证结果是否符合预期
```

### 3. 测试数据管理

- 使用 fixtures 来管理共享的测试数据
- 确保测试数据的独立性，避免测试间的相互影响
- 使用工厂函数创建复杂的测试数据

### 4. 测试环境

- 确保测试在隔离的环境中运行
- 使用内存数据库或临时数据库进行测试
- 测试完成后清理资源

## 维护说明

- 新增测试文件时，请根据测试类型放置到相应的目录
- 定期审查和重构测试代码，保持其有效性
- 当修改功能时，相应地更新或添加测试
- 保持高测试覆盖率，特别是对核心业务逻辑

## CI/CD 集成

在持续集成环境中，建议按以下顺序运行测试：

1. 单元测试 (快速反馈)
2. 集成测试 (验证集成)
3. 端到端测试 (验证整体功能)
4. 功能测试 (验证特定功能)

这样可以在早期发现问题，提高开发效率。