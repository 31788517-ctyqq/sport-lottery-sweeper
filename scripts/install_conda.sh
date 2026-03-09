#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 开始安装和配置竞彩足球扫盘系统${NC}"
echo "--------------------------------"

# 检测操作系统
OS_TYPE=$(uname -s)
echo -e "${BLUE}检测操作系统: $OS_TYPE${NC}"

# 检查是否已安装conda
if command -v conda &> /dev/null; then
    echo -e "${GREEN}✅ Conda 已安装${NC}"
    CONDA_INSTALLED=true
else
    echo -e "${YELLOW}⚠️  Conda 未安装，开始安装...${NC}"
    CONDA_INSTALLED=false
fi

# 安装Conda（如果未安装）
if [ "$CONDA_INSTALLED" = false ]; then
    if [[ "$OS_TYPE" == "Linux" ]]; then
        CONDA_FILE="Miniforge3-Linux-x86_64.sh"
    elif [[ "$OS_TYPE" == "Darwin" ]]; then
        CONDA_FILE="Miniforge3-MacOSX-x86_64.sh"
    else
        echo -e "${RED}❌ 不支持的操作系统: $OS_TYPE${NC}"
        exit 1
    fi

    # 下载并安装Miniforge
    echo -e "${YELLOW}📥 下载 $CONDA_FILE ...${NC}"
    curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/$CONDA_FILE"
    
    echo -e "${YELLOW}🔧 安装 Miniforge ...${NC}"
    bash "$CONDA_FILE" -b -p $HOME/miniforge3
    
    # 初始化conda
    $HOME/miniforge3/bin/conda init bash
    
    # 重新加载环境
    source ~/.bashrc
    
    echo -e "${GREEN}✅ Conda 安装完成${NC}"
fi

# 创建并激活conda环境
ENV_NAME="football-scan"
echo -e "${YELLOW}🔄 检查并创建conda环境: $ENV_NAME${NC}"

if conda env list | grep -q "^$ENV_NAME "; then
    echo -e "${GREEN}✅ 环境 $ENV_NAME 已存在${NC}"
else
    echo -e "${YELLOW}🆕 创建新环境: $ENV_NAME${NC}"
    conda create -n $ENV_NAME python=3.11 -y
fi

# 激活环境
echo -e "${YELLOW}🔌 激活conda环境: $ENV_NAME${NC}"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

# 检查Python版本
PYTHON_VERSION=$(python --version)
echo -e "${GREEN}✅ Python 版本: $PYTHON_VERSION${NC}"

# 检查并安装pip
if command -v pip &> /dev/null; then
    echo -e "${GREEN}✅ Pip 已安装${NC}"
else
    echo -e "${YELLOW}🔧 安装 Pip${NC}"
    conda install pip -y
fi

# 项目根目录
PROJECT_ROOT=$(pwd)

# 检查requirements.txt是否存在
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo -e "${YELLOW}📦 安装项目依赖...${NC}"
    pip install -r "$PROJECT_ROOT/requirements.txt"
    echo -e "${GREEN}✅ 项目依赖安装完成${NC}"
else
    echo -e "${RED}❌ 未找到 requirements.txt${NC}"
    exit 1
fi

# 检查Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js 版本: $NODE_VERSION${NC}"
else
    echo -e "${YELLOW}🔧 安装 Node.js${NC}"
    conda install nodejs -c conda-forge -y
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js 版本: $NODE_VERSION${NC}"
fi

# 检查npm
if command -v npm &> /dev/null; then
    echo -e "${GREEN}✅ npm 已安装${NC}"
else
    echo -e "${RED}❌ npm 未安装${NC}"
    exit 1
fi

# 检查前端目录并安装前端依赖
if [ -d "$PROJECT_ROOT/frontend" ]; then
    echo -e "${YELLOW}📦 安装前端依赖...${NC}"
    cd "$PROJECT_ROOT/frontend"
    
    if command -v pnpm &> /dev/null; then
        echo -e "${GREEN}✅ pnpm 已安装${NC}"
    else
        echo -e "${YELLOW}🔧 安装 pnpm${NC}"
        npm install -g pnpm
    fi
    
    pnpm install
    echo -e "${GREEN}✅ 前端依赖安装完成${NC}"
    cd "$PROJECT_ROOT"
else
    echo -e "${YELLOW}⚠️  前端目录不存在${NC}"
fi

# 安装playwright并下载浏览器
if python -c "import playwright" &> /dev/null; then
    echo -e "${GREEN}✅ Playwright 已安装${NC}"
else
    echo -e "${YELLOW}🔧 安装 Playwright${NC}"
    pip install playwright
fi

echo -e "${YELLOW}🌐 安装 Playwright 浏览器...${NC}"
playwright install chromium

# 检查是否可以导入项目模块
echo -e "${YELLOW}🧪 测试项目模块导入...${NC}"
if python -c "from src.backend.main import app; print('Success')" &> /dev/null; then
    echo -e "${GREEN}✅ 项目模块导入成功${NC}"
else
    echo -e "${RED}❌ 项目模块导入失败${NC}"
    exit 1
fi

echo "--------------------------------"
echo -e "${GREEN}🎉 安装配置完成！${NC}"
echo ""
echo -e "${BLUE}💡 使用说明:${NC}"
echo "   激活环境: conda activate $ENV_NAME"
echo "   启动后端: uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000"
echo "   启动前端: cd frontend && pnpm run dev"
echo ""
echo -e "${BLUE}🔧 开发模式启动:${NC}"
echo "# 1. 激活环境"
echo "   conda activate $ENV_NAME"
echo "# 2. 启动后端服务"
echo "   cd $PROJECT_ROOT"
echo "   uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000"
echo "# 3. 在新终端启动前端服务"
echo "   cd $PROJECT_ROOT/frontend"
echo "   pnpm run dev"
echo ""

# 提供启动示例
cat << EOF > $PROJECT_ROOT/start_example.sh
#!/bin/bash
# 示例启动脚本

# 激活conda环境
source \$(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

# 启动后端服务
echo "启动后端服务..."
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
EOF

chmod +x $PROJECT_ROOT/start_example.sh
echo -e "${GREEN}📄 示例启动脚本已保存到: $PROJECT_ROOT/start_example.sh${NC}"

echo -e "${GREEN}🏆 恭喜！环境配置完成！${NC}"
```
