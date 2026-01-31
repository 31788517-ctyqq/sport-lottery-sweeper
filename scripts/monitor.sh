#!/bin/bash

# =============================================================================
# 体育彩票扫盘系统监控脚本
# 监控系统状态、服务健康和性能指标
# =============================================================================

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置
LOG_FILE="/var/log/sport-lottery-monitor.log"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEMORY=85
ALERT_THRESHOLD_DISK=90
WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@sport-lottery-sweeper.com}"

# 日志函数
log_message() {
    local level=$1
    shift
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') [$level] $*" | tee -a "$LOG_FILE"
}

send_alert() {
    local message="$1"
    local severity="$2"
    
    # Slack通知
    if [[ -n "$WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[$severity] Sport Lottery Monitor Alert: $message\"}" \
            "$WEBHOOK_URL" || true
    fi
    
    # 邮件通知
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "[$severity] Sport Lottery Monitor Alert" "$ADMIN_EMAIL" || true
    fi
    
    log_message "ALERT" "$message"
}

# 系统资源检查
check_system_resources() {
    log_message "INFO" "检查系统资源..."
    
    # CPU使用率
    local cpu_usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d',' -f1)
    cpu_usage=${cpu_usage%.*}  # 移除小数部分
    
    if [[ $cpu_usage -gt $ALERT_THRESHOLD_CPU ]]; then
        send_alert "CPU使用率过高: ${cpu_usage}%" "WARNING"
    else
        log_message "INFO" "CPU使用率正常: ${cpu_usage}%"
    fi
    
    # 内存使用率
    local memory_info
    memory_info=$(free | grep Mem)
    local total_mem used_mem available_mem memory_usage
    total_mem=$(echo $memory_info | awk '{print $2}')
    used_mem=$(echo $memory_info | awk '{print $3}')
    available_mem=$(echo $memory_info | awk '{print $7}')
    memory_usage=$((used_mem * 100 / total_mem))
    
    if [[ $memory_usage -gt $ALERT_THRESHOLD_MEMORY ]]; then
        send_alert "内存使用率过高: ${memory_usage}%" "WARNING"
    else
        log_message "INFO" "内存使用率正常: ${memory_usage}%"
    fi
    
    # 磁盘使用率
    local disk_usage
    disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    if [[ $disk_usage -gt $ALERT_THRESHOLD_DISK ]]; then
        send_alert "磁盘使用率过高: ${disk_usage}%" "CRITICAL"
    else
        log_message "INFO" "磁盘使用率正常: ${disk_usage}%"
    fi
}

# Docker容器检查
check_docker_containers() {
    log_message "INFO" "检查Docker容器状态..."
    
    local containers unhealthy_containers
    containers=$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}")
    unhealthy_containers=$(echo "$containers" | grep -v "Up " || true)
    
    if [[ -n "$unhealthy_containers" ]]; then
        send_alert "发现不健康的容器:\n$unhealthy_containers" "CRITICAL"
    else
        log_message "INFO" "所有容器运行正常"
    fi
    
    # 检查容器资源使用
    echo "$containers" | tail -n +2 | while read -r line; do
        local container_name status image
        container_name=$(echo "$line" | awk '{print $1}')
        status=$(echo "$line" | awk '{print $2}')
        image=$(echo "$line" | awk '{print $3}')
        
        # 获取容器统计信息
        local stats
        stats=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" | grep "$container_name" || true)
        
        if [[ -n "$stats" ]]; then
            log_message "INFO" "容器 $container_name ($image): $status - $stats"
        fi
    done
}

# 应用健康检查
check_application_health() {
    log_message "INFO" "检查应用健康状态..."
    
    local endpoints=(
        "http://localhost:8000/health/live:Backend Live"
        "http://localhost:8000/health/ready:Backend Ready"
        "http://localhost:8000/api/v1/health:API Health"
        "http://localhost:3000/health:Frontend Health"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        local url desc
        url=$(echo "$endpoint_info" | cut -d':' -f1)
        desc=$(echo "$endpoint_info" | cut -d':' -f2)
        
        local response_code response_time
        response_time=$(date +%s%N)
        response_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --max-time 30 "$url" || echo "000")
        response_time=$((( $(date +%s%N) - response_time ) / 1000000))
        
        if [[ "$response_code" == "200" ]]; then
            log_message "INFO" "$desc: ✓ 正常 (${response_time}ms)"
        else
            send_alert "$desc 检查失败: HTTP $response_code (${response_time}ms)" "ERROR"
        fi
    done
}

# 数据库连接检查
check_database_connection() {
    log_message "INFO" "检查数据库连接..."
    
    # 检查PostgreSQL
    if docker exec postgres pg_isready -U sport_user &>/dev/null; then
        log_message "INFO" "PostgreSQL连接正常"
        
        # 检查活跃连接数
        local active_connections
        active_connections=$(docker exec postgres psql -U sport_user -d sport_lottery_prod -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';" | tr -d ' ')
        
        if [[ $active_connections -gt 50 ]]; then
            send_alert "数据库连接数过多: $active_connections" "WARNING"
        else
            log_message "INFO" "数据库连接数正常: $active_connections"
        fi
    else
        send_alert "PostgreSQL连接失败" "CRITICAL"
    fi
    
    # 检查Redis
    if docker exec redis redis-cli ping &>/dev/null; then
        log_message "INFO" "Redis连接正常"
        
        # 检查内存使用
        local redis_memory
        redis_memory=$(docker exec redis redis-cli info memory | grep used_memory_human | cut -d':' -f2 | tr -d '\r')
        log_message "INFO" "Redis内存使用: $redis_memory"
    else
        send_alert "Redis连接失败" "CRITICAL"
    fi
}

# 日志错误检查
check_log_errors() {
    log_message "INFO" "检查应用日志错误..."
    
    local error_patterns=(
        "ERROR:FATAL:CRITICAL"
        "Exception:Traceback:"
        "500 Internal Server Error"
        "Connection refused"
        "Database connection failed"
    )
    
    for pattern in "${error_patterns[@]}"; do
        local error_count
        error_count=$(docker-compose logs --since="5 minutes ago" 2>/dev/null | grep -i -E "$pattern" | wc -l || echo "0")
        
        if [[ $error_count -gt 0 ]]; then
            send_alert "发现 $error_count 个错误日志 (模式: $pattern)" "WARNING"
        fi
    done
}

# 性能指标收集
collect_metrics() {
    log_message "INFO" "收集性能指标..."
    
    # 应用指标
    if curl -s http://localhost:8000/metrics &>/dev/null; then
        local metrics
        metrics=$(curl -s http://localhost:8000/metrics | grep -E "(http_requests_total|http_request_duration_seconds|database_queries_total)" | head -10)
        log_message "INFO" "应用指标:\n$metrics"
    fi
    
    # 系统负载
    local load_avg
    load_avg=$(uptime | awk -F'load average:' '{print $2}')
    log_message "INFO" "系统负载: $load_avg"
    
    # 网络统计
    local network_stats
    network_stats=$(cat /proc/net/dev | grep -E "(eth0|ens|enp)" | head -1)
    log_message "INFO" "网络统计: $network_stats"
}

# 备份状态检查
check_backup_status() {
    log_message "INFO" "检查备份状态..."
    
    local backup_dir="/app/backups"
    if [[ -d "$backup_dir" ]]; then
        local latest_backup
        latest_backup=$(find "$backup_dir" -name "*.sql" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
        
        if [[ -n "$latest_backup" ]]; then
            local backup_age_days
            backup_age_days=$(( ($(date +%s) - $(stat -c %Y "$latest_backup")) / 86400 ))
            
            if [[ $backup_age_days -gt 1 ]]; then
                send_alert "备份文件过旧: $(basename "$latest_backup") ($backup_age_days 天前)" "WARNING"
            else
                log_message "INFO" "最新备份正常: $(basename "$latest_backup") (${backup_age_days} 天前)"
            fi
        else
            send_alert "未找到备份文件" "CRITICAL"
        fi
    fi
}

# 生成监控报告
generate_report() {
    local report_file="/tmp/monitor-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
================================================================================
体育彩票扫盘系统监控报告
生成时间: $(date)
系统信息: $(uname -a)

=== 系统资源 ===
CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
内存使用: $(free -h | grep Mem)
磁盘使用: $(df -h / | tail -1)
系统负载: $(uptime)

=== Docker容器状态 ===
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}")

=== 应用健康状态 ===
Backend Live: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/live || echo "Failed")
Backend Ready: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ready || echo "Failed")
API Health: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health || echo "Failed")
Frontend Health: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health || echo "Failed")

=== 数据库连接 ===
PostgreSQL: $(docker exec postgres pg_isready -U sport_user &>/dev/null && echo "Connected" || echo "Failed")
Redis: $(docker exec redis redis-cli ping &>/dev/null && echo "Connected" || echo "Failed")

=== 最近错误日志 ===
$(docker-compose logs --since="10 minutes ago" 2>/dev/null | grep -i -E "(ERROR|FATAL|CRITICAL|Exception)" | tail -5 || echo "No recent errors")

================================================================================
EOF

    log_message "INFO" "监控报告已生成: $report_file"
    
    # 如果配置了邮件，发送报告
    if command -v mail &> /dev/null && [[ -n "$ADMIN_EMAIL" ]]; then
        mail -s "Sport Lottery Monitor Report - $(date +%Y-%m-%d)" "$ADMIN_EMAIL" < "$report_file" || true
    fi
}

# 主监控函数
main_monitor() {
    local mode=${1:-full}
    
    log_message "INFO" "开始监控检查 (模式: $mode)"
    
    case "$mode" in
        "quick")
            check_application_health
            ;;
        "resources")
            check_system_resources
            ;;
        "containers")
            check_docker_containers
            ;;
        "database")
            check_database_connection
            ;;
        "logs")
            check_log_errors
            ;;
        "full")
            check_system_resources
            check_docker_containers
            check_application_health
            check_database_connection
            check_log_errors
            collect_metrics
            check_backup_status
            generate_report
            ;;
        *)
            log_message "ERROR" "未知监控模式: $mode"
            exit 1
            ;;
    esac
    
    log_message "INFO" "监控检查完成"
}

# 信号处理
trap 'log_message "INFO" "监控脚本被中断"; exit 0' INT TERM

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_monitor "${1:-full}"
fi