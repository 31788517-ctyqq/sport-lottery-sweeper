# 用户管理系统使用指南

## 概述

本系统提供了完善的后台用户管理功能，包括后台管理员和前台用户的全面管理。

## 功能特性

### 后台用户管理

1. **用户列表管理**
   - 分页显示所有后台管理员
   - 支持按角色、状态、部门筛选
   - 支持按用户名、真实姓名、邮箱搜索

2. **用户创建**
   - 创建新的后台管理员账户
   - 设置角色权限、部门、职位等信息

3. **用户详情查看**
   - 查看用户详细信息
   - 显示创建者、最后登录时间等

4. **用户信息编辑**
   - 修改用户基本信息
   - 更新联系方式、部门、职位等

5. **用户状态管理**
   - 激活/停用/锁定/解冻用户
   - 控制用户访问权限

6. **密码重置/修改**
   - 管理员可为用户重置密码
   - 强制用户下次登录时修改密码

7. **用户统计**
   - 显示用户总数、活跃用户数
   - 按角色、部门统计用户分布
   - 展示最近登录情况

8. **操作日志查看**
   - 查看用户的所有操作记录
   - 了解用户行为轨迹

9. **登录日志查看**
   - 查看用户登录历史
   - 了解登录地点、设备等信息

### 前台用户管理

1. **用户列表管理**
   - 分页显示所有前台用户
   - 支持按用户类型、状态筛选
   - 支持按用户名、昵称、邮箱搜索

2. **用户创建**
   - 创建新的前台用户账户
   - 设置用户类型、状态等信息

3. **用户详情查看**
   - 查看用户详细信息
   - 显示关注数、粉丝数等社交数据

4. **用户信息编辑**
   - 修改用户基本信息
   - 更新个人资料、联系方式等

5. **用户状态管理**
   - 激活/停用/封禁用户
   - 控制用户访问权限

6. **密码重置/修改**
   - 管理员可为用户重置密码

## API 接口

### 后台用户管理接口

- `GET /api/v1/admin-users/` - 获取后台用户列表
- `POST /api/v1/admin-users/` - 创建后台用户
- `GET /api/v1/admin-users/{id}` - 获取用户详情
- `PUT /api/v1/admin-users/{id}` - 更新用户信息
- `PUT /api/v1/admin-users/{id}/status` - 更新用户状态
- `PUT /api/v1/admin-users/{id}/reset-password` - 重置用户密码
- `DELETE /api/v1/admin-users/{id}` - 删除用户
- `GET /api/v1/admin-users/stats` - 获取用户统计信息

### 前台用户管理接口

- `GET /api/v1/frontend-users/` - 获取前台用户列表
- `POST /api/v1/frontend-users/` - 创建前台用户
- `GET /api/v1/frontend-users/{id}` - 获取用户详情
- `PUT /api/v1/frontend-users/{id}` - 更新用户信息
- `PUT /api/v1/frontend-users/{id}/status` - 更新用户状态
- `PUT /api/v1/frontend-users/{id}/reset-password` - 重置用户密码
- `DELETE /api/v1/frontend-users/{id}` - 删除用户

## 模拟数据管理

系统提供了生成和清理模拟数据的脚本：

### 生成模拟数据

```bash
# Windows
python scripts/simple_mock_users.py create

# 或者在backend目录
cd backend
python ../scripts/simple_mock_users.py create
```

### 清理模拟数据

```bash
# Windows
python scripts/simple_mock_users.py cleanup

# 或者在backend目录
cd backend
python ../scripts/simple_mock_users.py cleanup
```

### 模拟数据规模

- **后台用户**: 11个（1个超级管理员 + 10个其他角色）
- **前台用户**: 0个（可扩展）
- **操作日志**: 约100-110条
- **登录日志**: 约90-110条

### 模拟数据标识符

`mock_data_2026_01_19` - 所有模拟数据的用户名都包含此标识符，便于查找和清理

### 测试账号

| 用户名 | 邮箱 | 密码 | 角色 | 状态 |
|--------|------|------|------|------|
| sa_mock_data_2026_01_19 | sa_mock_data_2026_01_19@example.com | SuperAdmin@123456 | SUPER_ADMIN | ACTIVE |

其他管理员的默认密码：`Admin@123456`

## 前台用户管理
系统同样提供了完整的前台用户管理功能，用于管理注册的普通用户、高级会员和分析师等不同类型的用户。

## 后台用户管理
后台用户管理允许超级管理员和其他有权限的管理员管理后台系统用户，确保系统安全和操作合规。

```

