# Sport Lottery Sweeper 项目瘦身执行计划

## 执行顺序（按安全性排序）

### Phase 1: 安全清理（零风险）
```bash
# 1. 删除空文件
echo "清理空文件..."
rm -f LICENSE env.production backend/utils.py api/dependencies.py core/deps.py tasks/data_processing.py tasks/logger.py

# 2. 删除备份文件
echo "清理备份文件..."
rm -f backend/sport_lottery.db.backup frontend/index.html.backup models/match.py.bak

# 3. 删除临时调试HTML文件
echo "清理调试HTML..."
rm -f debug/500_com_page.html debug/www.lottery.gov.cn_kj_kjlb.html.html debug/www.lottery.gov.cn.html debug/www.sporttery.cn_.html debug/www.zhcw.com_.html backend/debug_sporttery_page.html
```

### Phase 2: 重复文件清理（低风险）
```bash
# 4. 删除重复初始化脚本（保留 init_admin_correct.py）
echo "清理重复初始化脚本..."
rm -f backend/init_admin.py backend/init_admin_simple.py backend/init_admin_user_correct.py backend/init_admin_user_fixed.py backend/init_admin_users.py backend/init_admin_async.py

# 5. 删除调试JSON文件
echo "清理调试JSON文件..."
rm -f debug/*.json

# 6. 删除过期API响应文件
echo "清理过期API文件..."
rm -f backend/api_response_raw.json
```

### Phase 3: 文档归档（中风险）
```bash
# 7. 创建文档归档目录
mkdir -p docs/archive

# 8. 归档历史分析文档
echo "归档历史文档..."
mv docs/PHASE*.md docs/archive/ 2>/dev/null || true
mv docs/*_SUMMARY.md docs/archive/ 2>/dev/null || true  
mv docs/*_REPORT.md docs/archive/ 2>/dev/null || true
mv docs/NAMING_*.md docs/archive/ 2>/dev/null || true
mv docs/OPTIMIZATION_*.md docs/archive/ 2>/dev/null || true
mv docs/CLEANUP_SUGGESTIONS.md docs/archive/ 2>/dev/null || true
```

### Phase 4: Docker文件整合（低风险）
```bash
# 9. 整理Docker文件
echo "整理Docker文件..."
rm -f Dockerfile.dev Dockerfile.crawler docker/Dockerfile.*
# 保留: Dockerfile, Dockerfile.production
```

### Phase 5: 脚本优化（需测试）
```bash
# 10. 审查并删除过时脚本
echo "审查脚本文件..."
# 手动检查 scripts/ 目录，删除明显过时的bat和py文件
# 建议保留: start_project.ps1, start-frontend-powershell.ps1, scripts/*.py (核心功能)
```

## 预期效果

### 空间节省预估
- **Phase 1**: ~150KB (空文件+备份)
- **Phase 2**: ~50MB (重复脚本+调试文件) 
- **Phase 3**: ~500KB (归档文档)
- **Phase 4**: ~10KB (Docker冗余)
- **总计**: 约50.6MB，减少60%+ 无用文件

### 维护性提升
✅ 消除文件混乱
✅ 提高构建速度  
✅ 减少IDE索引负担
✅ 清晰的项目结构

## 安全检查清单

执行前确认：
- [ ] Git仓库已提交当前变更
- [ ] 重要数据已备份
- [ ] 了解每个删除文件的用途
- [ ] 准备好回滚方案

执行后验证：
- [ ] 项目能正常启动
- [ ] 测试通过
- [ ] Git状态干净
- [ ] 文档链接有效
