# 生产环境部署指南

本文档介绍了如何部署Sport Lottery Sweeper System到生产环境。

## 1. 环境要求

### 服务器要求
- Linux服务器 (推荐Ubuntu 20.04+ 或 CentOS 8+)
- 至少4GB内存
- 至少20GB磁盘空间
- Docker 20.10+
- Docker Compose v2+

### 安全要求
- 防火墙已配置
- SSH访问已设置
- SSL证书已准备（可选，但推荐）

## 2. 准备工作

### 2.1 克隆代码仓库
```bash
git clone https://your-git-repo-url.git
cd sport-lottery-sweeper
```

### 2.2 生成安全密钥
```bash
# 生成至少32位的随机字符串作为SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.3 配置生产环境变量
```bash
cp .env.production .env
# 编辑 .env 文件，设置正确的值
vim .env
```

## 3. 配置说明

### 3.1 关键配置项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `SECRET_KEY` | JWT加密密钥，至少32位随机字符 | `your-very-long-random-string-here` |
| `DATABASE_URL` | 生产数据库连接字符串 | `postgresql://user:pass@localhost:5432/dbname` |
| `DB_USER` | 数据库用户名 | `prod_user` |
| `DB_PASSWORD` | 数据库密码 | `secure_password` |
| `REDIS_PASSWORD` | Redis密码 | `redis_secure_password` |
| `FRONTEND_BASE_URL` | 前端访问域名 | `https://yourdomain.com` |

### 3.2 数据库配置

#### 3.2.1 生产环境配置
生产环境推荐使用PostgreSQL：

```bash
# .env文件中的数据库配置
DATABASE_URL=postgresql://username:password@postgres:5432/sport_lottery_db
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@postgres:5432/sport_lottery_db
```

#### 3.2.2 开发环境数据库文件位置规范
开发环境使用SQLite数据库，数据库文件管理遵循以下规范：

1. **主数据库文件位置**：
   - 数据库文件应位于项目根目录，文件名为 `sport_lottery.db`
   - 这是项目的唯一权威数据库文件，所有数据操作都应基于此文件

2. **硬链接使用规范**：
   - 为保持向后兼容性，可在 `backend/` 和 `data/` 目录下创建硬链接指向根目录的数据库文件
   - 硬链接确保多个路径指向同一物理文件，避免数据不一致
   - 创建硬链接命令（Windows）：`mklink /H "backend\sport_lottery.db" "sport_lottery.db"`

3. **代码引用规范**：
   - 所有数据库访问应通过 `backend.database.DATABASE_PATH` 配置
   - 禁止在代码中硬编码数据库路径（如 `"backend/sport_lottery.db"`）
   - 现有脚本应逐步迁移到使用统一配置

4. **健康检查**：
   - 定期运行 `check_database_paths.py` 验证所有数据库访问路径是否一致
   - 检查硬链接状态，确保没有创建冗余的数据库副本

## 4. 部署步骤

### 4.1 使用部署脚本（推荐）

```bash
# 设置环境变量
export SECRET_KEY="your-generated-secret-key"
export DB_PASSWORD="your-db-password"
export REDIS_PASSWORD="your-redis-password"

# 运行部署脚本
chmod +x deploy_production.sh
./deploy_production.sh
```

### 4.2 手动部署

```bash
# 构建并启动服务
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# 检查服务状态
docker-compose -f docker-compose.production.yml ps
```

## 5. 验证部署

### 5.1 检查服务状态
```bash
docker-compose -f docker-compose.production.yml ps
```

### 5.2 查看日志
```bash
# 查看后端日志
docker-compose -f docker-compose.production.yml logs backend

# 查看数据库日志
docker-compose -f docker-compose.production.yml logs postgres
```

### 5.3 访问应用
打开浏览器访问 `http://your-server-ip`

## 6. 维护操作

### 6.1 更新应用
```bash
# 停止当前服务
docker-compose -f docker-compose.production.yml down

# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

### 6.2 备份数据
```bash
# 备份PostgreSQL数据库
docker-compose -f docker-compose.production.yml exec postgres pg_dump -U your_username your_db_name > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份Redis数据
docker-compose -f docker-compose.production.yml exec redis redis-cli BGSAVE
```

### 6.3 监控资源
```bash
# 查看容器资源使用情况
docker stats

# 查看系统日志
docker-compose -f docker-compose.production.yml logs --tail=100 -f
```

## 7. 故障排查

### 7.1 常见问题

1. **服务无法启动**
   - 检查端口是否被占用
   - 检查环境变量是否正确设置
   - 查看详细日志信息

2. **数据库连接失败**
   - 检查数据库服务是否运行
   - 检查数据库连接字符串是否正确
   - 检查数据库用户权限

3. **Redis连接失败**
   - 检查Redis服务是否运行
   - 检查Redis密码是否正确

### 7.2 日志文件位置

- Nginx日志: `./logs/nginx/`
- 后端日志: `./logs/backend/`
- 爬虫日志: `./logs/crawler/`

## 8. 安全注意事项

1. **密钥管理**
   - 定期更换SECRET_KEY
   - 不要在代码中硬编码敏感信息
   - 使用环境变量或密钥管理服务

2. **访问控制**
   - 配置防火墙只开放必要端口
   - 使用SSL/TLS加密传输
   - 定期更新系统和软件包

3. **监控和审计**
   - 监控系统日志
   - 定期检查安全漏洞
   - 实施入侵检测

## 9. 性能调优

1. **数据库优化**
   - 为常用查询字段添加索引
   - 定期清理过期数据
   - 调整连接池大小

2. **应用优化**
   - 调整worker数量以匹配CPU核心数
   - 启用Gzip压缩
   - 配置CDN加速静态资源

3. **系统优化**
   - 调整内核参数
   - 配置负载均衡
   - 实施缓存策略

## 10. 支持

如果遇到问题，请参考：

- [官方文档](link-to-docs)
- [常见问题解答](link-to-faq)
- [技术支持](contact-info)