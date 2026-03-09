# AI_WORKING: coder1 @1769627946 - 创建API路由错误解决方案

# API路由错误

## 症状描述
- 访问 API 端点返回 `404 Not Found`
- FastAPI 文档 (`/docs`) 中缺少预期的路由
- 导入模块时出现 `ModuleNotFoundError` 或 `ImportError`
- 路由注册成功但无法访问

## 根本原因
- 路由模块未正确导入到主应用
- 导入路径错误（相对导入 vs 绝对导入）
- 循环导入依赖
- 文件语法错误导致模块无法加载

## 解决方案

### 1. 检查路由注册状态
```bash
# 查看当前注册的所有路由
python -c "from backend.main import app; [print(route.path, route.methods) for route in app.routes]"
```

### 2. 验证模块导入
```bash
# 测试关键模块能否正常导入
python -c "from backend.config import settings; print('Config OK')"
python -c "from backend.database import engine; print('Database OK')"
python -c "from backend.api import router; print('API router OK')"
python -c "from backend.main import app; print('App OK')"
```

### 3. 检查导入路径
**常见错误**：
```python
# ❌ 错误：相对导入超出范围
from ..database import get_db  # 可能超出顶级包

# ✅ 正确：使用绝对导入
from backend.database_utils import get_db
```

**修复步骤**：
1. 检查 `backend/api/v1/__init__.py` 中的路由导入
2. 确保 `backend/api/__init__.py` 正确导出路由
3. 验证 `backend/main.py` 中的 `app.include_router` 调用

### 4. 修复循环导入
**症状**：`ImportError: cannot import name 'xxx' from partially initialized module`

**解决方案**：
1. 将共享依赖移到单独模块
2. 使用局部导入（在函数内部导入）
3. 重构代码结构，消除循环依赖

### 5. 检查文件语法
```bash
# 使用 Python 语法检查
python -m py_compile backend/api/v1/users.py

# 如果有语法错误，会显示具体行号
```

### 6. 重新启动服务
```bash
# 完全停止后重新启动
taskkill /F /IM python.exe
timeout /t 3
python -m uvicorn backend.main:app --port 8000 --reload
```

## 标准路由结构
```
backend/
├── api/
│   ├── __init__.py          # 导出 api_router
│   └── v1/
│       ├── __init__.py      # 导入所有 v1 路由
│       ├── users.py         # 用户相关路由
│       ├── crawler.py       # 爬虫管理路由
│       └── ...
└── main.py                  # 注册 api_router
```

## 预防措施
- 遵循项目导入规范（使用绝对导入 `backend.xxx`）
- 避免循环导入，使用依赖注入
- 新路由完成后立即验证是否出现在 `/docs`
- 编写路由单元测试

## 相关文档
- [路由规则](../../ROUTING_RULES.md)
- [后端 API 文档](../../docs/backend/API_DOCUMENTATION.md)
- [爬虫管理 API 完善总结](../../爬虫管理API完善总结.md)

# AI_DONE: coder1 @1769627946