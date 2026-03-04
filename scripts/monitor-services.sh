#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志文件
MONITOR_LOG="logs/monitor.log"
ERROR_LOG="logs/error.log"

# 创建日志目录
mkdir -p logs

# 记录日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    # 写入日志文件
    echo "[$timestamp] [$level] $message" >> $MONITOR_LOG
    
    # 根据级别输出到控制台
    case $level in
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message" | tee -a $ERROR_LOG
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "INFO")
            echo -e "${GREEN}[INFO]${NC} $message"
            ;;
    esac
}

# 检查服务状态
check_service() {
    local service=$1
    local port=$2
    local url=$3
    
    if [ -n "$port" ]; then
        if nc -z localhost $port; then
            log "INFO" "$service (port $port) is running"
            return 0
        else
            log "ERROR" "$service (port $port) is not accessible"
            return 1
        fi
    elif [ -n "$url" ]; then
        if curl -f $url > /dev/null 2>&1; then
            log "INFO" "$service is healthy"
            return 0
        else
            log "ERROR" "$service is not responding"
            return 1
        fi
    fi
}

# 检查Docker容器状态
check_docker_containers() {
    local containers=("db" "redis" "rabbitmq" "mongodb" "elasticsearch")
    
    log "INFO" "Checking Docker containers..."
    for container in "${containers[@]}"; do
        local status=$(docker inspect -f '{{.State.Health.Status}}' $(docker-compose -f docker-compose.dev.yml ps -q $container) 2>/dev/null || echo "unknown")
        if [ "$status" = "healthy" ]; then
            log "INFO" "Container $container is healthy"
        else
            log "ERROR" "Container $container status: $status"
        fi
    done
}

# 检查资源使用情况
check_resources() {
    log "INFO" "Checking system resources..."
    
    # CPU使用率
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    log "INFO" "CPU Usage: ${cpu_usage}%"
    
    # 内存使用率
    local mem_info=$(free -m | grep "Mem")
    local total_mem=$(echo $mem_info | awk '{print $2}')
    local used_mem=$(echo $mem_info | awk '{print $3}')
    local mem_usage=$(echo "scale=2; $used_mem * 100 / $total_mem" | bc)
    log "INFO" "Memory Usage: ${mem_usage}%"
    
    # 磁盘使用率
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}')
    log "INFO" "Disk Usage: $disk_usage"
}

# 检查日志文件大小
check_logs() {
    log "INFO" "Checking log files..."
    
    local logs=("backend.log" "frontend.log" "monitor.log")
    for log_file in "${logs[@]}"; do
        if [ -f "logs/$log_file" ]; then
            local size=$(du -h logs/$log_file | awk '{print $1}')
            log "INFO" "Log $log_file size: $size"
            
            # 如果日志文件过大，则轮转
            if [ $(stat -c%s "logs/$log_file") -gt 104857600 ]; then  # 100MB
                mv logs/$log_file logs/${log_file}.$(date +%Y%m%d_%H%M%S).old
                touch logs/$log_file
                log "WARNING" "Rotated log file $log_file"
            fi
        fi
    done
}

# 发送告警
send_alert() {
    local level=$1
    local message=$2
    
    # 这里可以集成邮件、短信、Webhook等告警方式
    log "ALERT" "$level: $message"
}

# 主监控循环
monitor_loop() {
    local interval=${1:-60}  # 默认60秒检查一次
    
    while true; do
        log "INFO" "Starting monitoring cycle..."
        
        # 检查Docker容器
        check_docker_containers
        
        # 检查服务
        check_service "Backend" 8000 "http://localhost:8000/health"
        check_service "Frontend" 3000 "http://localhost:3000"
        check_service "RabbitMQ Management" 15672
        check_service "Flower" 5555
        check_service "Elasticsearch" 9200
        check_service "Kibana" 5601
        check_service "Prometheus" 9090
        check_service "Grafana" 3001
        
        # 检查资源
        check_resources
        
        # 检查日志
        check_logs
        
        # 检查错误日志
        if [ -f "$ERROR_LOG" ] && [ -s "$ERROR_LOG" ]; then
            local error_count=$(wc -l < "$ERROR_LOG")
            if [ "$error_count" -gt 0 ]; then
                send_alert "ERROR" "Found $error_count errors in log"
            fi
        fi
        
        log "INFO" "Monitoring cycle completed. Next check in $interval seconds."
        sleep $interval
    done
}

# 主函数
main() {
    log "INFO" "Starting service monitoring..."
    
    # 设置信号处理
    trap 'log "INFO" "Stopping monitoring..."; exit 0' SIGINT SIGTERM
    
    # 开始监控循环
    monitor_loop $1
}

# 执行主函数
main $1