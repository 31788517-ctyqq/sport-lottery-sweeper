#!/bin/bash

# =============================================================================
# 体育彩票扫盘系统部署脚本
# 支持多环境部署：development, staging, production
# =============================================================================

set -euo pipefail  # 严格模式

# 颜色输出定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认值
ENVIRONMENT="development"
BUILD_FLAG=false
ROLLBACK_FLAG=false
VERSION="latest"
SKIP_TESTS=false
VERBOSE=false

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 帮助信息
usage() {
    cat << EOF
使用方法: $0 [选项]

选项:
    -e, --environment ENV     部署环境 (development|staging|production) [默认: development]
    -b, --build              构建新的Docker镜像
    -r, --rollback VERSION   回滚到指定版本
    -v, --version VERSION    指定版本标签 [默认: latest]
    -s, --skip-tests         跳过测试阶段
    --verbose                详细输出
    -h, --help               显示此帮助信息

示例:
    $0 -e staging -b                    # 构建并部署到staging环境
    $0 -e production -v v1.2.3         # 部署指定版本到生产环境
    $0 -e production -r v1.2.2          # 回滚到指定版本
    $0 -e development --skip-tests      # 跳过测试部署到开发环境

EOF
}

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--build)
            BUILD_FLAG=true
            shift
            ;;
        -r|--rollback)
            ROLLBACK_FLAG=true
            VERSION="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -s|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "未知选项: $1"
            usage
            exit 1
            ;;
    esac
done

# 验证环境参数
validate_environment() {
    case "$ENVIRONMENT" in
        development|staging|production)
            ;;
        *)
            log_error "无效的环境: $ENVIRONMENT"
            log_error "支持的环境: development, staging, production"
            exit 1
            ;;
    esac
}

# 检查必要工具
check_dependencies() {
    local deps=("docker" "docker-compose" "git" "curl")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "缺少必要工具: $dep"
            exit 1
        fi
    done
    
    # 检查Docker是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker未运行或无法连接"
        exit 1
    fi
}

# 检查Git状态
check_git_status() {
    log_info "检查Git仓库状态..."
    
    if [[ ! -d ".git" ]]; then
        log_error "当前目录不是Git仓库"
        exit 1
    fi
    
    # 检查是否有未提交的更改
    if [[ -n $(git status --porcelain) ]]; then
        log_warn "检测到未提交的更改"
        git status --short
        read -p "是否继续部署? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "部署已取消"
            exit 0
        fi
    fi
    
    # 拉取最新代码
    log_info "拉取最新代码..."
    git pull origin "${BRANCH:-main}"
}

# 运行测试
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_warn "跳过测试阶段"
        return 0
    fi
    
    log_info "运行测试套件..."
    
    # 后端测试
    log_info "运行后端测试..."
    cd backend
    if ! pip install -q -r requirements-dev.txt; then
        log_error "后端依赖安装失败"
        exit 1
    fi
    
    if ! pytest tests/unit/ tests/integration/ -v --tb=short; then
        log_error "后端测试失败"
        exit 1
    fi
    cd ..
    
    # 前端测试
    log_info "运行前端测试..."
    cd frontend
    if ! npm ci; then
        log_error "前端依赖安装失败"
        exit 1
    fi
    
    if ! npm run test:unit -- --run; then
        log_error "前端测试失败"
        exit 1
    fi
    cd ..
    
    log_success "所有测试通过"
}

# 构建镜像
build_images() {
    if [[ "$BUILD_FLAG" != "true" && "$ROLLBACK_FLAG" != "true" ]]; then
        log_info "跳过镜像构建"
        return 0
    fi
    
    log_info "构建Docker镜像..."
    
    # 构建后端镜像
    log_info "构建后端镜像..."
    if ! docker build -f Dockerfile.backend -t "sport-lottery-backend:$VERSION" .; then
        log_error "后端镜像构建失败"
        exit 1
    fi
    
    # 构建前端镜像
    log_info "构建前端镜像..."
    if ! docker build -f Dockerfile.frontend -t "sport-lottery-frontend:$VERSION" .; then
        log_error "前端镜像构建失败"
        exit 1
    fi
    
    log_success "镜像构建完成"
}

# 部署到指定环境
deploy_to_environment() {
    local compose_file="docker-compose.${ENVIRONMENT}.yml"
    
    if [[ ! -f "$compose_file" ]]; then
        log_error "找不到Compose文件: $compose_file"
        exit 1
    fi
    
    log_info "部署到 $ENVIRONMENT 环境..."
    
    # 备份当前配置
    if [[ -f "docker-compose.yml" ]]; then
        cp docker-compose.yml "docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 复制对应环境的Compose文件
    cp "$compose_file" docker-compose.yml
    
    # 拉取最新镜像
    log_info "拉取最新镜像..."
    docker-compose pull
    
    # 停止旧服务
    log_info "停止旧服务..."
    docker-compose down --remove-orphans
    
    # 启动新服务
    log_info "启动新服务..."
    if [[ "$ENVIRONMENT" == "production" ]]; then
        # 生产环境使用更安全的重启策略
        docker-compose up -d --build --force-recreate
    else
        docker-compose up -d --build
    fi
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 健康检查
    perform_health_check
}

# 健康检查
perform_health_check() {
    log_info "执行健康检查..."
    
    local max_retries=10
    local retry_count=0
    local health_url
    
    case "$ENVIRONMENT" in
        development)
            health_url="http://localhost:8000/health/live"
            ;;
        staging)
            health_url="https://staging.sport-lottery-sweeper.com/health/live"
            ;;
        production)
            health_url="https://sport-lottery-sweeper.com/health/live"
            ;;
    esac
    
    while [[ $retry_count -lt $max_retries ]]; do
        if curl -f -s "$health_url" &>/dev/null; then
            log_success "健康检查通过"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        log_warn "健康检查失败，$retry_count/$max_retries 次重试..."
        sleep 10
    done
    
    log_error "健康检查失败，部署可能有问题"
    
    # 显示容器日志
    log_info "显示容器日志..."
    docker-compose logs --tail=50
    
    exit 1
}

# 回滚操作
rollback_deployment() {
    log_info "回滚到版本: $VERSION"
    
    # 标记旧镜像
    docker tag "sport-lottery-backend:$VERSION" "sport-lottery-backend:rollback"
    docker tag "sport-lottery-frontend:$VERSION" "sport-lottery-frontend:rollback"
    
    # 更新Compose文件使用回滚版本
    sed -i.bak "s|sport-lottery-backend:.*|sport-lottery-backend:rollback|" docker-compose.yml
    sed -i.bak "s|sport-lottery-frontend:.*|sport-lottery-frontend:rollback|" docker-compose.yml
    
    # 重启服务
    docker-compose down --remove-orphans
    docker-compose up -d
    
    # 健康检查
    perform_health_check
    
    log_success "回滚完成"
}

# 清理资源
cleanup() {
    log_info "清理临时资源..."
    
    # 清理悬空镜像
    docker image prune -f
    
    # 清理未使用的容器
    docker container prune -f
    
    # 清理构建缓存
    docker builder prune -f
}

# 主函数
main() {
    log_info "开始部署流程"
    log_info "环境: $ENVIRONMENT"
    log_info "版本: $VERSION"
    log_info "构建: $BUILD_FLAG"
    log_info "回滚: $ROLLBACK_FLAG"
    log_info "跳过测试: $SKIP_TESTS"
    
    # 验证环境
    validate_environment
    
    # 检查依赖
    check_dependencies
    
    # Git状态检查
    check_git_status
    
    # 测试
    run_tests
    
    # 构建镜像
    build_images
    
    # 回滚或部署
    if [[ "$ROLLBACK_FLAG" == "true" ]]; then
        rollback_deployment
    else
        deploy_to_environment
    fi
    
    # 清理
    cleanup
    
    log_success "部署完成! 🚀"
    
    # 显示部署信息
    case "$ENVIRONMENT" in
        development)
            echo -e "\n${GREEN}开发环境访问地址:${NC}"
            echo -e "前端: ${BLUE}http://localhost:3000${NC}"
            echo -e "后端: ${BLUE}http://localhost:8000${NC}"
            echo -e "API文档: ${BLUE}http://localhost:8000/docs${NC}"
            ;;
        staging)
            echo -e "\n${GREEN}预发布环境访问地址:${NC}"
            echo -e "网站: ${BLUE}https://staging.sport-lottery-sweeper.com${NC}"
            ;;
        production)
            echo -e "\n${GREEN}生产环境访问地址:${NC}"
            echo -e "网站: ${BLUE}https://sport-lottery-sweeper.com${NC}"
            ;;
    esac
}

# 错误处理
trap 'log_error "部署过程中发生错误，退出码: $?"' ERR

# 运行主函数
main "$@"