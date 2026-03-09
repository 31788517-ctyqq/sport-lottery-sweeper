#!/bin/bash
# Docker 环境启动入口脚本
# 顺序执行：数据库迁移 → 种子数据导入 → 健康检查 → 启动服务

set -e  # 任何命令失败则退出

echo "========================================"
echo "[1/4] 执行数据库结构迁移..."
alembic upgrade head
if [ $? -ne 0 ]; then
    echo "❌ 数据库迁移失败，终止启动"
    exit 1
fi

echo "========================================"
echo "[2/4] 执行种子数据导入..."
python scripts/seed/seed_runner.py
if [ $? -ne 0 ]; then
    echo "❌ 种子数据导入失败，终止启动"
    exit 1
fi

echo "========================================"
echo "[3/4] 执行数据库健康检查..."
python scripts/health_check/db_health_check.py
if [ $? -ne 0 ]; then
    echo "❌ 数据库健康检查未通过，终止启动"
    exit 1
fi

echo "========================================"
echo "[4/4] 启动后端服务..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000