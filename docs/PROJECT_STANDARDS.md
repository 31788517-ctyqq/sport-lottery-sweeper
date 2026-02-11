# 体育彩票扫盘系统 - 开发规范标准

> **最新更新**: 2026-01-25 | **版本**: 2.0.0 | **AI协同增强版**

## 🎯 核心目标
建立统一的开发规范，让AI和开发者都能快速理解项目结构，避免路径、启动文件、路由等基础问题打断开发流程。**特别强化AI协同开发机制**。

## 📁 项目结构规范

### 后端结构 (backend/)
```
backend/
├── main.py                 # 🚀 唯一启动文件
├── config.py              # 配置文件
├── database_utils.py      # 数据库工具
├── api/
│   └── v1/
│       ├── __init__.py    # API路由注册入口
│       ├── admin/         # 管理端API
│       ├── auth.py        # 认证API
│       └── crawler/       # 爬虫API
├── models/               # 数据模型
├── crud/                 # 数据库操作
└── core/                 # 核心业务逻辑
```

### 前端结构 (frontend/)
```
frontend/
├── src/
│   ├── router/
│   │   └── index.js       # 🚀 唯一路由配置文件
│   ├── views/
│   │   ├── Login.vue      # 登录页
│   │   └── admin/         # 管理端页面
│   │       ├── Layout.vue # 布局组件
│   │       ├── Dashboard.vue
│   │       └── ...其他管理页面
│   └── api/               # API调用封装
├── public/               # 静态资源
└── package.json
```

### AI协同结构 (.codebuddy/)
```
.codebuddy/
├── plugin_identities.json     # 🤖 AI插件身份注册
├── coordination.md           # 协同协议文档
├── quick-start.md            # AI快速入门
├── locks/                   # 文件锁目录
│   ├── check_lock.py        # 锁检查脚本
│   └── *.lock               # 活跃锁文件
├── status/                  # 状态文件
│   ├── active_plugins.json  # 活跃插件状态
│   └── scan_results.json    # 扫描结果缓存
└── compliance_reports/      # 合规检查报告
    └── *.json               # 历史合规报告
```

## 🚀 启动文件规范

### 后端启动
- **唯一入口**: `backend/main.py`
- **启动命令**: 
  ```bash
  cd backend
  python main.py
  # 或使用提供的脚本
  start_backend.bat
  npm run backend:dev
  ```
- **端口**: 8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health/live

### 前端启动
- **开发服务器**: 端口3000
- **API代理**: 自动转发到后端8000端口
- **启动命令**:
  ```bash
  cd frontend
  npm run dev
  # 或使用提供的脚本
  start-frontend.bat
  npm run frontend:dev
  ```

### 智能启动（推荐）
```bash
# 一键启动所有服务
npm run smart-start

# 或使用Python脚本
python scripts/smart_start.py

# PowerShell一键启动
start-dev.ps1
```

## 🛣️ 路由映射规范

### 后端API路由
| 前端路径 | 后端API路径 | 功能 |
|---------|------------|------|
| `/api/auth/login` | `/api/v1/auth/login` | 用户登录 |
| `/api/dashboard/summary` | `/api/v1/admin/dashboard/stats` | 仪表板数据 |
| `/admin/users` | `/api/v1/admin/users/*` | 用户管理 |
| `/admin/crawler` | `/api/v1/admin/crawler/*` | 爬虫管理 |
| `/admin/sp` | `/api/v1/admin/sp/*` | SP管理 |

### 前端路由映射
| URL路径 | 组件 | 权限 |
|---------|------|------|
| `/` | Login | 公开 |
| `/login` | Login | 公开 |
| `/admin/dashboard` | Dashboard | admin, manager |
| `/admin/users/*` | UserManagement | admin |
| `/admin/crawler/*` | CrawlerManagement | admin, manager |

## 🔧 环境变量规范

### 后端环境变量 (backend/.env)
```env
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key
DEBUG=true
PORT=8000
```

### 前端环境变量 (frontend/.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=体育彩票扫盘系统
```

## 🤖 AI协同开发规范

### 多AI插件身份
- **coder1**: 主要代码编写AI (Claude) - 优先级1
- **coder2**: 辅助代码编写AI (GitHub Copilot) - 优先级2  
- **tester1**: 测试AI (Tabnine) - 优先级3
- **reviewer1**: 代码审查AI (SonarQube) - 优先级4
- **analyzer1**: 分析AI (CodeGecko) - 优先级5

### 文件修改流程
1. **检查锁状态**: `python .codebuddy/locks/check_lock.py check 文件名 AI标识`
2. **创建文件锁**: `python .codebuddy/locks/check_lock.py create 文件名 AI标识`
3. **修改代码**: 添加AI_WORKING标记
4. **释放锁**: 完成后自动释放或手动释放

### 代码注释规范
```python
# AI_WORKING: [AI标识] @[时间戳] - 具体修改说明
# [修改的代码]
# AI_DONE: [AI标识] @[时间戳]
```

### 冲突解决策略
1. **时间戳优先**: 先获取锁的AI获得优先权
2. **优先级次之**: 同时间时按priority数值决定
3. **用户仲裁**: 无法解决时标记需要人工介入

### 原子操作限制
- 单文件最大连续修改: 3处
- 同文件最小修改间隔: 5秒
- 复杂任务必须分解
- 5次操作后需确认

## 🔍 路径别名规范

### 前端路径别名 (@ 别名系统)
```javascript
resolve: {
  alias: {
    '@': path.resolve(__dirname, 'src'),
    '@/components': path.resolve(__dirname, 'src/components'),
    '@/views': path.resolve(__dirname, 'src/views'),
    '@/api': path.resolve(__dirname, 'src/api'),
    '@/utils': path.resolve(__dirname, 'src/utils'),
    '@/styles': path.resolve(__dirname, 'src/styles'),
    '@/layout': path.resolve(__dirname, 'src/layout'),
    '@/router': path.resolve(__dirname, 'src/router'),
    '@/stores': path.resolve(__dirname, 'src/stores'),
    '@/config': path.resolve(__dirname, 'src/config'),
  }
}
```

### 后端导入规范
```python
# ✅ 正确 - 使用绝对导入
from backend.api.v1.auth import router as auth_router
from backend.models.user import User
from backend.database_utils import get_db
from backend.core.security import create_access_token

# ❌ 错误 - 使用相对导入
from ..api.v1.auth import router
from .user import User
from database_utils import get_db
```

## 📝 开发工作流规范

### 1. 启动检查清单
- [ ] 后端服务运行在8000端口
- [ ] 前端服务运行在3000端口  
- [ ] API文档可访问: http://localhost:8000/docs
- [ ] 前端可正常访问登录页
- [ ] AI协同锁系统正常
- [ ] 所有必需文件存在

### 2. 文件修改规范
- 修改任何文件前必须检查文件锁状态
- Python/JS文件必须使用UTF-8编码
- 遵循项目的导入路径规范（使用绝对路径别名）
- AI修改必须添加规范注释标记

### 3. API调用规范
- 前端API调用统一走`/api`前缀
- 后端API统一在`/api/v1`路径下
- 认证使用JWT令牌
- WebSocket连接代理到后端8000端口

### 4. 健康检查命令
```bash
# 全面健康检查
npm run health
python scripts/project_health_check.py

# AI合规检查
npm run compliance
python scripts/check_ai_compliance.py

# 项目配置扫描
npm run scan
python scripts/config_scanner.py

# 智能启动
npm run smart-start
python scripts/smart_start.py
```

## 🔍 快速诊断命令

### 检查后端状态
```bash
# 检查端口占用
netstat -ano | findstr :8000

# 测试API连通性
curl http://localhost:8000/health/live

# 查看API文档
start http://localhost:8000/docs
```

### 检查前端状态
```bash
# 检查端口占用
netstat -ano | findstr :3000

# 检查路由配置
cat frontend/src/router/index.js
```

### AI协同诊断
```bash
# 检查活跃锁
ls -la .codebuddy/locks/

# 检查插件状态
cat .codebuddy/status/active_plugins.json

# 检查合规分数
npm run compliance
```

## ⚠️ 常见问题解决

### 问题1: 文件路径错误
**解决**: 始终使用绝对路径，参考项目结构规范

### 问题2: 路由404
**解决**: 
1. 检查后端`main.py`是否注册了对应路由
2. 检查前端`router/index.js`路径配置
3. 确认API前缀匹配（/api/v1 vs /api）

### 问题3: 启动失败
**解决**:
1. 确认使用正确的启动文件（`backend/main.py`）
2. 检查端口是否被占用
3. 查看日志文件排查错误
4. 使用`npm run smart-start`智能启动

### 问题4: AI理解困难
**解决**: 
1. 所有AI必须严格遵循本规范
2. 修改文件前必须检查锁状态
3. 添加清晰的代码注释标记
4. 运行`npm run compliance`检查合规性

### 问题5: 文件锁冲突
**解决**:
1. 检查`.codebuddy/locks/`目录
2. 等待锁自动过期或手动清理
3. 遵循时间戳优先原则
4. 必要时联系用户仲裁

## 🤖 AI协作最佳实践

### 协作原则
1. **原子性**: 每次修改应该是独立的、完整的变更
2. **可追溯**: 所有修改必须有清晰的注释和标记
3. **非阻塞**: 避免长期持有文件锁
4. **透明性**: 及时通知其他AI和开发者状态变化

### 沟通协议
```json
{
  "event": "lock_acquired|work_completed|conflict_detected",
  "ai_id": "coder1",
  "file": "backend/main.py",
  "timestamp": "2026-01-25T00:00:00Z",
  "description": "具体描述"
}
```

### 监控指标
- 操作成功率 > 95%
- 平均操作时间 < 30秒
- 冲突解决时间 < 5分钟
- 合规分数 > 85分

## 📚 重要文档索引

- **启动指南**: `STARTUP_GUIDE.md` - 快速启动和故障排除
- **路径别名**: `PATH_ALIASES.md` - 路径引用规范
- **API文档**: http://localhost:8000/docs - 在线接口文档
- **前端集成**: `FRONTEND_INTEGRATION_GUIDE.md` - 前端开发指南
- **项目结构**: `PROJECT_STRUCTURE.md` - 详细结构说明
- **API验证**: `API_VERIFICATION_GUIDE.md` - API测试方法
- **AI协同**: `.codebuddy/coordination.md` - AI协作协议详情

## 🎯 黄金法则

1. **规范至上**: 宁可多花时间遵循规范，也不要图方便破坏协作
2. **沟通透明**: AI之间要及时沟通状态，避免信息不对称
3. **原子操作**: 小步快跑，每次只做一个明确的修改
4. **文档先行**: 不确定时先查阅文档，不盲目猜测
5. **健康第一**: 定期运行健康检查，保持项目良好状态

---
**记住**: 本规范是所有开发和AI协作的基础，必须严格遵守！

**紧急联系**: 如遇无法解决的冲突或问题，立即停止操作并通知用户。