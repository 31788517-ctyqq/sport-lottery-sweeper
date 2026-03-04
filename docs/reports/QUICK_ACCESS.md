# 用户管理系统 - 快速访问指南

## 🚀 快速启动

### 一键启动（推荐）
```bash
start_user_management.bat
```

### 手动启动
```bash
# 1. 生成模拟数据
python scripts/simple_mock_users.py create

# 2. 启动后端
cd backend
python main.py

# 3. 启动前端（新终端窗口）
cd frontend
pnpm dev
```

---

## 🌐 访问地址

### 前端页面
- **主页**: http://localhost:3000
- **后台用户管理**: http://localhost:3000/admin-users
- **前台用户管理**: http://localhost:3000/frontend-users
- **登录页面**: http://localhost:3000/login

### 后端API
- **API文档 (Swagger)**: http://localhost:8000/docs
- **API文档 (ReDoc)**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

### API端点
- **后台用户管理**: http://localhost:8000/api/v1/admin-users
- **前台用户管理**: http://localhost:8000/api/v1/frontend-users
- **管理员后台用户**: http://localhost:8000/api/v1/admin/backend-users
- **管理员前台用户**: http://localhost:8000/api/v1/admin/users

---

## 🔐 测试账号

### 超级管理员
- **用户名**: `sa_mock_data_2026_01_19`
- **密码**: `SuperAdmin@123456`
- **角色**: SUPER_ADMIN
- **状态**: ACTIVE

### 其他管理员
- **用户名**: `admin_0_mock_data_2026_01_19` ~ `admin_9_mock_data_2026_01_19`
- **密码**: `Admin@123456`
- **角色**: admin / moderator / auditor / operator
- **状态**: active / inactive / suspended / locked

---

## 📋 功能清单

### 后台用户管理 (`/admin-users`)
- ✅ 用户列表展示（分页）
- ✅ 搜索（用户名/真实姓名/邮箱）
- ✅ 筛选（角色/状态/部门）
- ✅ 创建用户
- ✅ 编辑用户
- ✅ 删除用户
- ✅ 重置密码
- ✅ 更新状态
- ✅ 查看详情
- ✅ 查看操作日志
- ✅ 查看登录日志
- ✅ 统计信息展示

### 前台用户管理 (`/frontend-users`)
- ✅ 用户列表展示（分页）
- ✅ 搜索（用户名/昵称/邮箱）
- ✅ 筛选（状态/用户类型）
- ✅ 创建用户
- ✅ 编辑用户
- ✅ 删除用户
- ✅ 重置密码
- ✅ 更新状态
- ✅ 批量操作
- ✅ 统计信息展示

---

## 🧹 数据管理

### 查看模拟数据
```bash
# 检查数据库中的模拟数据
python -c "import sqlite3; conn = sqlite3.connect('sport_lottery.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM admin_users'); print('后台用户:', cursor.fetchone()[0]); cursor.execute('SELECT COUNT(*) FROM users'); print('前台用户:', cursor.fetchone()[0]); cursor.execute('SELECT COUNT(*) FROM admin_operation_logs'); print('操作日志:', cursor.fetchone()[0]); cursor.execute('SELECT COUNT(*) FROM admin_login_logs'); print('登录日志:', cursor.fetchone()[0]); conn.close()"
```

### 清理模拟数据
```bash
python scripts/simple_mock_users.py cleanup
```

### 重新生成模拟数据
```bash
python scripts/simple_mock_users.py create
```

---

## 📁 相关文件

### 后端
- `backend/api/v1/admin_user_management.py` - 后台用户管理API
- `backend/api/v1/frontend_user_management.py` - 前台用户管理API
- `backend/models/admin_user.py` - 后台用户模型
- `backend/models/user.py` - 前台用户模型
- `backend/crud/admin_user.py` - 后台用户CRUD
- `backend/schemas/admin_user.py` - 后台用户Schema

### 前端
- `frontend/src/views/admin/users/BackendUsers.vue` - 后台用户管理页面
- `frontend/src/views/admin/users/FrontendUsers.vue` - 前台用户管理页面
- `frontend/src/api/modules/backendUsers.js` - 后台用户API调用
- `frontend/src/api/modules/frontendUsers.js` - 前台用户API调用

### 脚本
- `scripts/simple_mock_users.py` - 模拟数据生成/清理脚本

### 数据库
- `sport_lottery.db` - SQLite数据库文件

### 文档
- `docs/USER_MANAGEMENT_GUIDE.md` - 详细使用指南
- `USER_MANAGEMENT_COMPLETION_REPORT.md` - 完成报告
- `QUICK_ACCESS.md` - 本文件

---

## 💡 使用提示

1. **首次使用**: 运行 `start_user_management.bat` 一键启动
2. **查看数据**: 使用提供的SQL命令查看模拟数据
3. **清理数据**: 使用cleanup命令清理所有模拟数据
4. **API测试**: 访问Swagger文档进行API测试
5. **前端调试**: 使用浏览器开发者工具查看网络请求

---

## 🔧 常见问题

### Q: 后端启动失败？
A: 检查端口8000是否被占用，或查看backend目录下的日志文件。

### Q: 前端无法访问后端API？
A: 确保后端服务已启动，并检查CORS配置。

### Q: 模拟数据无法加载？
A: 运行 `python scripts/simple_mock_users.py create` 重新生成数据。

### Q: 如何修改端口号？
A: 后端: 修改 `backend/config.py` 中的PORT配置
   前端: 修改 `frontend/vite.config.js` 中的server.port配置

---

## 📞 技术支持

如遇问题，请查看：
1. `docs/USER_MANAGEMENT_GUIDE.md` - 详细使用指南
2. `USER_MANAGEMENT_COMPLETION_REPORT.md` - 系统完成报告
3. 后端日志: `backend/app.log`
4. 前端控制台: 浏览器F12开发者工具

---

**最后更新**: 2026-01-20
