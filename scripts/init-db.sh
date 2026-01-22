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

# 检查服务状态
check_service() {
    local service=$1
    local host=$2
    local port=$3
    
    if nc -z $host $port; then
        print_message "$service is running on $host:$port"
        return 0
    else
        print_error "$service is not accessible on $host:$port"
        return 1
    fi
}

# 等待服务就绪
wait_for_service() {
    local service=$1
    local host=$2
    local port=$3
    local max_attempts=30
    local attempt=1

    print_message "Waiting for $service to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if check_service $service $host $port; then
            return 0
        fi
        print_message "Attempt $attempt/$max_attempts: $service not ready yet, waiting..."
        sleep 2
        ((attempt++))
    done
    
    print_error "Timeout: $service did not become ready"
    return 1
}

# 初始化数据库
init_database() {
    print_message "Initializing database..."
    
    # 检查数据库是否就绪
    if ! wait_for_service "PostgreSQL" localhost 5432; then
        print_error "Failed to connect to PostgreSQL"
        exit 1
    fi
    
    # 运行数据库迁移
    cd backend
    if ! alembic upgrade head; then
        print_error "Failed to run database migrations"
        exit 1
    fi
    cd ..
    
    # 初始化基础数据
    if ! docker-compose -f docker-compose.dev.yml exec -T backend python scripts/init_db.py; then
        print_error "Failed to initialize basic data"
        exit 1
    fi
    
    print_message "Database initialized successfully"
}

# 创建管理员账户
create_admin() {
    local username=${1:-admin}
    local email=${2:-admin@example.com}
    local password=${3:-admin123}
    
    print_message "Creating admin account..."
    
    if ! docker-compose -f docker-compose.dev.yml exec -T backend python scripts/create_admin.py \
        $username $email $password; then
        print_error "Failed to create admin account"
        exit 1
    fi
    
    print_message "Admin account created successfully"
}

# 验证数据库
verify_database() {
    print_message "Verifying database..."
    
    # 检查管理员账户
    if ! docker-compose -f docker-compose.dev.yml exec -T backend python -c "
import sys
sys.path.append('/app')
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
admin_user = db.query(User).filter(User.username == 'admin').first()
if not admin_user:
    print('Admin user not found')
    sys.exit(1)
print('Database verification passed')
"; then
        print_error "Database verification failed"
        exit 1
    fi
    
    print_message "Database verification successful"
}

# 主函数
main() {
    print_message "Starting database initialization..."
    
    # 检查Docker是否运行
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running"
        exit 1
    fi
    
    # 初始化数据库
    init_database
    
    # 创建管理员账户
    create_admin $1 $2 $3
    
    # 验证数据库
    verify_database
    
    print_message "Database initialization completed!"
}

# 执行主函数
main "$@"