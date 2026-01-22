#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# 日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
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

# 显示帮助信息
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Available commands:"
    echo "  start       Start development environment"
    echo "  stop        Stop all services"
    echo "  status      Show service status"
    echo "  restart     Restart all services"
    echo "  logs        Show service logs"
    echo "  verify      Verify environment setup"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start all services"
    echo "  $0 status    # Check service status"
    echo "  $0 logs      # Show logs"
}

# 启动开发环境
start_env() {
    log "INFO" "Starting development environment..."
    
    # 检查环境
    if ! ./scripts/verify-env.sh; then
        log "ERROR" "Environment verification failed"
        exit 1
    fi
    
    # 启动服务
    if ! ./scripts/start-with-monitoring.sh; then
        log "ERROR" "Failed to start services"
        exit 1
    fi
    
    log "INFO" "Development environment started successfully"
}

# 停止所有服务
stop_env() {
    log "INFO" "Stopping development environment..."
    
    if ! ./scripts/stop-dev.sh; then
        log "ERROR" "Failed to stop services"
        exit 1
    fi
    
    log "INFO" "Development environment stopped successfully"
}

# 显示服务状态
show_status() {
    log "INFO" "Checking service status..."
    ./scripts/status.sh
}

# 重启所有服务
restart_env() {
    log "INFO" "Restarting development environment..."
    
    stop_env
    sleep 2
    start_env
}

# 显示日志
show_logs() {
    local service=${1:-"all"}
    
    case $service in
        "backend")
            tail -f logs/backend.log
            ;;
        "frontend")
            tail -f logs/frontend.log
            ;;
        "monitor")
            tail -f logs/monitor.log
            ;;
        "error")
            tail -f logs/error.log
            ;;
        "all")
            log "INFO" "Following all logs..."
            tail -f logs/*.log
            ;;
        *)
            log "ERROR" "Unknown service: $service"
            echo "Available services: backend, frontend, monitor, error, all"
            exit 1
            ;;
    esac
}

# 验证环境设置
verify_env() {
    log "INFO" "Verifying environment setup..."
    ./scripts/verify-env.sh
}

# 主函数
main() {
    local command=${1:-"help"}
    
    # 进入项目根目录
    cd "$PROJECT_ROOT"
    
    # 创建必要的目录
    mkdir -p logs
    mkdir -p data/{postgres,redis,rabbitmq,mongodb,elasticsearch}
    
    case $command in
        "start")
            start_env
            ;;
        "stop")
            stop_env
            ;;
        "status")
            show_status
            ;;
        "restart")
            restart_env
            ;;
        "logs")
            show_logs ${2:-"all"}
            ;;
        "verify")
            verify_env
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log "ERROR" "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"