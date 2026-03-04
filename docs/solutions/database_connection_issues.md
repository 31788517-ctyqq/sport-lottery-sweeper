# AI_WORKING: coder1 @1769627946 - 创建数据库连接问题解决方案

# 数据库连接问题

## 症状描述
- `OperationalError: unable to open database file`
- `PermissionError: [Errno 13] Permission denied`
- 数据库查询返回空结果或异常
- 表不存在错误：`no such table: users`
- 数据库文件损坏或无法读取

## 根本原因
- 数据库文件路径配置错误
- 文件权限问题（只读、无写入权限）
- 数据库文件被其他进程锁定
- 数据库模式未初始化或已过时

## 解决方案

### 1. 检查数据库文件状态
```bash
# 检查数据库文件是否存在
dir backend\sport_lottery.db

# 检查文件大小（应为非零）
dir backend\sport_lottery.db | findstr "sport_lottery.db"

# 检查文件权限
icacls backend\sport_lottery.db
```

### 2. 修复文件权限
```bash
# 确保当前用户有读写权限
icacls backend\sport_lottery.db /grant:r "Users:(F)" /T

# 或使用简单方法：删除后重新创建
del backend\sport_lottery.db
```

### 3. 重新初始化数据库
```bash
# 运行初始化脚本
python backend/init_db.py

# 或使用快速初始化
python backend/init_admin_simple.py
```

### 4. 检查数据库连接配置
查看 `backend/config.py` 或 `backend/config_fixed.py`：
```python
# 正确的 SQLite 路径配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./sport_lottery.db"
# 或
SQLALCHEMY_DATABASE_URL = "sqlite:///backend/sport_lottery.db"
```

### 5. 验证数据库模式
```bash
# 使用 SQLite 命令行工具检查表结构
sqlite3 backend/sport_lottery.db ".tables"
sqlite3 backend/sport_lottery.db "SELECT * FROM users LIMIT 1;"
```

### 6. 处理数据库锁定
如果数据库被其他进程锁定：
```bash
# 查找锁定进程
handle.exe backend\sport_lottery.db

# 或使用 Process Explorer 工具查找文件句柄
# 然后结束相关进程
taskkill /F /IM python.exe
```

## 数据库文件位置
- **主数据库**: `backend/sport_lottery.db`
- **测试数据库**: `test.db`
- **备份数据库**: `data/` 目录下的 `.backup` 文件

## 预防措施
- 数据库文件应位于项目目录内，使用相对路径
- 定期备份重要数据
- 使用数据库迁移工具（Alembic）管理模式变更
- 开发环境与生产环境使用不同的数据库文件

## 相关文档
- [数据库架构评估](../../docs/DATABASE_ARCHITECTURE_EVALUATION.md)
- [数据库使用指南](../../docs/DATABASE_USAGE_GUIDE.md)
- [数据库管理流程报告](../../docs/DATABASE_MANAGEMENT_PROCESS_REPORT.md)

# AI_DONE: coder1 @1769627946