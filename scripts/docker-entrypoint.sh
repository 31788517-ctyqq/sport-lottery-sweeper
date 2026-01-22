#!/bin/bash
# Docker Entrypoint Script for Backend Service
# 体育彩票系统后端Docker入口脚本

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Function to wait for database
wait_for_db() {
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for database connection..."
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import sys
import os
from sqlalchemy import create_engine, text

try:
    engine = create_engine(os.environ.get('DATABASE_URL'))
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
except Exception as e:
    sys.exit(1)
" 2>/dev/null; then
            print_status "Database is ready!"
            return 0
        fi
        
        print_warning "Database not ready, attempt $attempt/$max_attempts"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Database connection failed after $max_attempts attempts"
    return 1
}

# Function to wait for Redis
wait_for_redis() {
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for Redis connection..."
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import sys
import os
import redis

try:
    r = redis.Redis.from_url(os.environ.get('REDIS_URL'))
    r.ping()
    print('Redis connection successful')
except Exception as e:
    sys.exit(1)
" 2>/dev/null; then
            print_status "Redis is ready!"
            return 0
        fi
        
        print_warning "Redis not ready, attempt $attempt/$max_attempts"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Redis connection failed after $max_attempts attempts"
    return 1
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if python -m alembic upgrade head; then
        print_status "Database migrations completed successfully"
    else
        print_error "Database migrations failed"
        return 1
    fi
}

# Function to initialize database
init_database() {
    print_status "Initializing database..."
    
    if python -c "
import sys
sys.path.append('/app/backend')
from scripts.init_user_tables import init_database
try:
    init_database()
    print('Database initialization completed')
except Exception as e:
    print(f'Database initialization warning: {e}')
" 2>/dev/null; then
        print_status "Database initialization completed"
    else
        print_warning "Database initialization had issues, but continuing..."
    fi
}

# Function to start Celery worker (if needed)
start_celery_worker() {
    if [ "$CELERY_WORKER_ENABLED" = "true" ]; then
        print_status "Starting Celery worker..."
        celery -A app.celery_app:celery worker -l info -Q default,data_processing,crawler &
        CELERY_PID=$!
        echo $CELERY_PID > /tmp/celery.pid
    fi
}

# Function to start Celery beat (if needed)
start_celery_beat() {
    if [ "$CELERY_BEAT_ENABLED" = "true" ]; then
        print_status "Starting Celery beat scheduler..."
        celery -A app.celery_app:celery beat -l info &
        BEAT_PID=$!
        echo $BEAT_PID > /tmp/celery-beat.pid
    fi
}

# Signal handlers
cleanup() {
    print_status "Shutting down services..."
    
    # Stop Celery worker
    if [ -f /tmp/celery.pid ]; then
        CELERY_PID=$(cat /tmp/celery.pid)
        kill -TERM $CELERY_PID 2>/dev/null || true
        rm -f /tmp/celery.pid
    fi
    
    # Stop Celery beat
    if [ -f /tmp/celery-beat.pid ]; then
        BEAT_PID=$(cat /tmp/celery-beat.pid)
        kill -TERM $BEAT_PID 2>/dev/null || true
        rm -f /tmp/celery-beat.pid
    fi
    
    print_status "Shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Main execution
main() {
    print_status "Starting Sport Lottery Backend Service..."
    
    # Source environment variables if .env file exists
    if [ -f /app/backend/.env ]; then
        print_status "Loading environment variables from .env file"
        set -a
        source /app/backend/.env
        set +a
    fi
    
    # Wait for dependencies
    wait_for_db
    wait_for_redis
    
    # Initialize database if needed
    if [ "$INIT_DB_ON_STARTUP" = "true" ]; then
        init_database
    fi
    
    # Run migrations
    if [ "$RUN_MIGRATIONS_ON_STARTUP" = "true" ]; then
        run_migrations
    fi
    
    # Start background services
    start_celery_worker
    start_celery_beat
    
    # Start main application
    print_status "Starting main application server..."
    exec "$@"
}

# Run main function with all arguments
main "$@"