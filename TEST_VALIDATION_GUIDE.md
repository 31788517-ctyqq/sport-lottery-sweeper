# 测试环境验证指南

本文档提供了测试环境验证的详细指南，确保测试体系正确配置并可用。

## 📋 验证脚本

项目提供了完整的测试环境验证脚本，用于检查所有关键配置：

### 1. 环境验证脚本
```bash
# 运行完整的环境验证
python scripts/validate-test-environment.py

# 输出示例：
# 🚀 开始验证测试环境配置
# 🔍 检查: 前端依赖配置
#    ✅ 通过
# 🔍 检查: 后端依赖配置
#    ✅ 通过
# ... 更多检查
```

### 2. 覆盖率阈值检查
```bash
# 检查覆盖率是否满足要求
python scripts/check-coverage-thresholds.py

# 输出包括：
# 📊 前端覆盖率指标
# 📊 后端覆盖率指标
# 📋 覆盖率检查报告
```

### 3. 测试数据初始化
```bash
# 初始化测试数据
python scripts/init-test-data.py

# 创建：
# - 前端测试数据文件 (JSON格式)
# - 后端测试数据库 (SQLite)
# - 测试环境配置文件
```

## 🏗️ 验证内容

验证脚本检查以下关键配置：

### 前端配置检查
- [ ] `package.json` 中的测试依赖 (Vitest, Testing Library, Playwright)
- [ ] `vitest.config.js` 的完整配置
- [ ] 测试目录结构 (`src/tests/unit/`)
- [ ] 测试示例文件的存在性

### 后端配置检查  
- [ ] `requirements-dev.txt` 中的测试依赖 (pytest, pytest-cov, pytest-asyncio)
- [ ] `pyproject.toml` 中的 pytest 和 coverage 配置
- [ ] 测试目录结构 (`tests/unit/`, `tests/integration/`)
- [ ] 测试示例文件的存在性

### 基础设施检查
- [ ] CI/CD 配置文件 (`.github/workflows/ci-cd-optimized.yml`)
- [ ] 测试执行脚本 (`scripts/run-all-tests.sh`, `scripts/run-all-tests.bat`)
- [ ] 测试报告脚本 (`scripts/generate-test-report.py`)

## 🔧 修复常见问题

### 1. 前端依赖缺失
```bash
cd frontend
npm install --save-dev vitest @vitest/ui @vue/test-utils jsdom playwright
```

### 2. 后端依赖缺失
```bash
cd backend
pip install pytest pytest-cov pytest-asyncio
# 或更新 requirements-dev.txt
echo "pytest>=7.4.0" >> requirements-dev.txt
echo "pytest-cov>=4.1.0" >> requirements-dev.txt
echo "pytest-asyncio>=0.21.0" >> requirements-dev.txt
```

### 3. 目录结构不完整
```bash
# 创建前端测试目录
mkdir -p frontend/src/tests/unit/{components,composables,utils,api,store}

# 创建后端测试目录  
mkdir -p backend/tests/unit/{api,models,services,core}
mkdir -p backend/tests/integration
```

### 4. 配置文件缺失
```bash
# 复制配置文件示例
cp frontend/.env.test.example frontend/.env.test
cp backend/.env.test.example backend/.env.test
```

## 🚀 完整验证流程

### 步骤1：基本环境验证
```bash
# 运行环境验证
python scripts/validate-test-environment.py

# 如果失败，按照建议修复
```

### 步骤2：测试数据准备
```bash
# 初始化测试数据
python scripts/init-test-data.py

# 检查数据是否创建成功
ls -la backend/test_data/
ls -la frontend/tests/fixtures/
```

### 步骤3：运行测试
```bash
# 运行完整测试套件
./scripts/run-all-tests.sh  # Linux/macOS
scripts\run-all-tests.bat   # Windows
```

### 步骤4：检查覆盖率
```bash
# 检查覆盖率阈值
python scripts/check-coverage-thresholds.py

# 如果覆盖率不足，添加更多测试用例
```

### 步骤5：生成报告
```bash
# 生成统一测试报告
python scripts/generate-test-report.py

# 报告位置：test-reports/
```

## 📊 验证标准

### 必须通过的项目
| 检查项 | 标准 | 优先级 |
|--------|------|--------|
| 前端依赖 | Vitest, Testing Library, Playwright | 高 |
| 后端依赖 | pytest, pytest-cov, pytest-asyncio | 高 |
| 测试目录 | 基本目录结构完整 | 中 |
| 配置文件 | vitest.config.js, pyproject.toml | 高 |
| CI/CD配置 | GitHub Actions工作流 | 中 |

### 建议通过的项目
| 检查项 | 标准 | 优先级 |
|--------|------|--------|
| 测试示例 | 有示例测试文件 | 低 |
| 覆盖率阈值 | 前端≥80%，后端≥80% | 中 |
| 测试脚本 | 所有脚本可执行 | 低 |

## 🛠️ 自动化验证

### GitHub Actions 集成
```yaml
# 在CI中添加验证步骤
- name: Validate Test Environment
  run: python scripts/validate-test-environment.py
  
- name: Check Coverage Thresholds
  run: python scripts/check-coverage-thresholds.py
```

### 本地开发钩子
```bash
# 在package.json中添加
"scripts": {
  "precommit": "python scripts/validate-test-environment.py"
}
```

## 🚨 故障排除

### 验证失败常见原因

1. **依赖未安装**
   ```
   前端: npm ci 或 npm install
   后端: pip install -r requirements-dev.txt
   ```

2. **配置文件缺失**
   ```
   # 检查关键文件
   ls frontend/vitest.config.js
   ls backend/pyproject.toml
   ```

3. **权限问题**
   ```
   # 设置脚本执行权限
   chmod +x scripts/*.sh
   ```

4. **环境变量未设置**
   ```
   # 复制环境文件
   cp .env.example .env.test
   ```

### 紧急修复流程
```bash
# 1. 检查依赖
cd frontend && npm list vitest
cd backend && pip list | grep pytest

# 2. 修复配置
python scripts/fix-test-config.py  # 如果有的话

# 3. 重新验证
python scripts/validate-test-environment.py
```

## 📈 持续改进

### 监控指标
- 验证通过率
- 覆盖率趋势
- 测试执行时间
- 环境配置一致性

### 定期检查
1. 每月运行完整验证
2. 更新测试依赖版本
3. 检查新的测试需求
4. 优化验证脚本

### 反馈机制
- 验证失败时生成详细报告
- 提供修复建议
- 记录验证历史
- 集成到开发工作流

---

**最后更新**: 2026-01-28  
**验证状态**: ✅ 验证脚本已就绪  
**下一步**: 运行 `python scripts/validate-test-environment.py` 验证环境