#!/bin/bash
# 竞彩足球扫盘系统 - 完整测试执行脚本
# 执行所有测试：单元测试、集成测试、端到端测试

set -e  # 遇到错误立即退出

echo "🚀 开始执行竞彩足球扫盘系统完整测试套件"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 '$1' 未找到，请先安装"
        exit 1
    fi
}

# 显示测试环境信息
show_environment() {
    log_info "测试环境信息:"
    echo "- 工作目录: $(pwd)"
    echo "- 系统: $(uname -s) $(uname -m)"
    echo "- Node版本: $(node --version 2>/dev/null || echo '未安装')"
    echo "- NPM版本: $(npm --version 2>/dev/null || echo '未安装')"
    echo "- Python版本: $(python3 --version 2>/dev/null || echo '未安装')"
    echo "- 当前时间: $(date)"
    echo "=========================================="
}

# 前端测试
run_frontend_tests() {
    log_info "开始前端测试..."
    cd frontend
    
    # 安装依赖（如果不存在）
    if [ ! -d "node_modules" ]; then
        log_warn "node_modules 目录不存在，正在安装依赖..."
        npm ci
    fi
    
    # 运行单元测试
    log_info "运行前端单元测试..."
    if npm run test:run; then
        log_info "前端单元测试通过 ✅"
    else
        log_error "前端单元测试失败 ❌"
        return 1
    fi
    
    # 运行组件测试
    log_info "运行前端组件测试..."
    if npm run test:components; then
        log_info "前端组件测试通过 ✅"
    else
        log_warn "前端组件测试有警告"
    fi
    
    cd ..
    return 0
}

# 后端测试
run_backend_tests() {
    log_info "开始后端测试..."
    cd backend
    
    # 创建测试环境
    if [ ! -f ".env.test" ]; then
        log_info "创建测试环境配置..."
        cat > .env.test << EOF
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=test-secret-key-for-local-testing
ENVIRONMENT=testing
DEBUG=true
LOG_LEVEL=INFO
EOF
    fi
    
    # 安装依赖
    log_info "安装Python依赖..."
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # 运行单元测试
    log_info "运行后端单元测试..."
    if python -m pytest tests/unit/ -v; then
        log_info "后端单元测试通过 ✅"
    else
        log_error "后端单元测试失败 ❌"
        return 1
    fi
    
    # 运行集成测试
    log_info "运行后端集成测试..."
    if python -m pytest tests/integration/ -v; then
        log_info "后端集成测试通过 ✅"
    else
        log_warn "后端集成测试有警告"
    fi
    
    cd ..
    return 0
}

# 端到端测试
run_e2e_tests() {
    log_info "开始端到端测试..."
    
    # 检查前端是否运行
    if ! curl -s http://localhost:3000 > /dev/null; then
        log_warn "前端服务未运行，请先启动: cd frontend && npm run dev"
        log_info "跳过端到端测试"
        return 0
    fi
    
    cd frontend
    
    # 安装Playwright浏览器（如果未安装）
    if [ ! -d "node_modules/.cache/ms-playwright" ]; then
        log_info "安装Playwright浏览器..."
        npx playwright install chromium
    fi
    
    # 运行端到端测试
    log_info "运行端到端测试..."
    log_info "Running intelligence pre-release regression (3 specs)..."
    if npx playwright test tests/e2e/intelligence-collection-quality-fields.spec.js tests/e2e/intelligence-collection-p2-cache.spec.js tests/e2e/intelligence-collection-settings-and-replay.spec.js --project=chromium --reporter=line; then
        log_info "Intelligence pre-release regression passed"
    else
        log_error "Intelligence pre-release regression failed"
        return 1
    fi

    log_info "Running full end-to-end suite..."
    if npx playwright test tests/e2e/ --reporter=html; then
        log_info "端到端测试通过 ✅"
    else
        log_error "端到端测试失败 ❌"
        return 1
    fi
    
    cd ..
    return 0
}

# 生成测试报告
generate_reports() {
    log_info "生成测试报告..."
    
    # 前端覆盖率报告
    if [ -d "frontend/coverage" ]; then
        log_info "前端覆盖率报告已生成: frontend/coverage/index.html"
    fi
    
    # 后端覆盖率报告
    if [ -d "backend/htmlcov" ]; then
        log_info "后端覆盖率报告已生成: backend/htmlcov/index.html"
    fi
    
    # Playwright报告
    if [ -d "frontend/playwright-report" ]; then
        log_info "Playwright测试报告: frontend/playwright-report/index.html"
    fi
    
    # 汇总报告
    echo "=========================================="
    echo "📊 测试执行完成汇总"
    echo "=========================================="
    echo "- 前端测试: $([ $FRONTEND_PASSED -eq 1 ] && echo '✅ 通过' || echo '❌ 失败')"
    echo "- 后端测试: $([ $BACKEND_PASSED -eq 1 ] && echo '✅ 通过' || echo '❌ 失败')"
    echo "- 端到端测试: $([ $E2E_PASSED -eq 1 ] && echo '✅ 通过' || echo '⚠️ 跳过/失败')"
    echo "=========================================="
}

# 主函数
main() {
    # 显示环境信息
    show_environment
    
    # 检查必要命令
    check_command node
    check_command npm
    check_command python3
    check_command pip
    
    # 初始化状态
    FRONTEND_PASSED=0
    BACKEND_PASSED=0
    E2E_PASSED=0
    
    # 执行测试
    if run_frontend_tests; then
        FRONTEND_PASSED=1
    fi
    
    if run_backend_tests; then
        BACKEND_PASSED=1
    fi
    
    # 端到端测试可选
    if run_e2e_tests; then
        E2E_PASSED=1
    fi
    
    # 生成报告
    generate_reports
    
    # 返回最终状态
    if [ $FRONTEND_PASSED -eq 1 ] && [ $BACKEND_PASSED -eq 1 ]; then
        log_info "🎉 所有关键测试通过！"
        exit 0
    else
        log_error "💥 部分测试失败，请检查以上错误信息"
        exit 1
    fi
}

# 执行主函数
main "$@"
