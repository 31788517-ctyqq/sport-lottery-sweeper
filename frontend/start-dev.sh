#!/bin/bash

# 体育彩票扫盘系统 - 开发环境启动脚本

echo "🚀 启动体育彩票扫盘系统开发环境..."

# 检查Node.js版本
NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_NODE="18.0.0"

if [ "$(printf '%s\n' "$REQUIRED_NODE" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_NODE" ]; then
    echo "❌ Node.js版本过低，需要 $REQUIRED_NODE 或更高版本，当前版本: $NODE_VERSION"
    exit 1
fi

echo "✅ Node.js版本检查通过: $NODE_VERSION"

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 创建必要的目录
mkdir -p test-results logs uploads backups

# 启动后端服务（如果后端目录存在）
if [ -d "../backend" ]; then
    echo "🔧 启动后端服务..."
    cd ../backend
    if command -v python &> /dev/null; then
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
        BACKEND_PID=$!
        echo $BACKEND_PID > ../frontend/backend.pid
        cd ../frontend
        echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
    elif command -v python3 &> /dev/null; then
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
        BACKEND_PID=$!
        echo $BACKEND_PID > backend.pid
        cd frontend
        echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
    else
        echo "⚠️  未找到Python，跳过后端启动"
    fi
else
    echo "⚠️  后端目录不存在，跳过后端启动"
fi

# 等待后端启动
if [ -f "backend.pid" ]; then
    echo "⏳ 等待后端服务启动..."
    sleep 5
    
    # 测试后端连接
    if curl -f http://localhost:8001/api/health > /dev/null 2>&1; then
        echo "✅ 后端服务连接正常"
    else
        echo "⚠️  后端服务可能未完全启动，请检查"
    fi
fi

# 启动前端开发服务器
echo "🌐 启动前端开发服务器..."
npm run dev &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid

echo ""
echo "🎉 开发环境启动完成!"
echo "📱 前端地址: http://localhost:3015"
echo "🔧 后端地址: http://localhost:8001"
echo "📊 API文档: http://localhost:8001/docs"
echo ""
echo "💡 提示:"
echo "  - 前端页面会自动在浏览器中打开"
echo "  - 按 Ctrl+C 停止所有服务"
echo "  - 使用 'npm run test' 运行测试"
echo "  - 使用 'npm run lint' 检查代码质量"
echo ""

# 等待用户中断
wait $FRONTEND_PID

# 清理进程
cleanup() {
    echo "\n🛑 正在停止服务..."
    
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        kill $FRONTEND_PID 2>/dev/null
        rm frontend.pid
        echo "✅ 前端服务已停止"
    fi
    
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        kill $BACKEND_PID 2>/dev/null
        rm backend.pid
        echo "✅ 后端服务已停止"
    fi
    
    echo "👋 再见!"
}

# 捕获中断信号
trap cleanup SIGINT SIGTERM

exit 0