#!/bin/bash
# 前端依赖安装脚本 (Linux/Mac)

cd "$(dirname "$0")/../frontend"

echo "===================================="
echo "前端依赖安装脚本"
echo "===================================="
echo ""

echo "[1/3] 检查 Node.js 和 npm..."
node --version
npm --version
echo ""

echo "[2/3] 安装前端依赖..."
npm install --legacy-peer-deps
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 依赖安装失败!"
    echo "尝试使用 --force 选项..."
    npm install --force
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 依赖安装仍然失败!"
        exit 1
    fi
fi
echo ""

echo "[3/3] 验证依赖安装..."
if [ -d "node_modules" ]; then
    echo "✅ 依赖安装成功!"
    echo ""
    echo "依赖数量:"
    ls -1 node_modules | wc -l
else
    echo "❌ node_modules 目录不存在!"
    exit 1
fi

echo ""
echo "===================================="
echo "安装完成!"
echo "启动前端: npm run dev"
echo "===================================="
