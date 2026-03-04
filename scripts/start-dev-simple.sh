#!/bin/bash

# 项目根目录
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)

# 日志目录
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 开始启动竞彩足球扫盘系统 - 开发模式${NC}"
echo "--------------------------------"

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  警告: 未检测到虚拟环境，尝试激活...${NC}"
    VENV_PATH="$PROJECT_ROOT/venv"
    if [ -d "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate" 2>/dev/null || source "$VENV_PATH/Scripts/activate" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 已激活虚拟环境${NC}"
        else
            echo -e "${RED}❌ 无法激活虚拟环境${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ 未找到虚拟环境目录${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ 已在虚拟环境中${NC}"
fi

# 检查依赖
echo -e "${YELLOW}🔍 检查依赖...${NC}"
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${RED}❌ FastAPI 未安装${NC}"
    pip install fastapi
fi

if ! python -c "import uvicorn" 2>/dev/null; then
    echo -e "${RED}❌ Uvicorn 未安装${NC}"
    pip install uvicorn
fi

echo -e "${GREEN}✅ 依赖检查完成${NC}"

# 启动后端服务
echo -e "${YELLOW}🌐 启动后端服务...${NC}"
if uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend.log" 2>&1 & then
    echo -e "${GREEN}✅ 后端服务已启动${NC}"
    echo "📖 API文档: http://0.0.0.0:8000/docs"
else
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    cat "$LOG_DIR/backend.log" 2>/dev/null || echo "无法读取日志文件"
    exit 1
fi

# 启动前端服务（如果存在）
if [ -d "$PROJECT_ROOT/frontend" ]; then
    echo -e "${YELLOW}🖥️  启动前端服务...${NC}"
    cd "$PROJECT_ROOT/frontend"
    if command -v pnpm >/dev/null 2>&1; then
        if pnpm run dev > "$LOG_DIR/frontend.log" 2>&1 & then
            echo -e "${GREEN}✅ 前端服务已启动${NC}"
            echo "🌐 前端界面: http://localhost:3000"
        else
            echo -e "${RED}❌ 前端服务启动失败${NC}"
            cat "$LOG_DIR/frontend.log" 2>/dev/null || echo "无法读取日志文件"
        fi
    elif command -v npm >/dev/null 2>&1; then
        if npm run dev > "$LOG_DIR/frontend.log" 2>&1 & then
            echo -e "${GREEN}✅ 前端服务已启动${NC}"
            echo "🌐 前端界面: http://localhost:3000"
        else
            echo -e "${RED}❌ 前端服务启动失败${NC}"
            cat "$LOG_DIR/frontend.log" 2>/dev/null || echo "无法读取日志文件"
        fi
    else
        echo -e "${RED}❌ 未找到 pnpm 或 npm${NC}"
    fi
    cd "$PROJECT_ROOT"
else
    echo -e "${YELLOW}⚠️  前端目录不存在，跳过前端启动${NC}"
fi

echo "--------------------------------"
echo -e "${GREEN}🎉 启动完成！${NC}"
echo "📖 API文档: http://0.0.0.0:8000/docs"
echo "📊 健康检查: http://0.0.0.0:8000/health"
if [ -d "$PROJECT_ROOT/frontend" ]; then
    echo "🌐 前端界面: http://localhost:3000"
fi
echo "📄 后端日志: $LOG_DIR/backend.log"
echo "📖 前端日志: $LOG_DIR/frontend.log"

# 等待用户中断信号
trap 'echo -e "\n${YELLOW}🛑 正在停止服务...${NC}"; kill %1 %2 2>/dev/null; exit' INT TERM

# 保持脚本运行
wait