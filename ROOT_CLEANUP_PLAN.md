# 根目录文件整理计划

## 📊 当前状况分析

根目录共有200+文件，主要包括：
- **文档类**: 16个 `.md` 文件 + 4个 `.docx` 文件
- **临时文件**: 4个Office临时文件(`~$*`), 1个coverage临时文件
- **测试报告**: 8个 `.txt` 文件, 2个 `.png` 截图
- **脚本文件**: 100+个 `.py` 检查/分析/测试脚本
- **数据文件**: 2个 `.json` 数据文件(3900494.json较大)
- **配置文件**: 各种 `.env*` 文件

## 🎯 整理方案

### Phase 1: 创建目录结构 (安全无风险)
```bash
# 创建整理目录
mkdir -p docs reports temp tools archives
```

### Phase 2: 移动文档类文件 (低风险)
**目标目录**: `docs/`
**文件列表**:
- `1.md`, `2.md` 
- `项目说明文档.md`, `项目完成状态总结报告.md`
- `第一阶段基础设施修复报告.md`, `第三阶段深度诊断报告.md`
- `爬虫管理API完善总结.md`, `用户操作模拟测试报告.md`
- `ADMIN_PANEL_EVALUATION.md`, `ADMIN_PANEL_OPTIMIZATION_PLAN.md`
- `API_VERIFICATION_GUIDE.md`, `AUTO_TEST_INTEGRATION_SUMMARY.md`
- `BEIDAN_SCHEDULE_E2E_EVALUATION.md`, `BEIDAN_SCHEDULE_E2E_TEST_PLAN.md`
- `CAPTCHA_INTEGRATION_SUMMARY.md`, `CONFIGURATION_MANAGEMENT.md`
- `CONFIGURATION_SETUP.md`, `cleanup_plan.md`
- `当点击.docx`, `平局.docx`, `三维精算筛选器.docx`, `在http.docx`

### Phase 3: 移动测试报告和日志 (低风险)
**目标目录**: `reports/`
**文件列表**:
- `auth_smoke_get_results_latest.txt`, `auth_smoke_get_results.txt`
- `backend_server.err`, `backend_start_test.log`, `backend_test_final.log`
- `complete_e2e_test_error.png`, `completed_e2e_test_error.png`
- `error.log`, `final_test.log`, `startup_stderr.log`, `startup_stdout.log`
- `response*.txt` (所有response开头的txt文件)

### Phase 4: 移动临时文件 (无风险)
**目标目录**: `temp/`
**文件列表**:
- `~$当点击.docx`, `~$平局.docx`, `~$维精算筛选器.docx`, `~$在http.docx`
- `.coverage.dmc.pid52796.XxzeZgFx.HNQIp837rWOh`

### Phase 5: 移动工具脚本 (需谨慎验证)
**目标目录**: `tools/`
**文件列表** (按功能分组):

#### 检查工具 (`tools/checkers/`)
- `check_*.py` (所有以check_开头的py文件)

#### 分析工具 (`tools/analyzers/`)
- `analyze_*.py`, `capture_errors.py`, `compare_*.py`

#### 创建工具 (`tools/creators/`)
- `create_*.py`, `add_*.py`, `clear_tasks.py`

#### 测试工具 (`tools/tests/`)
- 根目录的 `test_*.py` 文件

#### 其他工具 (`tools/misc/`)
- `crawl_and_store_ips.py`, `continuous_monitor_task_32.py`
- `count_*.py`, `complete_*.py`, `comprehensive_*.py`

### Phase 6: 特殊处理的大文件
**需要确认的**:
- `3900494.json` (2.86MB) - 看起来是球队数据，移到 `data/archive/`
- `3900494 (1).json` (22KB) - 相关数据，同目录
- `1.7.4`, `0.1.53` - 需要查看内容确定分类

## ⚠️ 绝对不能移动的文件
```
保留文件清单:
✅ .env, .env.production, .env.example, .env.llm.example
✅ .gitignore, .dockerignore, .pre-commit-config.yaml  
✅ README.md, PROJECT_STRUCTURE.md, STARTUP_GUIDE.md
✅ docker-compose*.yml, Dockerfile*
✅ package*.json, pnpm-*, requirements*.txt
✅ backend/, frontend/, tests/, scripts/, data/
✅ alembic.ini, alembic/ (数据库迁移配置)
```

## 🚀 执行脚本

创建安全的整理脚本:
```bash
#!/bin/bash
# scripts/cleanup_root_directory.sh

echo "🧹 开始根目录整理..."
echo "创建备份时间点: $(date)"

# 创建整理目录
echo "📁 创建整理目录..."
mkdir -p docs reports temp tools/{checkers,analyzers,creators,tests,misc} archives

# Phase 2: 移动文档
echo "📚 移动文档文件..."
mv 1.md 2.md 项目说明文档.md 项目完成状态总结报告.md \
   第一阶段基础设施修复报告.md 第三阶段深度诊断报告.md \
   爬虫管理API完善总结.md 用户操作模拟测试报告.md \
   ADMIN_PANEL_EVALUATION.md ADMIN_PANEL_OPTIMIZATION_PLAN.md \
   API_VERIFICATION_GUIDE.md AUTO_TEST_INTEGRATION_SUMMARY.md \
   BEIDAN_SCHEDULE_E2E_EVALUATION.md BEIDAN_SCHEDULE_E2E_TEST_PLAN.md \
   CAPTCHA_INTEGRATION_SUMMARY.md CONFIGURATION_MANAGEMENT.md \
   CONFIGURATION_SETUP.md cleanup_plan.md \
   当点击.docx 平局.docx 三维精算筛选器.docx 在http.docx \
   docs/ 2>/dev/null || echo "部分文档文件可能已存在"

# Phase 3: 移动测试报告
echo "📊 移动测试报告..."
mv auth_smoke_get_results*.txt backend_server.err backend_start_test.log \
   backend_test_final.log complete_e2e_test_error.png completed_e2e_test_error.png \
   error.log final_test.log startup_stderr.log startup_stdout.log \
   response*.txt reports/ 2>/dev/null || echo "部分报告文件可能已存在"

# Phase 4: 移动临时文件
echo "🗑️  移动临时文件..."
mv ~$* .coverage.dmc.pid* temp/ 2>/dev/null || echo "临时文件移动完成"

# Phase 5: 移动脚本文件
echo "🔧 移动脚本文件..."
# 检查工具
mv check_*.py tools/checkers/ 2>/dev/null || echo "检查脚本移动完成"

# 分析工具  
mv analyze_*.py capture_errors.py compare_*.py tools/analyzers/ 2>/dev/null || echo "分析脚本移动完成"

# 创建工具
mv create_*.py add_*.py clear_tasks.py tools/creators/ 2>/dev/null || echo "创建脚本移动完成"

# 根目录测试文件
mv test_*.py tools/tests/ 2>/dev/null || echo "测试脚本移动完成"

# 其他工具
mv crawl_and_store_ips.py continuous_monitor_task_32.py count_*.py \
   complete_*.py comprehensive_*.py tools/misc/ 2>/dev/null || echo "其他工具移动完成"

# Phase 6: 特殊处理
echo "📦 处理特殊文件..."
mkdir -p data/archive
mv 3900494*.json data/archive/ 2>/dev/null || echo "数据文件移动完成"

# 处理未知文件
echo "❓ 检查未分类文件..."
ls -la | grep -E "^[d-]r" | awk '{print $9}' | grep -v -E "(^docs|^reports|^temp|^tools|^archives|^backend|^frontend|^tests|^scripts|^data|\.|README|PROJECT_STRUCTURE|STARTUP_GUIDE|docker-compose|Dockerfile|package-|pnpm-|requirements|alembic)" > uncategorized_files.txt

if [ -s uncategorized_files.txt ]; then
    echo "发现未分类文件，请手动处理:"
    cat uncategorized_files.txt
else
    echo "✅ 所有文件已分类完成"
    rm -f uncategorized_files.txt
fi

echo "🎉 根目录整理完成!"
echo "📋 建议运行以下命令验证项目:"
echo "  - python backend_start.py"
echo "  - npm run dev (在前端目录)"
echo "  - 检查是否有ImportError"
```

## 🔙 回滚方案

如果出现问题，使用回滚脚本:
```bash
#!/bin/bash
# scripts/rollback_root_cleanup.sh

echo "🔄 开始回滚根目录整理..."

# 移动文档回根目录
mv docs/*.md docs/*.docx . 2>/dev/null

# 移动报告回根目录  
mv reports/*.txt reports/*.png reports/*.err reports/*.log . 2>/dev/null

# 移动临时文件回根目录
mv temp/~$* temp/.coverage.* . 2>/dev/null

# 移动脚本回根目录
mv tools/*/*.py . 2>/dev/null

# 移动数据文件回根目录
mv data/archive/3900494*.json . 2>/dev/null

echo "✅ 回滚完成"
```

## 📋 验证清单

整理完成后验证:
- [ ] 项目能正常启动 (`python backend_start.py`)
- [ ] 前端能正常启动 (`cd frontend && npm run dev`)
- [ ] 没有ImportError或ModuleNotFoundError
- [ ] Git状态正常 (`git status` 无异常)
- [ ] 所有配置文件路径正确
- [ ] 测试能正常运行

## ⏱️ 执行时间

预计执行时间: 5-10分钟
风险评估: 低风险 (有完整回滚方案)