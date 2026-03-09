# 项目端口配置清单

本文档详细列出了竞彩足球扫盘系统中所有影响项目启动端口的配置设置。

## 1. 前端端口配置

### Vite 开发服务器端口
- **文件**: `frontend/vite.config.js`
- **端口**: `3000`
- **配置**:
  ```javascript
  server: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: false,
    strict: false,
    open: true,
  }
  ```

### 前端API代理配置
- **文件**: `frontend/vite.config.js`
- **代理目标端口**: `8000`
- **配置**:
  ```javascript
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // 后端FastAPI服务地址
      changeOrigin: true,
      secure: false,
    },
    '/ws': {  // WebSocket连接代理
      target: 'http://localhost:8000',
      changeOrigin: true,
      ws: true,
    },
  }
  ```

### 前端API配置
- **文件**: `frontend/src/api/config.js`
- **默认后端API地址**: `http://localhost:3000/api`
- **环境变量**: `VITE_API_BASE_URL`

### 测试配置端口
- **文件**: `frontend/cypress.config.js`
- **端口**: `3000`
- **配置**: `baseUrl: 'http://localhost:3000'`

- **文件**: `frontend/playwright.config.js`
- **端口**: `3000`
- **配置**: `baseURL: 'http://localhost:3000'`

## 2. 后端端口配置

### FastAPI服务端口
- **文件**: `backend/config.py`
- **端口**: `8000`
- **配置**:
  ```python
  PORT: int = 8000
  HOST: str = "0.0.0.0"
  ```

### 后端主服务文件
- **文件**: `backend/main_final.py`
- **端口**: `8000`
- **配置**:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
  ```

### 后端配置中的前端地址
- **文件**: `backend/config.py`
- **前端地址端口**: `3000`
- **配置**:
  ```python
  FRONTEND_BASE_URL: str = "http://localhost:3000"  // 设置为前端运行的端口
  ```

## 3. Docker配置端口

### Docker Compose配置
- **文件**: `docker-compose.yml`
- **Nginx端口**:
  - 端口 `80` 映射到主机端口 `80`
  - 端口 `443` 映射到主机端口 `443`
- **后端端口**:
  - 容器内端口 `8000` 映射到主机端口 `8000`
- **前端端口**:
  - 容器内端口 `3000` 映射到主机端口 `3000`
- **数据库端口**:
  - PostgreSQL: 容器端口 `5432` 映射到主机端口 `5432`
  - Redis: 容器端口 `6379` 映射到主机端口 `6379`

## 4. 关联服务端口

### 数据库服务端口
- **PostgreSQL**: `5432`
- **Redis**: `6379`

## 5. 环境变量配置

### 环境变量影响
- `VITE_API_BASE_URL`: 前端环境变量，影响前端API请求的目标地址，默认值为 `http://localhost:3000/api`
- `PORT`: 后端服务端口，可在环境变量中覆盖

## 6. 调试和测试端口

### 调试脚本中的端口
- **文件**: `EMERGENCY_FIX.py`
- **后端API端口**: `8000`
- **前端端口**: `3000`

---

这些是影响项目启动端口的所有配置。前后端服务分别运行在不同端口上，通过代理进行通信。在开发环境中，前端运行在 `3000` 端口，后端运行在 `8000` 端口。在Docker部署中，这些端口也会映射到主机的相同端口。