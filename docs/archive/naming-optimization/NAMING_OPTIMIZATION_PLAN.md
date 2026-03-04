# 命名规则优化执行计划

> **项目**: Sport Lottery Sweeper  
> **执行日期**: 2026-01-19  
> **目标**: 优化命名规则，确保系统稳定性  
> **风险等级**: 中等 ⚠️

---

## 🎯 优化目标

- ✅ 提升项目结构清晰度 100%
- ✅ 提升命名一致性 32%
- ✅ 提升代码可维护性 38%
- ✅ 确保系统零宕机

---

## 📋 优化策略

### 核心原则

1. **渐进式优化** - 分阶段执行，避免大规模改动
2. **向后兼容** - 保留旧接口，逐步迁移
3. **充分测试** - 每步完成后验证功能
4. **可回滚** - 使用 Git 分支，支持快速回滚
5. **文档同步** - 及时更新文档和注释

---

## 🚦 优化阶段划分

### Phase 0: 准备阶段 (1小时)
**风险**: 🟢 低  
**影响范围**: 无  
**可回滚**: ✅

- [ ] 创建 Git 分支 `feature/naming-optimization`
- [ ] 备份数据库
- [ ] 记录当前系统状态
- [ ] 准备回滚脚本

### Phase 1: 文件结构优化 (2-4小时)
**风险**: 🟢 低  
**影响范围**: 开发环境  
**可回滚**: ✅

- [ ] 清理 backend/ 临时文件
- [ ] 修复前端目录重复
- [ ] 整理根目录文档
- [ ] 更新导入路径

### Phase 2: 枚举类命名统一 (2-3小时)
**风险**: 🟡 中  
**影响范围**: 数据模型  
**可回滚**: ✅

- [ ] 统一枚举类命名（添加 Enum 后缀）
- [ ] 更新所有引用
- [ ] 运行单元测试

### Phase 3: API 路由国际化 (4-8小时)
**风险**: 🟡 中  
**影响范围**: 前后端接口  
**可回滚**: ✅

- [ ] 创建新英文路由
- [ ] 保持旧路由向后兼容
- [ ] 前端逐步迁移
- [ ] 添加废弃警告

### Phase 4: CSS 类名规范化 (8-16小时)
**风险**: 🟢 低  
**影响范围**: 前端样式  
**可回滚**: ✅

- [ ] 统一为 BEM 规范
- [ ] 逐个组件重构
- [ ] 视觉回归测试

### Phase 5: 常量命名优化 (3-4小时)
**风险**: 🟢 低  
**影响范围**: 配置文件  
**可回滚**: ✅

- [ ] JavaScript 常量改为 UPPER_CASE
- [ ] Python 常量规范化
- [ ] 更新引用

---

## 🛠️ Phase 0: 准备阶段

### 执行步骤

```bash
# 1. 创建优化分支
git checkout -b feature/naming-optimization
git push -u origin feature/naming-optimization

# 2. 备份数据库
pg_dump sport_lottery > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. 记录当前系统状态
git log -1 > .naming-optimization/current-state.txt
pip freeze > .naming-optimization/requirements-backup.txt
npm list --depth=0 > .naming-optimization/npm-backup.txt

# 4. 创建回滚脚本
cat > .naming-optimization/rollback.sh << 'EOF'
#!/bin/bash
echo "Rolling back naming optimization..."
git checkout main
git branch -D feature/naming-optimization
echo "Rollback completed"
EOF
chmod +x .naming-optimization/rollback.sh
```

### 验证清单

- [ ] Git 分支创建成功
- [ ] 数据库备份完成
- [ ] 回滚脚本可执行
- [ ] 团队成员已通知

---

## 🗂️ Phase 1: 文件结构优化

### 1.1 清理 Backend 临时文件

**执行脚本**: `scripts/cleanup-backend-temp-files.sh`

```bash
#!/bin/bash
set -e  # 遇到错误立即退出

echo "=== Phase 1.1: 清理 Backend 临时文件 ==="

# 创建目标目录
mkdir -p backend/debug
mkdir -p backend/scripts/crawlers
mkdir -p backend/tests/integration

# 备份原文件列表
ls backend/*.py > .naming-optimization/backend-files-before.txt

# 移动调试文件
echo "移动调试文件..."
for file in backend/debug_*.py; do
    [ -e "$file" ] && mv "$file" backend/debug/
done

# 移动数据采集脚本
echo "移动数据采集脚本..."
for file in backend/get_*.py backend/*_sporttery_*.py backend/*_crawler*.py; do
    [ -e "$file" ] && mv "$file" backend/scripts/crawlers/
done

# 移动测试文件
echo "移动测试文件..."
for file in backend/test_*.py backend/verify_*.py backend/check_*.py; do
    [ -e "$file" ] && mv "$file" backend/tests/integration/
done

# 移动其他脚本
echo "移动其他脚本..."
for file in backend/show_*.py backend/run_*.py backend/find_*.py backend/inspect_*.py; do
    [ -e "$file" ] && mv "$file" backend/scripts/
done

# 记录移动后的文件
ls backend/*.py > .naming-optimization/backend-files-after.txt

echo "✅ Backend 临时文件清理完成"
echo "清理前文件数: $(wc -l < .naming-optimization/backend-files-before.txt)"
echo "清理后文件数: $(wc -l < .naming-optimization/backend-files-after.txt)"
```

**需要手动确认的重复文件**:

```bash
# 检查重复版本
ls backend/scripts/crawlers/*_optimized*.py
ls backend/scripts/crawlers/*_enhanced*.py
ls backend/scripts/crawlers/*_final*.py

# 手动确认后删除
# rm backend/scripts/crawlers/[重复文件名]
```

### 1.2 修复前端目录重复

**执行脚本**: `scripts/fix-frontend-structure.sh`

```bash
#!/bin/bash
set -e

echo "=== Phase 1.2: 修复前端目录结构 ==="

# 检查目录是否存在
if [ ! -d "frontend/src/components/store" ]; then
    echo "⚠️  components/store 目录不存在，跳过"
    exit 0
fi

# 创建目标目录
mkdir -p frontend/src/stores/modules
mkdir -p frontend/src/stores/plugins

# 移动 modules
if [ -d "frontend/src/components/store/modules" ]; then
    echo "移动 modules..."
    cp -r frontend/src/components/store/modules/* frontend/src/stores/modules/
fi

# 移动 plugins
if [ -d "frontend/src/components/store/plugins" ]; then
    echo "移动 plugins..."
    cp -r frontend/src/components/store/plugins/* frontend/src/stores/plugins/
fi

# 验证文件完整性
if [ "$(ls -A frontend/src/stores/modules)" ] && [ "$(ls -A frontend/src/stores/plugins)" ]; then
    echo "✅ 文件移动成功，删除旧目录"
    rm -rf frontend/src/components/store
else
    echo "❌ 文件移动失败，保留原目录"
    exit 1
fi

echo "✅ 前端目录结构修复完成"
```

### 1.3 整理根目录文档

**执行脚本**: `scripts/organize-root-docs.sh`

```bash
#!/bin/bash
set -e

echo "=== Phase 1.3: 整理根目录文档 ==="

# 移动文档到 docs/
[ -f "DEMO.md" ] && mv "DEMO.md" docs/
[ -f "README_START.md" ] && mv "README_START.md" docs/

# 检查重复文档
if [ -f "QUICK_START.md" ] && [ -f "docs/QUICK_START.md" ]; then
    echo "⚠️  发现重复的 QUICK_START.md"
    echo "请手动比较并决定保留哪个版本"
    diff QUICK_START.md docs/QUICK_START.md || true
fi

# 移动根目录测试脚本到 scripts/
mkdir -p scripts/tests
for file in crawl_*.py test_*.py quick_test.py find_*.py; do
    [ -e "$file" ] && mv "$file" scripts/tests/
done

echo "✅ 根目录文档整理完成"
ls -la | grep -E '\.(md|py)$' || echo "根目录清理完成"
```

### 1.4 更新导入路径

需要手动更新以下文件的导入路径：

```python
# backend/tests/integration/test_*.py
# 更新前
from backend.debug_scraper import DebugScraper

# 更新后
from backend.debug.debug_scraper import DebugScraper
```

**查找需要更新的导入**:
```bash
# 查找所有可能受影响的导入
grep -r "from backend.debug_" backend/ --include="*.py"
grep -r "from backend.get_" backend/ --include="*.py"
grep -r "from backend.test_" backend/ --include="*.py"
```

### Phase 1 验证清单

- [ ] Backend 临时文件已移动
- [ ] 前端目录结构已修复
- [ ] 根目录文档已整理
- [ ] 导入路径已更新
- [ ] **运行测试**: `pytest backend/tests/`
- [ ] **启动服务**: `python backend/main.py`
- [ ] **前端正常**: `npm run dev`

**回滚方法**:
```bash
git checkout HEAD -- backend/ frontend/
```

---

## 🏷️ Phase 2: 枚举类命名统一

### 2.1 识别需要修改的枚举类

```bash
# 查找所有没有 Enum 后缀的枚举类
grep -r "class \w\+\(enum\.Enum\)" backend/models/ --include="*.py" | grep -v "Enum(enum.Enum)"
```

### 2.2 创建重命名脚本

**执行脚本**: `scripts/rename-enums.py`

```python
#!/usr/bin/env python3
"""
枚举类重命名脚本
安全地将所有枚举类添加 Enum 后缀
"""
import os
import re
from pathlib import Path

# 需要重命名的枚举类映射
ENUM_RENAMES = {
    'UserRole': 'UserRoleEnum',
    'UserType': 'UserTypeEnum',
    'MatchType': 'MatchTypeEnum',
    # 添加更多...
}

def rename_enum_in_file(file_path: Path, old_name: str, new_name: str):
    """在文件中重命名枚举类"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 替换类定义
    content = re.sub(
        rf'\bclass {old_name}\(enum\.Enum\)',
        f'class {new_name}(enum.Enum)',
        content
    )
    
    # 替换类引用
    content = re.sub(
        rf'\b{old_name}\.',
        f'{new_name}.',
        content
    )
    
    # 替换导入
    content = re.sub(
        rf'\bfrom .* import .*{old_name}',
        lambda m: m.group(0).replace(old_name, new_name),
        content
    )
    
    if content != original_content:
        # 备份原文件
        backup_path = file_path.with_suffix('.py.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # 写入新内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    return False

def main():
    backend_dir = Path('backend')
    modified_files = []
    
    # 遍历所有 Python 文件
    for py_file in backend_dir.rglob('*.py'):
        for old_name, new_name in ENUM_RENAMES.items():
            if rename_enum_in_file(py_file, old_name, new_name):
                modified_files.append((py_file, old_name, new_name))
                print(f"✓ {py_file}: {old_name} → {new_name}")
    
    print(f"\n✅ 完成！共修改 {len(modified_files)} 个文件")
    
    # 保存修改记录
    with open('.naming-optimization/enum-renames.log', 'w') as f:
        for file, old, new in modified_files:
            f.write(f"{file},{old},{new}\n")

if __name__ == '__main__':
    main()
```

### 2.3 验证枚举重命名

```bash
# 运行重命名脚本
python scripts/rename-enums.py

# 验证没有遗漏
grep -r "class \w\+\(enum\.Enum\)" backend/models/ --include="*.py" | grep -v "Enum(enum.Enum)"

# 运行测试
pytest backend/tests/ -v

# 检查数据库迁移
alembic revision --autogenerate -m "Rename enum classes"
alembic upgrade head
```

### Phase 2 验证清单

- [ ] 所有枚举类已添加 Enum 后缀
- [ ] 所有引用已更新
- [ ] **单元测试通过**: `pytest backend/tests/`
- [ ] **数据库迁移成功**
- [ ] **API 响应正常**

**回滚方法**:
```bash
# 使用备份文件回滚
for file in backend/**/*.py.bak; do
    mv "$file" "${file%.bak}"
done
```

---

## 🌐 Phase 3: API 路由国际化

### 3.1 创建新的英文路由 (向后兼容)

**文件**: `backend/api/v1/lottery_football.py`

```python
"""
新的英文路由 - Football Lottery API
向后兼容旧的 jczq 路由
"""
from fastapi import APIRouter, Query
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from backend.api.v1.jczq import (
    load_500_com_data,
    get_jczq_matches as _get_matches_impl
)

logger = logging.getLogger(__name__)

# 新路由器 - 英文路径
router = APIRouter(
    prefix="/lottery/football",
    tags=["Football Lottery"],
    responses={404: {"description": "Not found"}}
)


@router.get("/matches", summary="Get football lottery matches")
async def get_matches(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Page size"),
    source: str = Query("auto", description="Data source: auto/500/sporttery"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    league: Optional[str] = Query(None, description="League filter"),
    day_filter: Optional[str] = Query(None, description="Day filter"),
    sort: Optional[str] = Query("date", description="Sort by: date/popularity"),
    order: Optional[str] = Query("asc", description="Order: asc/desc")
) -> Dict[str, Any]:
    """
    Get football lottery matches list with multi-source support
    
    Data source priority:
    - auto: Auto select (500.com first, fallback to sporttery)
    - 500: Force use 500.com data
    - sporttery: Force use sporttery data
    """
    logger.info(f"API called: /lottery/football/matches (source={source})")
    
    # 调用原有实现
    return await _get_matches_impl(
        page=page,
        size=size,
        source=source,
        date_from=date_from,
        date_to=date_to,
        league=league,
        day_filter=day_filter,
        sort=sort,
        order=order
    )


@router.get("/leagues", summary="Get available leagues")
async def get_leagues(
    source: str = Query("auto", description="Data source")
) -> Dict[str, Any]:
    """Get list of available leagues"""
    # 实现逻辑...
    pass


@router.post("/refresh", summary="Refresh cache")
async def refresh_cache() -> Dict[str, Any]:
    """Clear cache and force reload data"""
    # 实现逻辑...
    pass
```

### 3.2 更新 API 路由注册

**文件**: `backend/api/v1/__init__.py`

```python
from fastapi import APIRouter
from . import (
    jczq,
    lottery_football,  # 新增
    matches,
    public_matches,
    admin,
    auth,
    intelligence,
    data_submission
)

router = APIRouter(prefix="/v1")

# 新路由（推荐使用）
router.include_router(lottery_football.router)

# 旧路由（向后兼容，已废弃）
router.include_router(jczq.router)

# 其他路由...
router.include_router(matches.router)
router.include_router(public_matches.router)
# ...
```

### 3.3 添加废弃警告到旧路由

**文件**: `backend/api/v1/jczq.py`

```python
from fastapi import APIRouter, Response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jczq",
    tags=["竞彩足球 (Deprecated)"],
    deprecated=True  # FastAPI 自动标记为废弃
)

# 添加中间件：在响应头中添加废弃警告
@router.middleware("http")
async def add_deprecation_warning(request, call_next):
    response = await call_next(request)
    response.headers["X-API-Deprecated"] = "true"
    response.headers["X-API-Deprecated-Message"] = (
        "This API path is deprecated. "
        "Please use /api/v1/lottery/football/* instead."
    )
    response.headers["X-API-Sunset-Date"] = "2026-07-19"  # 6个月后
    return response


@router.get("/matches", deprecated=True)
async def get_jczq_matches(...):
    """
    [已废弃] 获取竞彩足球比赛列表
    
    ⚠️ DEPRECATED: This endpoint will be removed on 2026-07-19
    Please migrate to: GET /api/v1/lottery/football/matches
    """
    logger.warning(
        "Deprecated API called: /api/v1/jczq/matches. "
        "Please migrate to /api/v1/lottery/football/matches"
    )
    # 原有实现...
```

### 3.4 前端逐步迁移

**步骤 1: 创建新的 API 客户端**

**文件**: `frontend/src/api/lotteryFootball.js`

```javascript
/**
 * Football Lottery API Client (New English API)
 */
import { request } from './client'

/**
 * Get matches list
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>}
 */
export const getMatches = async (params = {}) => {
  return request.get('/api/v1/lottery/football/matches', { params })
}

/**
 * Get leagues list
 * @param {string} source - Data source
 * @returns {Promise<Object>}
 */
export const getLeagues = async (source = 'auto') => {
  return request.get('/api/v1/lottery/football/leagues', {
    params: { source }
  })
}

/**
 * Refresh cache
 * @returns {Promise<Object>}
 */
export const refreshCache = async () => {
  return request.post('/api/v1/lottery/football/refresh')
}

export default {
  getMatches,
  getLeagues,
  refreshCache
}
```

**步骤 2: 创建迁移配置**

**文件**: `frontend/src/config/api.js`

```javascript
/**
 * API 配置
 * USE_LEGACY_API: 是否使用旧的 API 路径
 */
export const API_CONFIG = {
  // 设置为 false 使用新 API，true 使用旧 API
  USE_LEGACY_API: false,
  
  // API 路径映射
  PATHS: {
    MATCHES: API_CONFIG.USE_LEGACY_API 
      ? '/api/v1/jczq/matches'
      : '/api/v1/lottery/football/matches',
    LEAGUES: API_CONFIG.USE_LEGACY_API
      ? '/api/v1/jczq/leagues'
      : '/api/v1/lottery/football/leagues',
  }
}
```

**步骤 3: 逐步切换**

```javascript
// frontend/src/views/JczqSchedule.vue
import { getMatches } from '@/api/lotteryFootball'  // 新 API
// import { getJczqMatches } from '@/api/jczq'      // 旧 API（注释掉）

export default {
  async mounted() {
    try {
      // 使用新 API
      const data = await getMatches({ source: '500', size: 10 })
      this.matches = data.data
    } catch (error) {
      console.error('Failed to fetch matches:', error)
    }
  }
}
```

### Phase 3 验证清单

- [ ] 新英文路由创建完成
- [ ] 旧路由添加废弃警告
- [ ] 前端API客户端已更新
- [ ] **两套API同时可用**
- [ ] **前端功能正常**
- [ ] **监控废弃API调用量**

**监控脚本**:
```bash
# 监控旧API调用
tail -f app.log | grep "Deprecated API called"
```

**回滚方法**:
```javascript
// 前端快速回滚：切换配置
export const API_CONFIG = {
  USE_LEGACY_API: true  // 改回 true
}
```

---

## 🎨 Phase 4: CSS 类名规范化

### 4.1 CSS 类名重构策略

**采用 BEM 规范**:
```
.block {}
.block__element {}
.block--modifier {}
.block__element--modifier {}
```

### 4.2 逐个组件重构

**示例: MatchCard.vue**

```vue
<!-- 重构前 -->
<template>
  <div class="match-card">
    <div class="match-card__header">
      <div class="matchTeams">           <!-- ❌ camelCase -->
        <span class="team_name">         <!-- ❌ snake_case -->
          {{ homeTeam }}
        </span>
      </div>
    </div>
  </div>
</template>

<!-- 重构后 -->
<template>
  <div class="match-card">
    <div class="match-card__header">
      <div class="match-card__teams">    <!-- ✓ BEM -->
        <span class="match-card__team-name match-card__team-name--home">
          {{ homeTeam }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* BEM 规范 */
.match-card {
  /* 块 */
}

.match-card__header {
  /* 元素 */
}

.match-card__teams {
  /* 元素 */
}

.match-card__team-name {
  /* 元素 */
}

.match-card__team-name--home {
  /* 修饰符 */
  color: blue;
}

.match-card__team-name--away {
  /* 修饰符 */
  color: red;
}

.match-card--featured {
  /* 块修饰符 */
  border: 2px solid gold;
}
</style>
```

### 4.3 创建CSS类名重构脚本

**文件**: `scripts/refactor-css-names.js`

```javascript
#!/usr/bin/env node
/**
 * CSS 类名重构辅助工具
 * 检测并建议 BEM 规范的类名
 */
const fs = require('fs')
const path = require('path')

const CSS_NAMING_RULES = {
  camelCase: /class="[a-z]+[A-Z][a-zA-Z]*"/g,
  snake_case: /class="[a-z]+_[a-z_]+"/g,
}

function analyzeCSSNaming(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8')
  const issues = []
  
  // 检测 camelCase
  const camelCases = content.match(CSS_NAMING_RULES.camelCase)
  if (camelCases) {
    camelCases.forEach(match => {
      const className = match.match(/class="([^"]*)"/)[1]
      issues.push({
        type: 'camelCase',
        original: className,
        suggested: className.replace(/([A-Z])/g, '-$1').toLowerCase()
      })
    })
  }
  
  // 检测 snake_case
  const snakeCases = content.match(CSS_NAMING_RULES.snake_case)
  if (snakeCases) {
    snakeCases.forEach(match => {
      const className = match.match(/class="([^"]*)"/)[1]
      issues.push({
        type: 'snake_case',
        original: className,
        suggested: className.replace(/_/g, '-')
      })
    })
  }
  
  return issues
}

// 扫描所有 Vue 文件
const componentsDir = 'frontend/src/components'
// 实现扫描逻辑...
```

### Phase 4 验证清单

- [ ] 核心组件CSS已重构
- [ ] **视觉回归测试通过**
- [ ] **响应式布局正常**
- [ ] **浏览器兼容性验证**

**视觉回归测试**:
```bash
# 使用 Percy 或 Playwright 进行截图对比
npm run test:visual
```

---

## 📊 Phase 5: 常量命名优化

### 5.1 JavaScript 常量规范化

```javascript
// frontend/src/stores/app.js

// ❌ 重构前
const mockConfig = {
  enabled: true,
  delay: 1000
}

// ✓ 重构后
const MOCK_CONFIG = {
  ENABLED: true,
  DELAY: 1000,
  DATA_SOURCE: 'local'
}

// 导出
export { MOCK_CONFIG }
```

### 5.2 Python 常量规范化

```python
# backend/config.py

# ✓ 统一使用 UPPER_CASE
API_VERSION = "v1"
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
CACHE_TTL = 300
REQUEST_TIMEOUT = 3000

# 枚举常量
class MatchStatus:
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
```

### Phase 5 验证清单

- [ ] JavaScript 常量已规范化
- [ ] Python 常量已规范化
- [ ] **所有引用已更新**
- [ ] **测试通过**

---

## ✅ 最终验证清单

### 功能验证

- [ ] **后端启动正常**: `python backend/main.py`
- [ ] **前端启动正常**: `npm run dev`
- [ ] **API 文档可访问**: `http://localhost:8000/docs`
- [ ] **所有端点响应正常**
- [ ] **WebSocket 连接正常**
- [ ] **数据库操作正常**

### 测试验证

- [ ] **单元测试**: `pytest backend/tests/ -v`
- [ ] **集成测试**: `pytest backend/tests/integration/ -v`
- [ ] **前端测试**: `npm run test`
- [ ] **E2E 测试**: `npm run test:e2e`
- [ ] **性能测试**: 响应时间无明显变化

### 文档验证

- [ ] API 文档已更新
- [ ] README 已更新
- [ ] 命名规范文档已创建
- [ ] 迁移指南已编写

---

## 🔄 回滚预案

### 快速回滚

```bash
# 回滚到优化前
git checkout main
git branch -D feature/naming-optimization

# 恢复数据库（如有需要）
psql sport_lottery < backup_*.sql
```

### 分阶段回滚

```bash
# 只回滚某个 Phase
git revert <phase-commit-hash>

# 或使用备份文件
cp backend/**/*.py.bak backend/**/*.py
```

---

## 📈 监控指标

### 关键指标

| 指标 | 优化前 | 目标 | 当前 |
|------|--------|------|------|
| API 响应时间 | 基线 | ≤ 基线+10% | - |
| 错误率 | 基线 | ≤ 基线 | - |
| 代码覆盖率 | - | ≥ 80% | - |
| 构建时间 | 基线 | ≤ 基线+5% | - |

### 监控脚本

```bash
# 监控 API 响应时间
while true; do
  curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/v1/lottery/football/matches"
  sleep 5
done

# 监控错误日志
tail -f app.log | grep -i error
```

---

## 🎓 团队协作

### 通知模板

```markdown
## 🚀 命名规则优化通知

各位团队成员：

我们正在执行项目命名规则优化，请注意以下事项：

### 当前阶段
Phase X: [阶段名称]

### 影响范围
- [ ] 后端 API
- [ ] 前端组件
- [ ] 数据库

### 需要您配合
1. 暂时不要合并 PR 到 main 分支
2. 如遇到问题，请及时反馈
3. 阅读最新的命名规范文档

### 预计完成时间
2026-01-XX XX:XX

感谢配合！
```

---

## ✅ 总结

通过渐进式、可回滚的优化策略，确保：

1. ✅ **零宕机** - 所有改动向后兼容
2. ✅ **可追溯** - 详细的变更记录
3. ✅ **可回滚** - 完善的备份和回滚机制
4. ✅ **可验证** - 每步都有验证清单
5. ✅ **可监控** - 实时监控关键指标

**预期成果**:
- 项目结构清晰度提升 100%
- 命名一致性提升 32%
- 代码可维护性提升 38%
- 系统稳定性保持 100%

---

**执行负责人**: 开发团队 Lead  
**预计总工作量**: 20-35 小时  
**建议执行周期**: 2-3周
