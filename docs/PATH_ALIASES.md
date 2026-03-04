# 路径别名映射规范

> **AI开发必读** | 统一路径引用，避免硬编码

## 🎯 核心原则
所有AI和开发者必须使用路径别名，**严禁硬编码相对路径**！

## 📁 前端路径别名 (@ 别名系统)

### Vite配置 (frontend/vite.config.js)
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

### 正确使用示例 ✅
```javascript
// Vue组件中
import LoginForm from '@/components/LoginForm.vue'
import { useAuth } from '@/composables/useAuth.js'
import { apiClient } from '@/api/client.js'

// JavaScript文件中
import { formatDate } from '@/utils/date.js'
import { API_ENDPOINTS } from '@/config/api.js'
```

### 错误用法 ❌
```javascript
// 严禁使用相对路径
import LoginForm from '../../components/LoginForm.vue'
import { useAuth } from '../composables/useAuth.js'
import { apiClient } from '../../api/client.js'

// 严禁使用绝对路径
import LoginForm from 'C:/project/src/components/LoginForm.vue'
```

## 🐍 后端导入规范 (Python)

### 标准导入路径
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

### 导入路径映射表
| 用途 | 正确导入 | 错误导入 |
|------|----------|----------|
| API路由 | `from backend.api.v1.auth import router` | `from .auth import router` |
| 数据模型 | `from backend.models.user import User` | `from models.user import User` |
| 数据库工具 | `from backend.database_utils import get_db` | `from database_utils import get_db` |
| 核心模块 | `from backend.core.security import create_access_token` | `from core.security import create_access_token` |

## 🔧 TypeScript 路径配置 (如适用)

### tsconfig.json 配置
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/components/*": ["src/components/*"],
      "@/views/*": ["src/views/*"],
      "@/api/*": ["src/api/*"],
      "@/utils/*": ["src/utils/*"]
    }
  }
}
```

## 🚨 AI检查清单

在修改任何文件前，AI必须验证：

### 前端检查项
- [ ] 所有导入使用 `@/` 别名
- [ ] 无 `../` 或 `../../` 相对路径
- [ ] 无硬编码绝对路径
- [ ] 别名在vite.config.js中已定义

### 后端检查项
- [ ] 所有导入使用完整模块路径
- [ ] 无 `.` 或 `..` 相对导入
- [ ] 导入路径以 `backend.` 开头
- [ ] 符合Python包导入规范

### 自动化检查
```bash
# 检查路径别名使用情况
python scripts/check_ai_compliance.py --check-aliases

# 扫描不规范导入
python scripts/config_scanner.py --scan-imports
```

## 📝 最佳实践

1. **一致性**: 整个项目使用相同的别名约定
2. **可读性**: 别名应清晰表达模块用途
3. **维护性**: 新增别名需在vite.config.js中注册
4. **团队协作**: AI和开发者都必须遵循此规范

## 🔍 快速验证

```bash
# 检查当前文件导入规范
grep -r "\.\.\/\)" frontend/src/  # 查找相对路径
grep -r "from backend" backend/      # 验证后端导入
```

---
**记住**: 路径别名是项目协作的基础设施，所有AI必须严格遵守！