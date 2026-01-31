#!/bin/bash

echo "========================================"
echo "运行足球SP管理数据源页面端到端测试"
echo "========================================"

# 检查是否在前端目录
if [ ! -f "package.json" ]; then
    echo "错误：请在frontend目录下运行此脚本"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "错误：未找到Node.js，请先安装Node.js"
    exit 1
fi

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "未找到node_modules，正在安装依赖..."
    npm install
fi

# 检查Playwright浏览器
echo "检查Playwright浏览器安装..."
npx playwright install chromium 2>/dev/null

# 启动前端服务器（如果未运行）
echo "启动前端开发服务器..."
npm run dev &
SERVER_PID=$!

# 等待服务器启动
echo "等待服务器启动（5秒）..."
sleep 5

# 运行测试
echo "开始运行端到端测试..."
npx playwright test tests/e2e/data-source-management.spec.js --headed

# 杀死服务器进程
kill $SERVER_PID 2>/dev/null

echo "测试完成！"