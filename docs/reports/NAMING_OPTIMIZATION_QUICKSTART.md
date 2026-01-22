# 命名规则优化 - 快速开始指南

> **快速、安全、可回滚的命名规则优化方案**

---

## 🚀 5分钟快速开始

### 方式 1: 使用总控脚本（推荐）

```bash
# Windows
scripts\naming-optimization.bat

# 按照菜单提示操作：
# 1. 选择 [1] 执行 Phase 1
# 2. 等待完成后选择 [V] 验证
# 3. 如有问题选择 [R] 回滚
```

### 方式 2: 单独执行

```bash
# 1. Phase 1: 清理文件结构
scripts\phase1-cleanup-backend.bat
scripts\phase1-fix-frontend-structure.bat

# 2. 验证
scripts\verify-phase1.bat

# 3. 如需回滚
scripts\rollback-phase1.bat
```

---

## 📋 Phase 1 详细说明

### 执行内容

✅ **Backend 清理** (2小时)
- 移动 30+ 临时/调试文件到规范目录
- 创建 `backend/debug/`、`backend/scripts/`、`backend/tests/integration/`
- 删除重复版本（需手动确认）

✅ **Frontend 修复** (1小时)
- 合并 `components/store` 到 `stores/`
- 统一状态管理目录结构

✅ **文档整理** (0.5小时)
- 移动根目录文档到 `docs/`
- 清理根目录测试脚本

### 影响范围

🟢 **低风险**
- ✅ 不修改核心业务逻辑
- ✅ 不改变 API 接口
- ✅ 不影响数据库
- ✅ 完全可回滚

### 预期结果

**清理前**:
```
backend/
├── debug_api.py                    ❌
├── debug_scraper.py                ❌
├── get_sporttery_data.py           ❌
├── get_real_sporttery_data_final.py ❌
└── ... (30+ 临时文件)
```

**清理后**:
```
backend/
├── main.py                         ✓
├── config.py                       ✓
├── models.py                       ✓
├── debug/                          ✓
│   └── debug_scraper.py
├── scripts/                        ✓
│   └── crawlers/
│       └── sporttery_scraper.py
└── tests/                          ✓
    └── integration/
```

---

## ✅ 验证清单

### 自动验证

```bash
# 运行验证脚本
scripts\verify-phase1.bat

# 检查项：
# ✓ Backend 文件已移动
# ✓ Frontend 目录已修复
# ✓ 核心文件完整
# ✓ 无明显导入错误
```

### 手动验证

```bash
# 1. 后端启动测试
python backend/main.py
# 访问: http://localhost:8000/docs

# 2. 运行单元测试
pytest backend/tests/ -v

# 3. 前端启动测试
cd frontend
npm run dev
# 访问: http://localhost:5173

# 4. API 功能测试
curl http://localhost:8000/api/v1/jczq/matches
```

---

## 🔄 回滚方案

### 快速回滚

```bash
# 使用回滚脚本（推荐）
scripts\rollback-phase1.bat

# 或使用 Git
git checkout HEAD -- backend/ frontend/
```

### 分步回滚

```bash
# 1. 查看备份
dir .naming-optimization\

# 2. 手动恢复
# Backend: 将 backend/debug/、backend/scripts/ 中的文件移回 backend/
# Frontend: 恢复 .naming-optimization\components-store-backup\
```

---

## 🔍 故障排查

### 问题 1: 导入错误

**症状**:
```python
ModuleNotFoundError: No module named 'backend.debug_scraper'
```

**解决**:
```python
# 更新导入路径
from backend.debug.debug_scraper import DebugScraper
```

**查找需要更新的文件**:
```bash
findstr /s /i "from backend.debug_" backend\*.py
findstr /s /i "from backend.get_" backend\*.py
```

### 问题 2: 前端状态管理失效

**症状**: Pinia store 无法找到

**解决**:
```javascript
// 更新导入
// 旧: import matches from '@/components/store/modules/matches'
// 新: import matches from '@/stores/modules/matches'
```

### 问题 3: 文件缺失

**解决**: 查看备份
```bash
# Backend 文件列表备份
type .naming-optimization\backend-files-before.txt

# Frontend 备份
dir .naming-optimization\components-store-backup\
```

---

## 📊 执行时间表

| 任务 | 预计时间 | 风险 |
|------|---------|------|
| 阅读文档 | 10分钟 | - |
| 执行 Phase 1 | 30-60分钟 | 🟢 低 |
| 验证功能 | 20分钟 | - |
| 处理问题 | 0-30分钟 | - |
| **总计** | **1-2小时** | 🟢 低 |

---

## 🎯 下一步计划

完成 Phase 1 后，可以继续执行：

### Phase 2: 枚举类命名统一（预计 2-3小时）
- 统一添加 `Enum` 后缀
- 更新所有引用
- 验证数据库迁移

### Phase 3: API 路由国际化（预计 4-8小时）
- 创建英文路由 `/api/v1/lottery/football/`
- 保持向后兼容
- 逐步迁移前端

### Phase 4-5: 其他优化（预计 8-12小时）
- CSS 类名 BEM 规范化
- 常量命名优化

---

## 📚 相关文档

| 文档 | 路径 | 说明 |
|------|------|------|
| **优化计划** | `docs/NAMING_OPTIMIZATION_PLAN.md` | 完整执行计划 |
| **健康检查报告** | `docs/NAMING_CONVENTION_HEALTH_CHECK.md` | 问题分析 |
| **业务模块列举** | `docs/BUSINESS_MODULES_OVERVIEW.md` | 项目架构 |
| **快速开始** | `NAMING_OPTIMIZATION_QUICKSTART.md` | 本文档 |

---

## ⚠️ 重要提示

### 执行前

- ✅ 确保代码已提交到 Git
- ✅ 通知团队成员暂停合并 PR
- ✅ 备份数据库（如有生产数据）
- ✅ 在开发分支上执行

### 执行中

- ✅ 仔细阅读每步提示
- ✅ 不要跳过验证步骤
- ✅ 记录遇到的问题
- ✅ 保持冷静，所有操作可回滚

### 执行后

- ✅ 运行完整测试套件
- ✅ 验证所有功能正常
- ✅ 更新团队文档
- ✅ 提交代码并推送

---

## 🆘 获取帮助

如遇到问题：

1. **查看日志**: `.naming-optimization/` 目录
2. **查阅文档**: 详细优化计划和健康检查报告
3. **使用回滚**: 快速恢复到初始状态
4. **团队讨论**: 与团队成员沟通

---

## ✅ 成功标志

当你看到以下结果，说明 Phase 1 成功：

- ✅ `scripts\verify-phase1.bat` 全部通过
- ✅ `pytest backend/tests/` 测试通过
- ✅ `python backend/main.py` 正常启动
- ✅ `npm run dev` 前端正常运行
- ✅ API 功能正常响应

---

**准备好了吗？让我们开始优化！** 🚀

```bash
scripts\naming-optimization.bat
```
