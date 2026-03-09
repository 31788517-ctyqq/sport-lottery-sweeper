# 爬虫管理API验证和前端集成指南

## 📋 验证步骤概览

### Phase 1: API连通性验证
### Phase 2: 前端模拟数据清理  
### Phase 3: 真实API集成
### Phase 4: 数据库连接

---

## Phase 1: API连通性验证

### 1.1 启动后端服务

**方法A: 使用现有修复版启动脚本**
```bash
# 在项目根目录执行
start_fixed_backend.bat
```

**方法B: 手动启动简化服务**
```bash
cd backend
python simple_main.py
```

**验证服务状态**
```bash
# 检查服务是否启动
curl http://localhost:8000/health/live

# 预期响应
{"status":"healthy","service":"sport-lottery-sweeper"}
```

### 1.2 API端点验证清单

使用以下端点进行测试（已实现的API）：

| 功能模块 | HTTP方法 | 端点 | 用途 |
|---------|---------|------|------|
| 数据源管理 | GET | `/api/admin/v1/sources` | 获取数据源列表 |
| 数据源管理 | POST | `/api/admin/v1/sources` | 创建数据源 |
| 数据源管理 | PUT | `/api/admin/v1/sources/{id}/status` | 更新状态 |
| 数据情报 | GET | `/api/admin/v1/intelligence/data` | 获取情报数据 |
| 数据情报 | GET | `/api/admin/v1/intelligence/stats` | 获取统计信息 |
| 爬虫配置 | GET | `/api/admin/v1/crawler-configs` | 获取配置列表 |
| 系统健康 | GET | `/api/admin/v1/system/health` | 健康检查 |

### 1.3 快速API测试脚本

创建 `quick_api_test.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_endpoint(name, method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    print(f"\n测试: {name}")
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=HEADERS, timeout=5)
        elif method == "POST":
            resp = requests.post(url, headers=HEADERS, json=data, timeout=5)
        
        print(f"  URL: {url}")
        print(f"  状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"  ✅ 成功: {result.get('message', 'OK')}")
            return True
        else:
            print(f"  ❌ 失败: {resp.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ 异常: {str(e)}")
        return False

# 执行测试
tests = [
    ("服务健康检查", "GET", "/health/live"),
    ("获取数据源列表", "GET", "/api/admin/v1/sources"),
    ("获取数据情报", "GET", "/api/admin/v1/intelligence/data"),
    ("获取统计信息", "GET", "/api/admin/v1/intelligence/stats"),
    ("系统健康检查", "GET", "/api/admin/v1/system/health"),
]

print("=== API连通性测试 ===")
for name, method, endpoint in tests:
    test_endpoint(name, method, endpoint)

print("\n=== 测试完成 ===")
```

运行测试：
```bash
python quick_api_test.py
```

---

## Phase 2: 前端模拟数据清理

### 2.1 识别模拟数据位置

**文件: `frontend/src/views/CrawlerSourceConfig.vue`**

找到以下模拟数据代码段（约第145-155行）：

```javascript
// 模拟数据
await new Promise(resolve => setTimeout(resolve, 500))
sources.value = [
  {
    id: '0001',
    name: '500赛事抓取器',
    category: 'football_sp_odds',
    createTime: '2024-01-15 10:30:00',
    status: 'active'
  }
]
```

### 2.2 替换为真实API调用

**修改前:**
```javascript
const loadSources = async () => {
  loading.value = true
  try {
    // 模拟数据 - 需要删除
    await new Promise(resolve => setTimeout(resolve, 500))
    sources.value = [/* 模拟数据 */]
  } catch (error) {
    ElMessage.error('加载数据源失败')
  } finally {
    loading.value = false
  }
}
```

**修改后:**
```javascript
import { getSources } from '@/api/crawlerConfig.js'  // 引入API

const loadSources = async () => {
  loading.value = true
  try {
    const response = await getSources()
    if (response.code === 200) {
      sources.value = response.data
    } else {
      ElMessage.error(response.message || '加载数据源失败')
    }
  } catch (error) {
    console.error('API调用失败:', error)
    ElMessage.error('网络错误或服务器无响应')
  } finally {
    loading.value = false
  }
}
```

### 2.3 需要清理模拟数据的其他位置

检查以下文件的模拟数据：

1. **`frontend/src/views/admin/CrawlerConfig.vue`** - 管理页面
2. **`frontend/src/views/admin/intelligence/CrawlerIntelligence.vue`** - 情报页面  
3. **`frontend/src/api/crawler.js`** - API封装层

**通用的模拟数据模式识别:**
```javascript
// 需要删除的模式
await new Promise(resolve => setTimeout(resolve, XXX))
XXX.value = [{...}]  // 硬编码的数据数组
return mockData      // 明确的模拟数据返回
```

---

## Phase 3: 真实API集成

### 3.1 API调用封装检查

**文件: `frontend/src/api/crawlerConfig.js`**

确认API路径与后端一致：

```javascript
export function getSources(params) {
  return request({
    url: '/api/admin/v1/sources',  // 确认路径正确
    method: 'get',
    params
  })
}

export function createSource(data) {
  return request({
    url: '/api/admin/v1/sources',
    method: 'post',
    data
  })
}
```

### 3.2 增强API错误处理

建议在API封装中添加统一错误处理：

```javascript
// 在 request.js 或 API封装中添加
import { ElMessage } from 'element-plus'

export function handleApiError(error) {
  console.error('API Error:', error)
  
  if (error.response) {
    const { status, data } = error.response
    switch (status) {
      case 401:
        ElMessage.error('认证失败，请重新登录')
        break
      case 403:
        ElMessage.error('权限不足')
        break
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 500:
        ElMessage.error('服务器内部错误')
        break
      default:
        ElMessage.error(data.message || `请求失败 (${status})`)
    }
  } else if (error.request) {
    ElMessage.error('网络连接失败，请检查网络')
  } else {
    ElMessage.error('请求配置错误')
  }
}
```

### 3.3 添加加载状态和用户反馈

```javascript
const loadSources = async () => {
  loading.value = true
  try {
    const response = await getSources(filterParams.value)
    if (response.code === 200) {
      sources.value = response.data
      ElMessage.success(`成功加载 ${response.data.length} 条数据源`)
    } else {
      ElMessage.error(response.message || '加载失败')
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    loading.value = false
  }
}
```

---

## Phase 4: 数据库连接配置

### 4.1 当前数据库配置

**环境配置文件优先级:**
1. `backend.env` - 开发环境变量
2. `.env` - 本地环境覆盖
3. `config.py` - 应用默认配置

### 4.2 数据库配置检查

**文件: `backend/config.py`**

当前配置：
```python
DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"  # 默认SQLite
# DATABASE_URL: str = "postgresql://user:pass@localhost/db"  # PostgreSQL
```

**切换到PostgreSQL（推荐用于生产）:**

1. 修改 `backend.env`:
```bash
DATABASE_URL=postgresql://soccer_user:soccer_pass@localhost:5432/soccer_db
```

2. 确保PostgreSQL服务运行
3. 创建数据库和用户

### 4.3 数据库初始化

```bash
# 进入backend目录
cd backend

# 初始化数据库表
python init_db.py

# 或使用Alembic迁移
alembic upgrade head

# 检查表结构
python check_db.py
```

### 4.4 测试数据库连接

创建测试脚本 `test_db_connection.py`:

```python
from database import engine, SessionLocal
from models.crawler_config import CrawlerConfig

def test_connection():
    try:
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ 数据库连接成功")
        
        # 测试表是否存在
        db = SessionLocal()
        count = db.query(CrawlerConfig).count()
        print(f"✅ 爬虫配置表存在，当前记录数: {count}")
        db.close()
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

if __name__ == "__main__":
    test_connection()
```

---

## 🔧 故障排除

### 常见问题及解决方案

**1. 端口8000被占用**
```bash
# 查找占用进程
netstat -ano | findstr :8000
# 终止进程
taskkill /f /pid <PID>
```

**2. CORS跨域问题**
- 检查 `main.py` 中的CORS配置
- 确保前端请求头包含正确的Origin

**3. API返回404**
- 确认后端服务已正确注册路由
- 检查API路径拼写

**4. 认证失败**
- 检查token获取逻辑
- 确认Authorization header格式：`Bearer <token>`

**5. 数据库连接失败**
- 检查数据库服务是否启动
- 验证连接字符串格式
- 确认用户权限

---

## ✅ 验证清单

完成以下步骤后打勾确认：

- [ ] 后端服务正常启动（http://localhost:8000）
- [ ] API连通性测试全部通过
- [ ] 前端模拟数据已清理
- [ ] 真实API调用正常工作
- [ ] 错误处理机制完善
- [ ] 数据库连接成功
- [ ] 数据表初始化完成
- [ ] 前端界面能正常显示真实数据

---

## 📞 下一步工作

完成API验证和前端集成后，可以继续：

1. **完善爬虫配置业务逻辑**
   - 实现配置版本管理
   - 添加配置验证规则
   - 支持配置模板功能

2. **增强监控和日志**
   - 添加API调用日志
   - 实现性能指标收集
   - 设置告警机制

3. **前端功能完善**
   - 添加数据可视化图表
   - 实现批量操作功能
   - 优化用户体验

4. **生产环境准备**
   - 配置HTTPS和安全策略
   - 性能优化和压力测试
   - 部署流程自动化
