# Scripts 目录使用指南

> 📋 **最新重构**: 2024年12月 - 已完成45个冗余脚本的清理归档
> 📖 **详细指南**: 请参考根目录的 `REFACTORED_SCRIPTS_GUIDE.md`

## 🚀 快速开始

### 后端服务
```bash
# 开发环境启动
python start_backend.py

# 生产环境部署
python deploy_helper.py production

# 快速测试启动
./quick-start.sh
```

### 数据库管理
```bash
# 数据库健康检查
python ../scripts/db/database_health_scan.py

# 检查表结构
python check_tables.py

# 验证数据内容
python check_db_content.py
```

### 管理员用户
```bash
# 初始化管理员和角色
python admin/init_admin_and_roles.py

# 创建新的管理员用户
python utils/create_proper_admin_user.py
```

### 数据爬取和导入
```bash
# 手动控制爬虫
python manual_crawler_control.py

# 导入500网数据
python import_500_data.py
```

### 前端服务
```bash
# Linux/Mac
./install-frontend-deps.sh
npm run dev

# Windows
install-frontend-deps.bat
npm run dev
```

## 📁 目录结构

```
scripts/
├── admin/              # 管理员用户管理
├── backup/             # 数据库备份脚本
├── batch/              # Windows批处理脚本
├── crawler/            # 数据爬取脚本
├── db/                 # 数据库管理脚本
├── deploy/             # 部署相关脚本
├── dev/                # 开发调试脚本
├── docker/             # Docker相关脚本
├── fixes/              # 问题修复脚本
├── health_check/       # 健康检查脚本
├── recovery/           # 数据恢复脚本
├── refactor/           # 重构工具脚本
├── seed/               # 数据种子脚本
├── ssl-certificates/   # SSL证书管理
├── utils/              # 通用工具脚本
└── archive/            # 🗃️ 已归档的冗余脚本（不纳入版本控制）
```

## ⚠️ 重要提醒

1. **归档脚本**: `scripts/archive/` 目录包含已废弃的冗余脚本，**不要直接使用**
2. **权限设置**: 部分脚本需要执行权限 (`chmod +x script.sh`)
3. **环境依赖**: 运行前请确保Python虚拟环境和Node.js依赖已正确安装
4. **配置文件**: 敏感配置请使用 `.env` 文件，不要硬编码在脚本中

## 🔧 常用脚本说明

| 脚本 | 用途 | 使用频率 |
|------|------|----------|
| `start_backend.py` | 后端服务启动 | 高频 |
| `deploy_helper.py` | 多环境部署 | 中频 |
| `manual_crawler_control.py` | 爬虫手动控制 | 中频 |
| `import_500_data.py` | 数据导入 | 低频 |
| `database-health_scan.py` | 数据库健康检查 | 中频 |

## 📞 获取帮助

- 📖 详细重构指南: `REFACTORED_SCRIPTS_GUIDE.md`
- 🐛 发现问题: 联系开发团队恢复归档脚本
- 💡 建议改进: 提交Issue或Pull Request

---
*最后更新: $(date)*