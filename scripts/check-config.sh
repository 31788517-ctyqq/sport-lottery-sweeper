#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志文件
CONFIG_CHECK_LOG="logs/config-check.log"

# 创建日志目录
mkdir -p logs

# 记录日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    # 写入日志文件
    echo "[$timestamp] [$level] $message" >> $CONFIG_CHECK_LOG
    
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

# 检查环境变量文件
check_env_file() {
    log "INFO" "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.development" ]; then
            cp .env.development .env
            log "INFO" "Created .env from .env.development"
        elif [ -f ".env.example" ]; then
            cp .env.example .env
            log "WARNING" "Created .env from .env.example, please review settings"
        else
            log "ERROR" "No environment configuration file found"
            return 1
        fi
    fi
    
    # 检查必需的环境变量
    local required_vars=(
        "DB_HOST"
        "DB_PORT"
        "DB_USER"
        "DB_PASSWORD"
        "DB_NAME"
        "REDIS_HOST"
        "REDIS_PORT"
        "SECRET_KEY"
        "API_V1_STR"
    )
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env; then
            log "ERROR" "Missing required environment variable: $var"
        else
            log "INFO" "Environment variable $var is set"
        fi
    done
    
    return 0
}

# 检查目录结构
check_directories() {
    log "INFO" "Checking directory structure..."
    
    local required_dirs=(
        "backend"
        "frontend"
        "scripts"
        "config"
        "docs"
        "logs"
        "data"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            log "INFO" "Directory $dir exists"
        else
            log "WARNING" "Directory $dir is missing, creating..."
            mkdir -p "$dir"
        fi
    done
    
    # 检查数据目录
    local data_dirs=(
        "data/postgres"
        "data/redis"
        "data/rabbitmq"
        "data/mongodb"
        "data/elasticsearch"
    )
    
    for dir in "${data_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log "INFO" "Created data directory: $dir"
        fi
    done
    
    return 0
}

# 检查配置文件
check_config_files() {
    log "INFO" "Checking configuration files..."
    
    local config_files=(
        "config/nginx.conf"
        "config/prometheus.yml"
        "docker-compose.yml"
        "docker-compose.dev.yml"
        ".env"
    )
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            log "INFO" "Configuration file $file exists"
        else
            log "WARNING" "Configuration file $file is missing"
        fi
    done
    
    # 检查后端配置
    if [ -f "backend/alembic.ini" ]; then
        log "INFO" "Backend Alembic configuration exists"
    else
        log "ERROR" "Backend Alembic configuration is missing"
    fi
    
    # 检查前端配置
    if [ -f "frontend/vite.config.js" ]; then
        log "INFO" "Frontend Vite configuration exists"
    else
        log "ERROR" "Frontend Vite configuration is missing"
    fi
    
    return 0
}

# 检查脚本文件
check_scripts() {
    log "INFO" "Checking script files..."
    
    local scripts=(
        "scripts/start-dev.sh"
        "scripts/stop-dev.sh"
        "scripts/status.sh"
        "scripts/monitor-services.sh"
        "scripts/start-with-monitoring.sh"
        "scripts/check-requirements.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            if [ -x "$script" ]; then
                log "INFO" "Script $script exists and is executable"
            else
                log "WARNING" "Script $script exists but is not executable"
                chmod +x "$script"
            fi
        else
            log "ERROR" "Script $script is missing"
        fi
    done
    
    return 0
}

# 检查依赖
check_dependencies() {
    log "INFO" "Checking dependencies..."
    
    # 检查Python依赖
    if [ -f "backend/requirements.txt" ]; then
        log "INFO" "Backend requirements.txt exists"
        if command -v pip3 &> /dev/null; then
            log "INFO" "pip3 is available"
        else
            log "ERROR" "pip3 is not available"
        fi
    else
        log "ERROR" "Backend requirements.txt is missing"
    fi
    
    # 检查Node.js依赖
    if [ -f "frontend/package.json" ]; then
        log "INFO" "Frontend package.json exists"
        if command -v npm &> /dev/null; then
            log "INFO" "npm is available"
        else
            log "ERROR" "npm is not available"
        fi
    else
        log "ERROR" "Frontend package.json is missing"
    fi
    
    return 0
}

# 检查端口配置
check_ports() {
    log "INFO" "Checking port configuration..."
    
    local ports=(
        "5432:PostgreSQL"
        "6379:Redis"
        "5672:RabbitMQ"
        "27017:MongoDB"
        "9200:Elasticsearch"
        "8000:Backend API"
        "3000:Frontend"
    )
    
    for port_info in "${ports[@]}"; do
        local port=$(echo $port_info | cut -d: -f1)
        local service=$(echo $port_info | cut -d: -f2)
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log "WARNING" "Port $port ($service) is already in use"
        else
            log "INFO" "Port $port ($service) is available"
        fi
    done
    
    return 0
}

# 生成配置报告
generate_report() {
    local report_file="logs/config-report.txt"
    
    log "INFO" "Generating configuration report..."
    
    {
        echo "=== Configuration Report ==="
        echo "Generated at: $(date)"
        echo ""
        echo "=== Environment Variables ==="
        cat .env | grep -v "^#" | sort
        echo ""
        echo "=== Docker Configuration ==="
        docker-compose -f docker-compose.dev.yml config 2>/dev/null || echo "Docker Compose configuration not available"
        echo ""
        echo "=== Network Configuration ==="
        ip addr show | grep "inet " | grep -v 127.0.0.1
        echo ""
        echo "=== System Information ==="
        uname -a
        echo ""
        echo "=== Disk Usage ==="
        df -h
        echo ""
        echo "=== Memory Usage ==="
        free -h
        echo ""
        echo "=== CPU Information ==="
        lscpu
    } > $report_file
    
    log "INFO" "Configuration report generated: $report_file"
}

# 主函数
main() {
    log "INFO" "Starting configuration check..."
    
    # 检查环境变量
    check_env_file || return 1
    
    # 检查目录结构
    check_directories || return 1
    
    # 检查配置文件
    check_config_files || return 1
    
    # 检查脚本文件
    check_scripts || return 1
    
    # 检查依赖
    check_dependencies || return 1
    
    # 检查端口配置
    check_ports || return 1
    
    # 生成配置报告
    generate_report
    
    log "INFO" "Configuration check completed"
    log "INFO" "Check logs/config-report.txt for detailed information"
}

# 执行主函数
main