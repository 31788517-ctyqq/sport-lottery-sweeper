#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志文件
STATUS_LOG="logs/status.log"

# 创建日志目录
mkdir -p logs

# 记录日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    # 写入日志文件
    echo "[$timestamp] [$level] $message" >> $STATUS_LOG
    
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

# 检查Docker容器状态
check_docker_containers() {
    log "INFO" "=== Docker Containers Status ==="
    
    local containers=("db" "redis" "rabbitmq" "mongodb" "elasticsearch")
    
    for container in "${containers[@]}"; do
        local container_id=$(docker-compose -f docker-compose.dev.yml ps -q $container)
        if [ -n "$container_id" ]; then
            local status=$(docker inspect -f '{{.State.Status}}' $container_id 2>/dev/null || echo "unknown")
            local health=$(docker inspect -f '{{.State.Health.Status}}' $container_id 2>/dev/null || echo "unknown")
            
            case $status in
                "running")
                    if [ "$health" = "healthy" ]; then
                        log "INFO" "$container: Running (Healthy)"
                    else
                        log "WARNING" "$container: Running (Health: $health)"
                    fi
                    ;;
                "exited")
                    log "ERROR" "$container: Stopped"
                    ;;
                *)
                    log "ERROR" "$container: Unknown status ($status)"
                    ;;
            esac
        else
            log "ERROR" "$container: Not found"
        fi
    done
}

# 检查应用服务状态
check_app_services() {
    log "INFO" "=== Application Services Status ==="
    
    # 检查后端服务
    if [ -f "logs/backend.pid" ]; then
        local backend_pid=$(cat logs/backend.pid)
        if kill -0 $backend_pid 2>/dev/null; then
            if curl -f http://localhost:8000/health > /dev/null 2>&1; then
                log "INFO" "Backend: Running (PID: $backend_pid)"
            else
                log "WARNING" "Backend: Running but not responding (PID: $backend_pid)"
            fi
        else
            log "ERROR" "Backend: Not running (stale PID file)"
        fi
    else
        log "ERROR" "Backend: Not running (no PID file)"
    fi
    
    # 检查前端服务
    if [ -f "logs/frontend.pid" ]; then
        local frontend_pid=$(cat logs/frontend.pid)
        if kill -0 $frontend_pid 2>/dev/null; then
            if curl -f http://localhost:3000 > /dev/null 2>&1; then
                log "INFO" "Frontend: Running (PID: $frontend_pid)"
            else
                log "WARNING" "Frontend: Running but not responding (PID: $frontend_pid)"
            fi
        else
            log "ERROR" "Frontend: Not running (stale PID file)"
        fi
    else
        log "ERROR" "Frontend: Not running (no PID file)"
    fi
    
    # 检查监控服务
    if [ -f "logs/monitor.pid" ]; then
        local monitor_pid=$(cat logs/monitor.pid)
        if kill -0 $monitor_pid 2>/dev/null; then
            log "INFO" "Monitor: Running (PID: $monitor_pid)"
        else
            log "ERROR" "Monitor: Not running (stale PID file)"
        fi
    else
        log "ERROR" "Monitor: Not running (no PID file)"
    fi
}

# 检查端口占用
check_ports() {
    log "INFO" "=== Port Usage ==="
    
    local ports=("5432:PostgreSQL" "6379:Redis" "5672:RabbitMQ" "27017:MongoDB" "9200:Elasticsearch" "8000:Backend" "3000:Frontend")
    
    for port_info in "${ports[@]}"; do
        local port=$(echo $port_info | cut -d: -f1)
        local service=$(echo $port_info | cut -d: -f2)
        
        if lsof -i :$port -sTCP:LISTEN > /dev/null 2>&1; then
            local pid=$(lsof -ti :$port)
            log "INFO" "$service: Port $port (PID: $pid)"
        else
            log "ERROR" "$service: Port $port not in use"
        fi
    done
}

# 检查资源使用情况
check_resources() {
    log "INFO" "=== Resource Usage ==="
    
    # CPU使用率
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    log "INFO" "CPU Usage: ${cpu_usage}%"
    
    # 内存使用情况
    local mem_info=$(free -m | grep "Mem")
    local total_mem=$(echo $mem_info | awk '{print $2}')
    local used_mem=$(echo $mem_info | awk '{print $3}')
    local mem_usage=$(echo "scale=2; $used_mem * 100 / $total_mem" | bc)
    log "INFO" "Memory: ${used_mem}MB/${total_mem}MB (${mem_usage}%)"
    
    # 磁盘使用情况
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}')
    local disk_free=$(df -h / | awk 'NR==2 {print $4}')
    log "INFO" "Disk: Used $disk_usage (Free $disk_free)"
    
    # Docker容器资源使用
    log "DETAIL" "=== Docker Container Resources ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || \
        log "WARNING" "Failed to get container resource usage"
}

# 检查最近的日志
check_recent_logs() {
    log "INFO" "=== Recent Log Entries ==="
    
    local logs=("backend.log" "frontend.log" "monitor.log")
    
    for log_file in "${logs[@]}"; do
        if [ -f "logs/$log_file" ] && [ -s "logs/$log_file" ]; then
            log "DETAIL" "Last 5 lines from $log_file:"
            tail -5 logs/$log_file | while read line; do
                log "DETAIL" "$line"
            done
            echo
        else
            log "WARNING" "Log file $log_file not found or empty"
        fi
    done
}

# 检查最近的错误
check_recent_errors() {
    log "INFO" "=== Recent Error Log Entries ==="
    
    if [ -f "logs/error.log" ] && [ -s "logs/error.log" ]; then
        log "DETAIL" "Last 5 error entries:"
        grep "ERROR" logs/error.log | tail -5 | while read line; do
            log "DETAIL" "$line"
        done
    else
        log "INFO" "No recent errors found"
    fi
}

# 主函数
main() {
    log "INFO" "=== Soccer Scanning System Status Report ==="
    log "INFO" "Report generated at: $(date)"
    echo
    
    # 检查Docker容器状态
    check_docker_containers
    echo
    
    # 检查应用服务状态
    check_app_services
    echo
    
    # 检查端口使用情况
    check_ports
    echo
    
    # 检查资源使用情况
    check_resources
    echo
    
    # 检查最近的日志
    check_recent_logs
    echo
    
    # 检查最近的错误
    check_recent_errors
}

# 执行主函数
main "$@"