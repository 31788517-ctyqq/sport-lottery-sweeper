# 命名规则优化 - 执行检查清单

> ✅ 使用此清单确保每一步都正确执行

---

## 📋 Phase 1: 文件结构优化

### ⏰ 预计时间: 2-4小时
### 🎯 风险等级: 🟢 低

---

## 🔰 准备阶段 (15-30分钟)

### 1. 文档阅读

- [ ] 已阅读 `NAMING_OPTIMIZATION_QUICKSTART.md` (5分钟)
- [ ] 了解 Phase 1 的执行内容
- [ ] 知道如何回滚

### 2. 环境准备

- [ ] Git 状态已提交
  ```bash
  git status  # 确保工作区干净
  ```

- [ ] 创建优化分支
  ```bash
  git checkout -b feature/naming-optimization
  ```

- [ ] 数据库已备份（如有生产数据）
  ```bash
  # PostgreSQL
  pg_dump sport_lottery > backup_$(date +%Y%m%d).sql
  
  # SQLite
  cp backend/sport_lottery.db backup_sport_lottery_$(date +%Y%m%d).db
  ```

- [ ] 已通知团队成员
  ```
  主题: Phase 1 命名规则优化执行通知
  时间: [填写时间]
  影响: 开发环境（不影响生产）
  注意: 暂停向 main 分支提交 PR
  ```

### 3. 工具检查

- [ ] Python 环境可用
  ```bash
  python --version
  ```

- [ ] Node.js 环境可用
  ```bash
  node --version
  npm --version
  ```

- [ ] 测试工具可用
  ```bash
  pytest --version
  ```

---

## 🗂️ 执行阶段 (1-2小时)

### 步骤 1: Backend 清理 (30-60分钟)

#### 1.1 执行清理脚本

- [ ] 运行脚本
  ```bash
  scripts\phase1-cleanup-backend.bat
  ```

- [ ] 检查执行日志
  - [ ] 调试文件已移动
  - [ ] 爬虫脚本已移动
  - [ ] 测试文件已移动
  - [ ] 其他脚本已移动

- [ ] 记录清理结果
  ```
  清理前文件数: ___ 个
  清理后文件数: ___ 个
  移动文件数: ___ 个
  ```

#### 1.2 处理重复文件

- [ ] 检查重复版本
  ```bash
  dir backend\scripts\crawlers\*_optimized*.py
  dir backend\scripts\crawlers\*_enhanced*.py
  dir backend\scripts\crawlers\*_final*.py
  ```

- [ ] 确认最新版本
  - [ ] 查看文件修改时间
  - [ ] 比较文件内容
  - [ ] 咨询原作者（如需要）

- [ ] 删除旧版本
  ```bash
  # 示例
  del backend\scripts\crawlers\get_sporttery_data_optimized.py
  del backend\scripts\crawlers\debug_scraper_enhanced.py
  ```

- [ ] 记录删除的文件
  ```
  删除文件列表:
  1. _______________
  2. _______________
  3. _______________
  ```

#### 1.3 更新导入路径

- [ ] 查找需要更新的导入
  ```bash
  findstr /s /i "from backend.debug_" backend\*.py
  findstr /s /i "from backend.get_" backend\*.py
  findstr /s /i "from backend.test_" backend\*.py
  ```

- [ ] 逐个文件更新
  ```python
  # 旧导入
  from backend.debug_scraper import DebugScraper
  
  # 新导入
  from backend.debug.debug_scraper import DebugScraper
  ```

- [ ] 记录更新的文件
  ```
  更新文件列表:
  1. _______________
  2. _______________
  3. _______________
  ```

---

### 步骤 2: Frontend 修复 (15-30分钟)

#### 2.1 检查目录结构

- [ ] 确认目录存在
  ```bash
  dir frontend\src\components\store
  ```

- [ ] 如目录不存在，跳过此步骤

#### 2.2 执行修复脚本

- [ ] 运行脚本
  ```bash
  scripts\phase1-fix-frontend-structure.bat
  ```

- [ ] 确认文件移动
  - [ ] modules 已移动到 stores/modules
  - [ ] plugins 已移动到 stores/plugins

- [ ] 确认删除旧目录
  - [ ] components/store 已删除
  - [ ] 或保留但已备份

#### 2.3 更新导入路径

- [ ] 查找需要更新的导入
  ```bash
  findstr /s /i "components/store" frontend\src\*.vue
  findstr /s /i "components/store" frontend\src\*.js
  ```

- [ ] 逐个文件更新
  ```javascript
  // 旧导入
  import matches from '@/components/store/modules/matches'
  
  // 新导入
  import matches from '@/stores/modules/matches'
  ```

- [ ] 记录更新的文件
  ```
  更新文件列表:
  1. _______________
  2. _______________
  ```

---

### 步骤 3: 根目录整理 (10-15分钟)

#### 3.1 移动文档

- [ ] 检查重复文档
  ```bash
  # 比较内容
  fc QUICK_START.md docs\QUICK_START.md
  ```

- [ ] 移动到 docs/
  ```bash
  move DEMO.md docs\
  # 根据实际情况处理 QUICK_START.md
  ```

#### 3.2 移动脚本

- [ ] 移动根目录测试脚本
  ```bash
  mkdir scripts\tests
  move crawl_*.py scripts\tests\
  move test_*.py scripts\tests\
  move quick_test.py scripts\tests\
  ```

- [ ] 记录移动的文件
  ```
  移动文件列表:
  1. _______________
  2. _______________
  ```

---

## ✅ 验证阶段 (20-30分钟)

### 1. 自动验证

- [ ] 运行验证脚本
  ```bash
  scripts\verify-phase1.bat
  ```

- [ ] 检查验证结果
  - [ ] Backend 文件已移动 ✓
  - [ ] Frontend 目录已修复 ✓
  - [ ] 核心文件完整 ✓
  - [ ] 无明显导入错误 ✓

- [ ] 所有检查通过
  - [ ] 是 → 继续下一步
  - [ ] 否 → 查看问题并修复

### 2. 单元测试

- [ ] 运行 Backend 测试
  ```bash
  cd backend
  pytest tests/ -v
  ```

- [ ] 测试结果
  ```
  通过: ___ 个
  失败: ___ 个
  跳过: ___ 个
  ```

- [ ] 如有失败，记录并修复
  ```
  失败测试:
  1. _______________
  2. _______________
  ```

### 3. 启动验证

- [ ] 启动后端
  ```bash
  python backend/main.py
  ```

- [ ] 检查启动日志
  - [ ] 无错误信息
  - [ ] 所有模块加载成功
  - [ ] 监听端口正常

- [ ] 访问 API 文档
  ```
  URL: http://localhost:8000/docs
  状态: [ ] 可访问  [ ] 不可访问
  ```

- [ ] 启动前端
  ```bash
  cd frontend
  npm run dev
  ```

- [ ] 检查启动日志
  - [ ] 无错误信息
  - [ ] 编译成功
  - [ ] 监听端口正常

- [ ] 访问前端页面
  ```
  URL: http://localhost:5173
  状态: [ ] 可访问  [ ] 不可访问
  ```

### 4. 功能测试

- [ ] 测试核心 API
  ```bash
  # 测试比赛列表
  curl http://localhost:8000/api/v1/jczq/matches
  
  # 测试新路由（如已实现）
  curl http://localhost:8000/api/v1/lottery/football/matches
  ```

- [ ] API 响应正常
  - [ ] 返回数据
  - [ ] 无错误信息
  - [ ] 响应时间正常

- [ ] 测试前端功能
  - [ ] 比赛列表显示
  - [ ] 筛选功能正常
  - [ ] 详情页正常
  - [ ] 无控制台错误

---

## 🔄 问题处理

### 如遇到问题

#### 1. 导入错误

- [ ] 问题描述
  ```
  错误信息: _________________
  影响文件: _________________
  ```

- [ ] 解决方案
  - [ ] 更新导入路径
  - [ ] 重新运行测试
  - [ ] 确认修复成功

#### 2. 测试失败

- [ ] 问题描述
  ```
  失败测试: _________________
  错误信息: _________________
  ```

- [ ] 解决方案
  - [ ] 分析失败原因
  - [ ] 修复代码
  - [ ] 重新运行测试

#### 3. 功能异常

- [ ] 问题描述
  ```
  异常功能: _________________
  错误信息: _________________
  ```

- [ ] 解决方案
  - [ ] 检查日志
  - [ ] 回滚相关改动
  - [ ] 或使用完整回滚

### 回滚决策

- [ ] 是否需要回滚？
  - [ ] 否 → 继续修复问题
  - [ ] 是 → 执行回滚

- [ ] 执行回滚
  ```bash
  scripts\rollback-phase1.bat
  ```

- [ ] 验证回滚
  - [ ] 文件恢复原位
  - [ ] 测试通过
  - [ ] 功能正常

---

## 📊 结果记录

### 执行统计

- **开始时间**: ___:___ 
- **结束时间**: ___:___
- **总耗时**: ___ 小时

### 文件统计

- **Backend 文件数**
  - 清理前: ___ 个
  - 清理后: ___ 个
  - 移动数量: ___ 个

- **Frontend 文件数**
  - 修复前: ___ 个
  - 修复后: ___ 个
  - 移动数量: ___ 个

### 测试结果

- **单元测试**
  - 通过: ___ 个
  - 失败: ___ 个
  - 覆盖率: ____%

- **功能测试**
  - 测试项: ___ 个
  - 通过: ___ 个
  - 失败: ___ 个

### 问题记录

- **遇到的问题**: ___ 个
  1. ___________________
  2. ___________________
  3. ___________________

- **解决方案**:
  1. ___________________
  2. ___________________
  3. ___________________

---

## 🎉 完成阶段

### 1. 代码提交

- [ ] 查看改动
  ```bash
  git status
  git diff
  ```

- [ ] 添加文件
  ```bash
  git add .
  ```

- [ ] 提交代码
  ```bash
  git commit -m "refactor: Phase 1 文件结构优化

  - 清理 Backend 30+ 临时文件
  - 修复前端目录结构重复
  - 整理根目录文档
  - 更新导入路径
  
  相关文档: docs/NAMING_OPTIMIZATION_PLAN.md
  验证通过: scripts/verify-phase1.bat
  "
  ```

- [ ] 推送到远程
  ```bash
  git push -u origin feature/naming-optimization
  ```

### 2. 创建 Pull Request

- [ ] PR 标题
  ```
  refactor: Phase 1 命名规则优化 - 文件结构整理
  ```

- [ ] PR 描述
  ```markdown
  ## 📋 变更说明
  
  Phase 1: 文件结构优化
  
  ## 🎯 优化内容
  - [x] Backend 临时文件清理（30+ 文件）
  - [x] Frontend 目录结构修复
  - [x] 根目录文档整理
  - [x] 导入路径更新
  
  ## ✅ 验证结果
  - [x] 所有测试通过
  - [x] 功能正常运行
  - [x] 无性能影响
  
  ## 📊 统计数据
  - Backend 清理: ___ 个文件
  - Frontend 修复: ___ 个目录
  - 测试通过率: 100%
  
  ## 📚 相关文档
  - [优化计划](docs/NAMING_OPTIMIZATION_PLAN.md)
  - [健康检查](docs/NAMING_CONVENTION_HEALTH_CHECK.md)
  ```

- [ ] 指定审查人
  - [ ] 技术负责人
  - [ ] 后端工程师
  - [ ] 前端工程师

### 3. 团队通知

- [ ] 发送完成通知
  ```
  主题: ✅ Phase 1 命名规则优化已完成
  
  各位同事：
  
  Phase 1 文件结构优化已完成并通过所有测试。
  
  主要改动：
  - Backend 临时文件已整理
  - Frontend 目录结构已规范化
  - 根目录更清爽
  
  影响范围：
  - 开发环境文件结构
  - 不影响功能和性能
  
  后续行动：
  1. 请及时 pull 最新代码
  2. 如遇问题，查看文档或联系我
  
  感谢配合！
  ```

### 4. 文档更新

- [ ] 更新项目 README
  - [ ] 添加新目录结构说明
  - [ ] 更新开发指南

- [ ] 更新团队文档
  - [ ] 记录优化成果
  - [ ] 分享经验教训

### 5. 经验总结

- [ ] 记录心得
  ```
  成功经验:
  1. ___________________
  2. ___________________
  
  遇到困难:
  1. ___________________
  2. ___________________
  
  改进建议:
  1. ___________________
  2. ___________________
  ```

---

## 🎯 下一步计划

- [ ] Phase 2: 枚举类命名统一
  - 预计时间: 2-3小时
  - 计划日期: ___________

- [ ] Phase 3: API 路由国际化
  - 预计时间: 4-8小时
  - 计划日期: ___________

---

## ✅ 最终确认

### 完成检查

- [ ] ✅ 所有脚本执行成功
- [ ] ✅ 所有测试通过
- [ ] ✅ 功能验证正常
- [ ] ✅ 代码已提交
- [ ] ✅ PR 已创建
- [ ] ✅ 团队已通知
- [ ] ✅ 文档已更新

### 签字确认

- **执行人**: ___________
- **审核人**: ___________
- **完成日期**: ___________
- **状态**: [ ] 完成  [ ] 部分完成  [ ] 需改进

---

**恭喜！Phase 1 完成！** 🎉

**下一步**: 准备 Phase 2 的执行

---

**检查清单版本**: v1.0  
**最后更新**: 2026-01-19
