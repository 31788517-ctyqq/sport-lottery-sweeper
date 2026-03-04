#!/bin/bash

# Production Deployment Script for Sport Lottery Sweeper System
# =============================================================

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 开始部署生产环境..."

# 检查必要的环境变量
if [ -z "$SECRET_KEY" ]; then
    echo "❌ 错误: 未设置SECRET_KEY环境变量"
    echo "💡 提示: 请设置至少32位的随机字符串作为SECRET_KEY"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ 错误: 未设置DB_PASSWORD环境变量"
    echo "💡 提示: 请设置数据库密码"
    exit 1
fi

echo "✅ 环境变量检查通过"

# 检查Docker是否安装
if ! [ -x "$(command -v docker)" ]; then
  echo '❌ 错误: Docker未安装' >&2
  exit 1
fi

echo "✅ Docker已安装"

# 检查Docker Compose是否安装
if ! [ -x "$(command -v docker-compose)" ]; then
  echo '❌ 错误: Docker Compose未安装' >&2
  exit 1
fi

echo "✅ Docker Compose已安装"

# 创建必要的目录
mkdir -p logs/nginx logs/backend logs/crawler data/crawler

echo "📁 日志和数据目录已创建"

# 检查配置文件是否存在
if [ ! -f ".env.production" ]; then
    echo "❌ 错误: .env.production文件不存在"
    echo "💡 提示: 请先创建生产环境配置文件"
    exit 1
fi

echo "✅ 生产环境配置文件存在"

# 拉取最新的镜像
echo "🐳 拉取最新镜像..."
docker-compose -f docker-compose.production.yml pull --ignore-pull-failures

# 构建应用镜像
echo "🔨 构建应用镜像..."
docker-compose -f docker-compose.production.yml build --no-cache

# 启动服务
echo "🚀 启动生产环境服务..."
docker-compose -f docker-compose.production.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.production.yml ps

# 显示部署完成信息
echo ""
echo "🎉 生产环境部署完成!"
echo ""
echo "📊 服务状态:"
docker-compose -f docker-compose.production.yml ps
echo ""
echo "🌐 访问地址:"
echo "   - 应用: http://localhost"
echo ""
echo "📝 部署完成时间: $(date)"
echo ""
echo "⚠️  安全提醒:"
echo "   - 确保防火墙已配置，只开放必要的端口"
echo "   - 定期备份数据库"
echo "   - 监控系统日志"
echo "   - 定期更新依赖包和基础镜像"