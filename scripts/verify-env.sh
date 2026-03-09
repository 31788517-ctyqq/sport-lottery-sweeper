#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志文件
VERIFY_LOG="logs/verify.log"

# 创建日志目录
mkdir -p logs

# 记录日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    # 写入日志文件
    echo "[$timestamp] [$level] $message" >> $VERIFY_LOG
    
    # 根据级别输出到控制台
    case $level in
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "INFO")
            echo -e "${GREEN}[INFO]${NC} $message"
            ;;
        "DETAIL")
            echo -e "${BLUE}[DETAIL]${NC} $message"
            ;;
    esac
}

# 验证Docker环境
verify_docker() {
    log "INFO" "=== Verifying Docker Environment ==="
    
    # 检查Docker是否安装
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker is not installed"
        return 1
    fi
    
    # 检查Docker Compose是否安装
    if ! command -v docker-compose &> /dev/null; then
        log "ERROR" "Docker Compose is not installed"
        return 1
    fi
    
    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        log "ERROR" "Docker daemon is not running"
        return 1
    fi
    
    log "INFO" "Docker environment verified"
    return 0
}

# 验证Python环境
verify_python() {
    log "INFO" "=== Verifying Python Environment ==="
    
    # 检查Python是否安装
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python 3 is not installed"
        return 1
    fi
    
    # 检查Python版本
    local python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
        log "ERROR" "Python 3.8 or higher is required, found $python_version"
        return 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log "ERROR" "pip3 is not installed"
        return 1
    fi
    
    # 检查虚拟环境
    if [ ! -d "backend/venv" ]; then
        log "WARNING" "Python virtual environment not found in backend/"
        return 1
    fi
    
    log "INFO" "Python environment verified (version $python_version)"
    return 0
}

# 验证Node.js环境
verify_nodejs() {
    log "INFO" "=== Verifying Node.js Environment ==="
    
    # 检查Node.js是否安装
    if ! command -v node &> /dev/null; then
        log "ERROR" "Node.js is not installed"
        return 1
    fi
    
    # 检查Node.js版本
    local node_version=$(node -v)
    if [[ $(echo "${node_version#v} < 16.0.0" | bc -l) -eq 1 ]]; then
        log "ERROR" "Node.js 16.0.0 or higher is required, found $node_version"
        return 1
    fi
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        log "ERROR" "npm is not installed"
        return 1
    fi
    
    # 检查node_modules
    if [ ! -d "frontend/node_modules" ]; then
        log "WARNING" "Node modules not found in frontend/"
        return 1
    fi
    
    log "INFO" "Node.js environment verified (version $node_version)"
    return 0
}

# 验证服务状态
verify_services() {
    log "INFO" "=== Verifying Service Status ==="
    
    # 检查基础服务
    local services=("db" "redis" "rabbitmq" "mongodb" "elasticsearch")
    
    for service in "${services[@]}"; do
        if docker-compose -f docker-compose.dev.yml ps -q $service > /dev/null; then
            local status=$(docker inspect -f '{{.State.Health.Status}}' \
                $(docker-compose -f docker-compose.dev.yml ps -q $service) 2>/dev/null || echo "unknown")
            if [ "$status" = "healthy" ]; then
                log "INFO" "$service is healthy"
            else
                log "WARNING" "$service status: $status"
            fi
        else
            log "ERROR" "$service is not running"
        fi
    done
    
    # 检查应用服务
    if [ -f "logs/backend.pid" ]; then
        local backend_pid=$(cat logs/backend.pid)
        if kill -0 $backend_pid 2>/dev/null; then
            if curl -f http://localhost:8000/health > /dev/null 2>&1; then
                log "INFO" "Backend service is healthy"
            else
                log "WARNING" "Backend service is running but not responding"
            fi
        else
            log "ERROR" "Backend service is not running"
        fi
    else
        log "ERROR" "Backend PID file not found"
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        local frontend_pid=$(cat logs/frontend.pid)
        if kill -0 $frontend_pid 2>/dev/null; then
            if curl -f http://localhost:3000 > /dev/null 2>&1; then
                log "INFO" "Frontend service is healthy"
            else
                log "WARNING" "Frontend service is running but not responding"
            fi
        else
            log "ERROR" "Frontend service is not running"
        fi
    else
        log "ERROR" "Frontend PID file not found"
    fi
}

# 验证配置文件
verify_configs() {
    log "INFO" "=== Verifying Configuration Files ==="
    
    # 检查环境变量文件
    if [ ! -f ".env" ]; then
        log "ERROR" ".env file not found"
        return 1
    fi
    
    # 检查Docker配置
    if [ ! -f "docker-compose.yml" ]; then
        log "ERROR" "docker-compose.yml not found"
    fi
    
    if [ ! -f "docker-compose.dev.yml" ]; then
        log "ERROR" "docker-compose.dev.yml not found"
    fi
    
    # 检查后端配置
    if [ ! -f "backend/alembic.ini" ]; then
        log "ERROR" "backend/alembic.ini not found"
    fi
    
    # 检查前端配置
    if [ ! -f "frontend/vite.config.js" ]; then
        log "ERROR" "frontend/vite.config.js not found"
    fi
    
    log "INFO" "Configuration files verified"
}

# 验证数据目录
verify_data_dirs() {
    log "INFO" "=== Verifying Data Directories ==="
    
    local dirs=("data/postgres" "data/redis" "data/rabbitmq" "data/mongodb" "data/elasticsearch")
    
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            log "INFO" "Directory $dir exists"
        else
            log "WARNING" "Directory $dir does not exist"
        fi
    done
}

# 生成验证报告
generate_report() {
    local report_file="logs/verify-report.txt"
    
    {
        echo "=== Environment Verification Report ==="
        echo "Generated at: $(date)"
        echo ""
        echo "=== System Information ==="
        uname -a
        echo ""
        echo "=== Docker Information ==="
        docker --version 2>/dev/null || echo "Docker not available"
        docker-compose --version 2>/dev/null || echo "Docker Compose not available"
        echo ""
        echo "=== Python Information ==="
        python3 --version 2>/dev/null || echo "Python 3 not available"
        pip3 --version 2>/dev/null || echo "pip3 not available"
        echo ""
        echo "=== Node.js Information ==="
        node --version 2>/dev/null || echo "Node.js not available"
        npm --version 2>/dev/null || echo "npm not available"
        echo ""
        echo "=== Service Status ==="
        docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "Docker Compose services not available"
        echo ""
        echo "=== Network Configuration ==="
        ip addr show | grep "inet " | grep -v 127.0.0.1
        echo ""
        echo "=== Environment Variables ==="
        cat .env | grep -v "^#" | sort
    } > $report_file
    
    log "INFO" "Verification report generated: $report_file"
}

# 主函数
main() {
    log "INFO" "Starting environment verification..."
    
    # 验证Docker环境
    verify_docker || exit 1
    
    # 验证Python环境
    verify_python || exit 1
    
    # 验证Node.js环境
    verify_nodejs || exit 1
    
    # 验证配置文件
    verify_configs || exit 1
    
    # 验证数据目录
    verify_data_dirs
    
    # 验证服务状态
    verify_services
    
    # 生成验证报告
    generate_report
    
    log "INFO" "Environment verification completed"
    log "INFO" "Check logs/verify-report.txt for detailed information"
}

# 执行主函数
main