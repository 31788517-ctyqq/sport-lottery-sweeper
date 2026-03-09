# 配置管理规范

## 📋 配置文件架构

项目采用**分层配置管理**策略，确保环境隔离和配置一致性：

```
项目根目录/
├── .env                     # 主配置文件（开发环境默认值）
├── .env.example             # 配置模板（不含敏感信息）
├── .env.production          # 生产环境配置
├── .env.staging             # 预发布环境配置（预留）
├── backend/.env             # 软链接→../.env（保持兼容性）
├── frontend/
│   ├── .env.development    # 前端开发环境
│   └── .env.production     # 前端生产环境
└── docker/.env              # Docker专用配置
```

## 🎯 配置分类

### 1. **通用配置** (所有环境共享)
- `APP_NAME`, `VERSION` - 应用基本信息
- `API_V1_PREFIX` - API路径前缀
- 功能开关配置

### 2. **环境特定配置** (按环境分离)
- **开发环境**: `.env`, `frontend/.env.development`
- **生产环境**: `.env.production`, `frontend/.env.production`
- **Docker环境**: `docker/.env`

### 3. **敏感配置** (永不提交到版本控制)
- `SECRET_KEY` - JWT密钥
- API密钥 (OpenAI, Gemini, Qwen等)
- 数据库密码
- 邮箱密码

## 🔧 使用指南

### 开发环境设置
```bash
# 1. 复制配置模板（首次设置）
cp .env.example .env

# 2. 编辑 .env 文件，填入实际配置值
# 特别注意：修改 SECRET_KEY 和其他敏感配置

# 3. 启动服务
python backend/start_server.py
```

### 生产环境部署
```bash
# 1. 创建生产环境配置
cp .env.production .env

# 2. 设置生产环境密钥（通过环境变量或安全配置管理）
export SECRET_KEY="your-production-secret-key"

# 3. 或使用Docker Compose
cd docker
cp .env .env.local  # 创建本地覆盖配置
docker-compose up -d
```

### 前端环境切换
```bash
# 开发环境 (默认)
npm run dev

# 生产环境构建
npm run build

# Docker构建
cd frontend
docker build -t sport-lottery-frontend .
```

## ⚙️ 配置加载顺序

1. **环境变量** (最高优先级)
2. **.env.local** (本地覆盖，不提交Git)
3. **环境特定配置** (.env.production, frontend/.env.production等)
4. **主配置文件** (.env)
5. **默认值** (代码中硬编码)

## 🔒 安全规范

### 必须加密的配置
- `SECRET_KEY` - 至少32位随机字符串
- 所有第三方API密钥
- 数据库密码
- JWT相关密钥

### 生产环境检查清单
- [ ] 所有敏感配置已通过环境变量设置
- [ ] `DEBUG=false`
- [ ] CORS限制为实际域名
- [ ] 日志级别设置为WARNING或更高
- [ ] 功能开关优化（关闭不必要功能）
- [ ] 登录失败锁定已启用

## 🚨 故障排除

### 常见问题

**Q: 配置不生效？**
A: 检查环境变量优先级，确保没有冲突的配置源

**Q: Docker中数据库连接失败？**
A: 检查 `docker/.env` 中的网络配置，使用 `host.docker.internal` 访问宿主机服务

**Q: 前端API请求404？**
A: 确认 `VITE_API_BASE_URL` 配置正确，开发环境应为空以启用代理

### 配置验证
```bash
# 验证配置文件语法
python -c "from dotenv import load_dotenv; load_dotenv(); print('Config OK')"

# 检查必需配置项
python scripts/validate_config.py
```

## 📝 维护指南

### 添加新配置项
1. 在 `.env.example` 中添加模板项
2. 在适当的环境配置文件中设置默认值
3. 在代码中添加配置验证逻辑
4. 更新本文档

### 配置变更流程
1. 更新配置模板 (.env.example)
2. 在开发环境测试
3. 更新生产环境配置
4. 部署并验证

---

**最后更新**: 2025-02-12  
**维护者**: AI Coding Assistant