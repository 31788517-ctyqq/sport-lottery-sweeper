# Backend 工具集

## issue_fixer.py - 统一问题修复工具

### 概述
此工具整合了项目中所有重复的修复脚本，提供统一的命令行接口。它取代了以下分散的修复脚本：

### 已整合的修复脚本
| 旧脚本 | 功能 | 新命令 |
|--------|------|--------|
| `fix_relative_imports.py` | 修复相对导入 (`from ...`) | `import-paths` |
| `fix_double_dot_imports.py` | 修复双点导入 (`backend..`) | `import-paths` |
| `fix_encoding_and_imports.py` | 检测并修复文件编码 | `encoding` |
| `scripts/fixes/fix_admin_login.py` | 修复管理员登录 | `admin-login` |
| `scripts/fixes/fix_admin_login_issue.py` | 修复管理员登录问题 | `admin-login` |
| `scripts/fixes/fix_admin_password.py` | 修复管理员密码 | `admin-login` |
| `scripts/fixes/fix_admin_datetime.py` | 修复datetime字段 | `db-fields` |
| `scripts/fixes/fix_all_admin_issues.py` | 修复所有管理员问题 | `admin-login` + `db-fields` |
| `fix_admin_routes.py` | 修复管理员路由 | (部分功能整合) |
| `fix_db_structure.py` | 修复数据库结构 | (检查功能) |

### 使用方式
```bash
# 查看帮助
python issue_fixer.py help

# 修复导入路径问题
python issue_fixer.py import-paths

# 检测并修复文件编码
python issue_fixer.py encoding

# 修复管理员登录
python issue_fixer.py admin-login

# 修复数据库字段（datetime, notification_preferences）
python issue_fixer.py db-fields

# 检查目录结构
python issue_fixer.py check-dirs

# 执行所有修复
python issue_fixer.py all
```

### 依赖安装
```bash
# 如果需要编码检测功能
pip install chardet

# 如果需要密码哈希功能
pip install bcrypt
```

### 设计原则
1. **模块化**：每个功能独立，可单独调用
2. **安全**：修改前备份，提供详细日志
3. **可扩展**：易于添加新的修复功能
4. **文档化**：清晰的帮助信息和错误提示

### 添加新功能
要添加新的修复功能：
1. 在 `issue_fixer.py` 中添加新的函数
2. 在 `main()` 函数中添加命令选项
3. 更新帮助文档

### 注意事项
- 运行修复前建议备份重要文件
- 管理员登录修复需要数据库访问权限
- 编码修复需要 chardet 模块支持
- 部分功能可能需要管理员权限

### 版本历史
- v1.0.0 (2026-01-29): 初始版本，整合10+个重复修复脚本