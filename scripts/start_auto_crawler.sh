#!/bin/bash

# 500彩票网自动爬虫启动脚本

echo "🚀 启动500彩票网自动爬虫系统..."

# 检查Redis是否运行
echo "📋 检查Redis连接..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis未运行，请先启动Redis"
    echo "   可以使用: redis-server"
    exit 1
fi
echo "✅ Redis连接正常"

# 启动Celery Worker
echo "👷 启动Celery Worker..."
celery -A backend.tasks.celery_schedule worker --loglevel=info --queues=crawler,monitor &
WORKER_PID=$!
echo "   Worker PID: $WORKER_PID"

# 启动Celery Beat (定时任务调度器)
echo "⏰ 启动Celery Beat..."
celery -A backend.tasks.celery_schedule beat --loglevel=info &
BEAT_PID=$!
echo "   Beat PID: $BEAT_PID"

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 测试立即执行一次抓取
echo "🧪 测试执行一次抓取..."
celery -A backend.tasks.celery_schedule call tasks.500wang.fetch_daily_matches

echo ""
echo "✅ 自动爬虫系统启动完成！"
echo "   Worker PID: $WORKER_PID"
echo "   Beat PID: $BEAT_PID"
echo ""
echo "📊 定时任务计划:"
echo "   - 每日08:00: 抓取3天赛程"
echo "   - 每小时整点: 更新最新数据" 
echo "   - 每30分钟: 健康检查"
echo ""
echo "🔧 管理命令:"
echo "   - 查看任务: celery -A backend.tasks.celery_schedule inspect active"
echo "   - 停止系统: kill $WORKER_PID $BEAT_PID"
echo "   - 手动执行: celery -A backend.tasks.celery_schedule call tasks.500wang.fetch_daily_matches"

# 等待用户输入以保持进程运行
wait