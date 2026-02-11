# 体育彩票扫盘系统 - 项目结构备忘

## 🗂️ 核心目录结构

```
sport-lottery-sweeper/                 # 项目根目录
├── data/                              # 🗄️ 数据存储目录
│   └── sport_lottery.db               # SQLite 数据库文件（统一位置）
├── backend/                           # 🎯 后端服务目录（重要！）
│   ├── main.py                        # 主应用入口文件
│   ├── database_utils.py              # 数据库工具模块
│   ├── simple_main.py                 # 简化版后端服务
│   ├── main_working.py                # 工作版后端服务
│   ├── admin/                         # 管理后台模块
│   │   └── api/
│   │       └── v1/
│   │           └── router.py          # API v1 路由定义
│   └── ...
├── frontend/                          # 前端应用目录
├── docs/                              # 文档目录
└── ...
```

## 🔑 关键记忆点

### 数据库文件位置
- **路径**: `项目根目录/data/sport_lottery.db`
- **重要性**: ⭐⭐⭐⭐⭐ 所有数据库操作都应指向此位置
- **注意**: 项目根目录的旧数据库文件已删除，避免数据不一致

### 后端目录位置
- **路径**: `项目根目录/backend/`
- **完整路径**: `c:/Users/11581/Downloads/sport-lottery-sweeper/backend/`
- **重要性**: ⭐⭐⭐⭐⭐ 所有后端服务文件都在这里

### 主要后端文件
| 文件名 | 用途 | 重要程度 |
|--------|------|----------|
| `main.py` | 主应用入口，包含API路由 | ⭐⭐⭐⭐⭐ |
| `database_utils.py` | 数据库操作工具 | ⭐⭐⭐⭐ |
| `simple_main.py` | 简化版后端服务 | ⭐⭐⭐ |
| `main_working.py` | 工作版后端服务 | ⭐⭐⭐⭐ |

### 常用启动命令
```bash
# 进入后端目录
cd backend

# 启动主服务
python main.py

# 或使用 uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 环境变量
- `FULL_API_MODE=true` - 强制启用完整API模式
- 端口：8000（用户设定）

## 🚀 快速启动指南

1. **进入后端目录**: `cd backend`
2. **检查文件**: `dir *.py`
3. **启动服务**: `python main.py`
4. **验证服务**: 访问 `http://localhost:8000/docs`

---

**记忆口诀**: "后端在根目录的backend文件夹下" ✅

*创建时间: 2026-01-25*
*最后更新: 修复database_utils.py编码问题后*