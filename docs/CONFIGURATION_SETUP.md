# 项目配置与启动说明

## 项目架构概览

本项目采用前后端分离架构：

- **后端**: FastAPI 应用，运行在 8000/8001 端口
- **前端**: Vue.js 应用，运行在 3000 端口
- **SonarQube**: 代码质量检测，运行在 9000 端口

## 端口分配

- `8000`: 后端API服务（备用）
- `8001`: 后端API服务（推荐）
- `3000`: 前端开发服务器
- `9000`: SonarQube服务器

## 环境配置

### 后端服务启动

```bash
# 推荐使用8001端口，避免与可能存在的其他服务冲突
cd sport-lottery-sweeper
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

### 前端配置

项目已配置适当的代理规则，将 `/api`、`/ws` 和 `/admin` 请求代理到后端服务。

当前端运行在3000端口时：
- `/api` 请求将被代理到 `http://localhost:8001`
- `/ws` WebSocket 请求将被代理到 `http://localhost:8001`
- `/admin` 请求将被代理到 `http://localhost:8001`

### 环境变量配置

前端环境配置文件 `.env.development.local` 已配置为连接到8001端口：

```
VITE_API_BASE_URL=http://localhost:8001
```

## SonarQube配置

### 本地扫描配置

项目根目录下的 `sonar-project.properties` 文件包含SonarQube扫描所需的配置：

```properties
sonar.host.url=http://localhost:9000
sonar.projectKey=sport-lottery-sweeper
sonar.sources=backend,frontend/src
```

### GitHub Actions配置

`.github/workflows/sonarqube.yml` 文件配置了CI/CD中的SonarQube扫描：

- 需要在仓库的Secrets中设置 `SONAR_TOKEN` 和 `SONAR_HOST_URL`
- 扫描包含后端(Python)和前端(Javascript/Vue)代码

## 常见问题解决

### WebSocket连接问题

如果遇到类似 `http://http//localhost:3000/admin/logs` 的错误：

1. 检查 `vite.config.js` 中的代理配置是否包含 `ws: true` 选项
2. 确保 `/admin` 路径的请求也被正确代理到后端
3. 验证前端和后端服务端口配置一致

### 端口占用问题

如果8000端口被占用，使用8001端口启动后端服务，并相应更新前端配置。

### SonarQube扫描失败

如果遇到 `Failed to query server version: URI with undefined scheme` 错误：

1. 确保 `sonar.host.url` 配置正确
2. 确保SonarQube服务器正在运行
3. 检查 `sonar-project.properties` 文件中的配置项是否完整

## 启动顺序

1. 启动SonarQube服务（如果需要代码扫描）
2. 启动后端服务（8001端口）
3. 启动前端开发服务器（3000端口，自动代理到后端）