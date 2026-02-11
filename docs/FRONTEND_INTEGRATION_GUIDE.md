# 前端对接指南

## 🎯 概述
后端服务已成功启动并运行在 `http://localhost:8000`，所有核心接口测试通过。本文档指导前端如何对接后端API。

## 📋 环境信息

### 后端服务
- **地址**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs`
- **状态**: ✅ 运行中

### 前端开发服务器
- **地址**: `http://localhost:3000` (根据项目配置)
- **代理**: 建议配置代理避免CORS问题

## 🔗 快速开始

### 1. 安装依赖
```bash
cd frontend
npm install axios  # 如果尚未安装
```

### 2. 配置代理 (推荐)
在 `vite.config.js` 或 `vue.config.js` 中添加代理：

```javascript
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
}
```

### 3. 使用API配置
已创建 `frontend/src/api/config.js` 和 `frontend/src/api/example.js`

## 📡 可用接口列表

### 健康检查接口
| 接口 | 方法 | 地址 | 状态 |
|------|------|------|------|
| 服务存活检查 | GET | `/health/live` | ✅ 正常 |
| 就绪检查 | GET | `/health/ready` | ✅ 正常 |
| API状态检查 | GET | `/api/v1/health` | ✅ 正常 |

### 用户认证接口
| 接口 | 方法 | 地址 | 说明 |
|------|------|------|------|
| 用户登录(v1) | POST | `/api/v1/auth/login` | 推荐使用 |
| 用户注册(v1) | POST | `/api/v1/auth/register` | 用户注册 |
| 获取用户信息 | GET | `/api/v1/auth/me` | 需要认证 |
| 兼容登录 | POST | `/api/auth/login` | 兼容旧前端 |
| 用户信息兼容 | GET | `/api/auth/profile` | 兼容旧前端 |

### 业务接口
| 接口 | 方法 | 地址 | 说明 |
|------|------|------|------|
| 仪表板统计 | GET | `/api/dashboard/summary` | 统计数据 |
| 情报筛查列表 | GET | `/api/intelligence/screening/list` | 情报数据 |

## 💻 使用示例

### Vue 3 Composition API 示例
```vue
<template>
  <div>
    <button @click="checkHealth">检查服务状态</button>
    <button @click="handleLogin">登录</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { checkServiceHealth, loginUser, getDashboardStats } from '@/api/example.js'

const healthStatus = ref(null)
const dashboardData = ref(null)

// 检查服务状态
const checkHealth = async () => {
  try {
    healthStatus.value = await checkServiceHealth()
    console.log('服务状态:', healthStatus.value)
  } catch (error) {
    console.error('健康检查失败:', error.message)
  }
}

// 用户登录
const handleLogin = async () => {
  try {
    const result = await loginUser('admin@example.com', 'password')
    console.log('登录成功:', result)
    
    // 登录成功后获取仪表板数据
    dashboardData.value = await getDashboardStats()
    console.log('仪表板数据:', dashboardData.value)
  } catch (error) {
    console.error('登录失败:', error.message)
  }
}

// 组件挂载时检查服务
setTimeout(checkHealth, 1000)
</script>
```

### 错误处理示例
```javascript
import { loginUser } from '@/api/example.js'

try {
  const result = await loginUser(email, password)
  if (result.code === 200) {
    // 登录成功处理
    console.log('登录成功:', result.data)
  } else {
    // 业务逻辑错误
    console.error('登录失败:', result.message)
  }
} catch (error) {
  // 网络错误或服务器错误
  console.error('请求失败:', error.message)
  // 显示错误提示给用户
  alert(error.message)
}
```

## ⚠️ 注意事项

### 1. 跨域问题
- **开发环境**: 配置代理或使用 `withCredentials: true`
- **生产环境**: 确保前后端域名同源或配置CORS

### 2. 认证机制
- 当前使用JWT Token认证（演示模式）
- 实际项目中需要在请求头添加 `Authorization: Bearer <token>`

### 3. 数据格式
- 请求数据: JSON格式
- 响应格式: `{code: 200, message: "success", data: {...}}`
- 错误格式: `{detail: "错误信息"}` 或 HTTP状态码

### 4. 环境变量
根据需要修改 `frontend/src/api/config.js` 中的配置：
- 开发环境: `http://localhost:8000`
- 生产环境: 你的生产域名

## 🔧 故障排除

### 常见问题
1. **连接拒绝**
   - 检查后端服务是否启动
   - 确认端口8000未被占用

2. **CORS错误**
   - 配置代理或后端CORS设置
   - 检查 `withCredentials` 配置

3. **404错误**
   - 确认接口地址正确
   - 检查API前缀 `/api`

4. **认证失败**
   - 当前为演示模式，使用正确的测试数据
   - 实际使用时需要实现真实用户认证

## 📞 技术支持

如果遇到问题：
1. 检查浏览器开发者工具的Network标签
2. 查看后端服务控制台日志
3. 参考后端API文档: `http://localhost:8000/docs`

---
**最后更新**: 2026-01-25  
**后端状态**: ✅ 运行中  
**测试状态**: ✅ 所有接口测试通过