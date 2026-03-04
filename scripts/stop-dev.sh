#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 停止所有服务
stop_services() {
    print_message "Stopping all services..."
    
    # 停止前端服务
    if pgrep -f "npm run dev" > /dev/null; then
        print_message "Stopping frontend service..."
        pkill -f "npm run dev"
    fi
    
    # 停止后端服务
    if pgrep -f "uvicorn" > /dev/null; then
        print_message "Stopping backend service..."
        pkill -f "uvicorn"
    fi
    
    # 停止Docker Compose服务
    print_message "Stopping Docker Compose services..."
    docker-compose -f docker-compose.yml down
    
    # 清理临时文件
    print_message "Cleaning up temporary files..."
    rm -f .python-version
    rm -f *.pyc
    
    print_message "All services stopped successfully"
}

# 主函数
main() {
    print_message "Stopping Soccer Scanning System development environment..."
    stop_services
}

# 执行主函数
main