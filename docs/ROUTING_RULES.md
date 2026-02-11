# API路由管理规则

## 🚨 强制性规则

### 1. 路由前缀管理
- 所有前缀在 `backend/api/v1/__init__.py` 中统一定义
- 路由文件中使用 `router = APIRouter(prefix="", ...)`
- 禁止在路由文件中硬编码前缀

### 2. 修改路由后必须执行
- [ ] 运行 `python quick_route_check.py` 验证
- [ ] 重启后端服务 `taskkill /f /im python.exe && start python backend/main.py`
- [ ] 前端硬刷新 `Ctrl+F5`
- [ ] 检查浏览器控制台是否还有404

### 3. 路径命名规范
- 集合用复数: `/data-sources`
- 单项用单数+ID: `/data-source/{id}`
- 避免模糊路径: `/data`、`/list`、`/info`

### 4. 调试命令速查
```bash
# 检查路由
python quick_route_check.py

# 检查端口
netstat -ano | findstr :8000

# 重启后端
taskkill /f /im python.exe
start python backend/main.py

# 检查前端代理
# 查看 vite.config.js 中的 target 配置
```

## 🔍 常见问题排查

### Q: 修改路由后仍404？
A: 1. 检查后端是否重启 2. 检查前端是否硬刷新 3. 运行路由检查脚本

### Q: 路由冲突怎么办？
A: 使用 `prefix` 隔离不同模块的路由

### Q: 如何避免重复造轮子？
A: 修改前先搜索现有路由 `grep -r "data-source" backend/api/`