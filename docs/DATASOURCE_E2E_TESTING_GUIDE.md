# 数据源管理模块端到端测试指南

## 概述

本文档介绍如何运行数据源管理模块的端到端测试，验证模块的完整功能链路。

## 测试目标

- 验证前端界面与后端API的完整交互
- 测试数据源的CRUD操作
- 验证健康检查和批量操作功能
- 确保数据模型与前端需求匹配

## 测试环境要求

- Python 3.8+
- Node.js (前端开发)
- 数据库 (SQLite/PostgreSQL/MySQL)
- 后端服务运行在 `http://localhost:8000`

## 启动后端服务

```bash
# 进入项目目录
cd c:\Users\11581\Downloads\sport-lottery-sweeper

# 启动后端服务
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## 运行端到端测试

### 方法一：使用测试运行脚本

```bash
# 运行测试脚本
python run_datasource_e2e_test.py
```

### 方法二：直接运行测试文件

```bash
# 使用pytest运行测试
python -m pytest tests/e2e/test_datasource_management_e2e.py -v

# 或者直接运行Python文件
python -m tests.e2e.test_datasource_management_e2e
```

## 测试内容详解

### 1. 完整工作流程测试

- 获取数据源列表（初始状态）
- 创建新数据源
- 验证数据源创建
- 测试数据源连接
- 更新数据源信息
- 批量测试多个数据源
- 删除数据源
- 验证数据清理

### 2. 前端用户操作模拟测试

- 模拟用户进入数据源管理页面
- 执行筛选操作
- 创建数据源
- 测试连接
- 编辑数据源
- 批量操作
- 删除数据源

## 测试用例覆盖

### API端点测试

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/admin/v1/sources` | GET | 获取数据源列表 |
| `/api/admin/v1/sources` | POST | 创建数据源 |
| `/api/admin/v1/sources/{id}` | GET | 获取数据源详情 |
| `/api/admin/v1/sources/{id}` | PUT | 更新数据源 |
| `/api/admin/v1/sources/{id}` | DELETE | 删除数据源 |
| `/api/admin/v1/sources/{id}/health` | GET | 测试数据源连接 |
| `/api/admin/v1/sources/batch/test` | POST | 批量测试数据源 |

### 功能验证

- [x] 数据源创建
- [x] 数据源读取
- [x] 数据源更新
- [x] 数据源删除
- [x] 数据源测试连接
- [x] 数据源批量操作
- [x] 分页功能
- [x] 筛选功能
- [x] 统计信息

## 预期结果

- 所有API端点返回正确的HTTP状态码
- 数据库中的记录与操作一致
- 返回的数据结构符合前端要求
- 所有测试用例通过

## 环境变量

可以通过环境变量配置测试：

```bash
# 设置测试服务器URL
export TEST_BASE_URL=http://localhost:8000

# 设置管理员令牌
export ADMIN_TOKEN=your-admin-jwt-token
```

## 故障排除

### 1. 后端服务不可用

如果收到连接错误，请确保后端服务正在运行：

```bash
curl http://localhost:8000/health/ready
```

### 2. 权限错误

确保请求头中包含有效的管理员JWT令牌。

### 3. 数据库连接错误

检查数据库配置和连接字符串是否正确。

## 扩展测试

如需扩展测试，可以修改 `tests/e2e/test_datasource_management_e2e.py` 文件，添加更多测试场景。

## 测试结果验证

测试完成后，您应该看到类似以下的成功消息：

```
========================================================
数据源管理模块端到端测试通过！
数据源管理模块功能完整，已达到生产就绪状态
========================================================
```

## 注意事项

- 测试过程中会创建和删除测试数据
- 确保数据库有足够的权限进行CRUD操作
- 在生产环境中运行测试前，请确认不会影响现有数据