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

# 检查系统要求
check_system() {
    print_message "Checking system requirements..."
    
    # 检查操作系统
    if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    # 检查架构
    arch=$(uname -m)
    if [[ "$arch" != "x86_64" ]] && [[ "$arch" != "arm64" ]]; then
        print_error "Unsupported architecture: $arch"
        exit 1
    fi
}

# 检查并安装 Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. Installing Docker..."
        
        # 添加 Docker 官方 GPG 密钥
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        
        # 添加 Docker 仓库
        sudo add-apt-repository \
            "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable"
            
        # 更新包索引
        sudo apt-get update
        
        # 安装最新版本的 Docker
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        
        # 启动 Docker 服务
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # 添加当前用户到 docker 组
        sudo usermod -aG docker $USER
        
        print_message "Docker installed successfully"
        print_warning "Please log out and log back in to use Docker without sudo"
        exit 1
    else
        print_message "Docker is installed"
        
        # 检查 Docker 服务状态
        if ! sudo systemctl is-active --quiet docker; then
            print_warning "Starting Docker service..."
            sudo systemctl start docker
            sudo systemctl enable docker
        fi
    fi
}

# 检查并安装 Docker Compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose is not installed. Installing Docker Compose..."
        
        # 下载 Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        
        # 设置可执行权限
        sudo chmod +x /usr/local/bin/docker-compose
        
        print_message "Docker Compose installed successfully"
    else
        print_message "Docker Compose is installed"
    fi
}

# 检查 Python 环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
        print_error "Python 3.8 or higher is required, found $python_version"
        exit 1
    fi
    
    print_message "Python $python_version is installed"
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        print_warning "pip3 is not installed. Installing..."
        sudo apt-get update
        sudo apt-get install -y python3-pip
    fi
    
    # 检查虚拟环境
    if ! command -v venv &> /dev/null; then
        print_warning "venv is not installed. Installing..."
        sudo apt-get install -y python3-venv
    fi
}

# 检查 Node.js 环境
check_node() {
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Installing Node.js..."
        
        # 添加 NodeSource 仓库
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        
        # 安装 Node.js
        sudo apt-get install -y nodejs
        
        print_message "Node.js installed successfully"
    else
        node_version=$(node -v)
        print_message "Node.js $node_version is installed"
    fi
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    else
        npm_version=$(npm -v)
        print_message "npm $npm_version is installed"
    fi
}

# 检查端口占用
check_ports() {
    print_message "Checking required ports..."
    
    local ports=("5432" "6379" "27017" "5672" "9200" "8000" "3000")
    local services=("PostgreSQL" "Redis" "MongoDB" "RabbitMQ" "Elasticsearch" "Backend" "Frontend")
    
    for i in "${!ports[@]}"; do
        port=${ports[$i]}
        service=${services[$i]}
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port ($service) is already in use"
            print_warning "Please stop the service using port $port or change the configuration"
        else
            print_message "Port $port ($service) is available"
        fi
    done
}

# 主函数
main() {
    print_message "Checking requirements for Soccer Scanning System development environment..."
    
    # 检查系统
    check_system
    
    # 检查 Docker
    check_docker
    
    # 检查 Docker Compose
    check_docker_compose
    
    # 检查 Python
    check_python
    
    # 检查 Node.js
    check_node
    
    # 检查端口
    check_ports
    
    print_message "All requirements are satisfied!"
}

# 执行主函数
main