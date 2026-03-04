#!/bin/bash
# Database Backup Script for Sport Lottery Sweeper
# 体育彩票系统数据库备份脚本

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKUP_BASE_DIR="/opt/backups/sport-lottery"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30
LOG_FILE="/var/log/sport-lottery/backup.log"

# Database configuration
POSTGRES_HOST="postgres"
POSTGRES_PORT="5432"
POSTGRES_DB="sport_lottery_prod"
POSTGRES_USER="${POSTGRES_USER}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"

# Redis configuration
REDIS_HOST="redis"
REDIS_PORT="6379"
REDIS_PASSWORD="${REDIS_PASSWORD}"

# Notification settings
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL}"

print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a $LOG_FILE
}

print_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1${NC}" | tee -a $LOG_FILE
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠ $1${NC}" | tee -a $LOG_FILE
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ $1${NC}" | tee -a $LOG_FILE
}

# Create backup directories
create_backup_dirs() {
    print_status "Creating backup directories..."
    
    mkdir -p $BACKUP_BASE_DIR/postgres/daily
    mkdir -p $BACKUP_BASE_DIR/postgres/weekly
    mkdir -p $BACKUP_BASE_DIR/postgres/monthly
    mkdir -p $BACKUP_BASE_DIR/redis
    mkdir -p $BACKUP_BASE_DIR/configs
    mkdir -p $(dirname $LOG_FILE)
    
    print_success "Backup directories created"
}

# PostgreSQL backup
backup_postgres() {
    print_status "Starting PostgreSQL backup..."
    
    local backup_file="$BACKUP_BASE_DIR/postgres/daily/postgres_backup_$TIMESTAMP.sql.gz"
    local backup_dir="$(dirname $backup_file)"
    
    # Set PGPASSWORD environment variable
    export PGPASSWORD=$POSTGRES_PASSWORD
    
    # Create backup using pg_dump
    if pg_dump -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB \
        --verbose --clean --no-owner --no-privileges --format=custom \
        | gzip > "${backup_file%.gz}"; then
        
        # Compress the backup
        gzip "${backup_file%.gz}"
        
        # Get backup size
        local backup_size=$(du -h $backup_file | cut -f1)
        print_success "PostgreSQL backup completed: $backup_file ($backup_size)"
        
        # Verify backup integrity
        if gunzip -t $backup_file 2>/dev/null; then
            print_success "PostgreSQL backup integrity verified"
        else
            print_error "PostgreSQL backup integrity check failed"
            return 1
        fi
        
        # Upload to cloud storage (optional)
        upload_to_cloud_storage $backup_file "postgres"
        
    else
        print_error "PostgreSQL backup failed"
        unset PGPASSWORD
        return 1
    fi
    
    unset PGPASSWORD
    return 0
}

# Redis backup
backup_redis() {
    print_status "Starting Redis backup..."
    
    local backup_file="$BACKUP_BASE_DIR/redis/redis_backup_$TIMESTAMP.rdb.gz"
    
    # Trigger BGSAVE in Redis
    if redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD BGSAVE; then
        print_status "Redis BGSAVE triggered, waiting for completion..."
        
        # Wait for BGSAVE to complete
        local max_wait=30
        local wait_time=0
        
        while [ $wait_time -lt $max_wait ]; do
            local bgsave_status=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD INFO persistence | grep rdb_bgsave_in_progress | cut -d: -f2 | tr -d '\r')
            
            if [ "$bgsave_status" = "0" ]; then
                print_success "Redis BGSAVE completed"
                break
            fi
            
            sleep 2
            wait_time=$((wait_time + 2))
        done
        
        # Copy RDB file (assuming default location)
        # In production, you might need to adjust the RDB file path
        local rdb_source="/var/lib/redis/dump.rdb"
        
        if docker exec $REDIS_HOST test -f $rdb_source; then
            docker cp $REDIS_HOST:$rdb_source $backup_file
            gunzip -c $backup_file | gzip > "${backup_file}.tmp" && mv "${backup_file}.tmp" $backup_file
            
            local backup_size=$(du -h $backup_file | cut -f1)
            print_success "Redis backup completed: $backup_file ($backup_size)"
            
            # Upload to cloud storage
            upload_to_cloud_storage $backup_file "redis"
        else
            print_warning "Redis RDB file not found at $rdb_source"
            # Alternative: use redis-cli SAVE command
            redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD SAVE
            print_warning "Used synchronous SAVE instead of BGSAVE"
        fi
        
    else
        print_error "Failed to trigger Redis BGSAVE"
        return 1
    fi
    
    return 0
}

# Application configuration backup
backup_configs() {
    print_status "Backing up application configurations..."
    
    local config_backup="$BACKUP_BASE_DIR/configs/config_backup_$TIMESTAMP.tar.gz"
    
    # Create compressed archive of important configs
    tar -czf $config_backup \
        docker-compose*.yml \
        nginx/ \
        scripts/ \
        .env* \
        alembic.ini \
        --exclude=node_modules \
        --exclude=.git \
        --exclude=__pycache__ \
        --exclude="*.log" \
        2>/dev/null
    
    if [ $? -eq 0 ]; then
        local backup_size=$(du -h $config_backup | cut -f1)
        print_success "Configuration backup completed: $config_backup ($backup_size)"
        
        # Upload to cloud storage
        upload_to_cloud_storage $config_backup "configs"
    else
        print_error "Configuration backup failed"
        return 1
    fi
    
    return 0
}

# Upload backup to cloud storage
upload_to_cloud_storage() {
    local file_path=$1
    local backup_type=$2
    
    # AWS S3 upload (if configured)
    if command -v aws &> /dev/null && [[ -n "${AWS_S3_BUCKET}" ]]; then
        print_status "Uploading to AWS S3..."
        aws s3 cp $file_path s3://${AWS_S3_BUCKET}/sport-lottery/${backup_type}/$(basename $file_path)
        if [ $? -eq 0 ]; then
            print_success "Successfully uploaded to S3"
        else
            print_warning "Failed to upload to S3"
        fi
    fi
    
    # Google Cloud Storage upload (if configured)
    if command -v gsutil &> /dev/null && [[ -n "${GCS_BUCKET}" ]]; then
        print_status "Uploading to Google Cloud Storage..."
        gsutil cp $file_path gs://${GCS_BUCKET}/sport-lottery/${backup_type}/$(basename $file_path)
        if [ $? -eq 0 ]; then
            print_success "Successfully uploaded to GCS"
        else
            print_warning "Failed to upload to GCS"
        fi
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    print_status "Cleaning up old backups (retention: $RETENTION_DAYS days)..."
    
    # Remove old daily backups
    find $BACKUP_BASE_DIR/postgres/daily -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
    find $BACKUP_BASE_DIR/redis -name "*.rdb.gz" -mtime +$RETENTION_DAYS -delete
    find $BACKUP_BASE_DIR/configs -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
    
    # Weekly backup (keep 12 weeks)
    if [[ $(date +%u) == 7 ]]; then  # Sunday
        cp $(ls -t $BACKUP_BASE_DIR/postgres/daily/*.sql.gz | head -1) \
           $BACKUP_BASE_DIR/postgres/weekly/postgres_weekly_$TIMESTAMP.sql.gz
    fi
    
    # Monthly backup (keep 12 months)
    if [[ $(date +%d) == 01 ]]; then  # First day of month
        cp $(ls -t $BACKUP_BASE_DIR/postgres/daily/*.sql.gz | head -1) \
           $BACKUP_BASE_DIR/postgres/monthly/postgres_monthly_$TIMESTAMP.sql.gz
    fi
    
    # Cleanup weekly backups older than 12 weeks
    find $BACKUP_BASE_DIR/postgres/weekly -name "*.sql.gz" -mtime +84 -delete
    find $BACKUP_BASE_DIR/postgres/monthly -name "*.sql.gz" -mtime +365 -delete
    
    print_success "Old backups cleaned up"
}

# Send notification
send_notification() {
    local status=$1
    local message=$2
    
    # Slack notification
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        local color="good"
        if [[ $status != "success" ]]; then
            color="danger"
        fi
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"attachments\":[{\"color\":\"$color\",\"text\":\"$message\"}]}" \
            $SLACK_WEBHOOK_URL
    fi
    
    # Email notification (if mail command is available)
    if command -v mail &> /dev/null && [[ -n "$NOTIFICATION_EMAIL" ]]; then
        echo "$message" | mail -s "Sport Lottery Backup $status" $NOTIFICATION_EMAIL
    fi
}

# Verify backup completeness
verify_backup_completeness() {
    print_status "Verifying backup completeness..."
    
    local backup_success=true
    
    # Check if PostgreSQL backup exists and is recent
    if ls $BACKUP_BASE_DIR/postgres/daily/postgres_backup_*.sql.gz 1> /dev/null 2>&1; then
        local latest_backup=$(ls -t $BACKUP_BASE_DIR/postgres/daily/postgres_backup_*.sql.gz | head -1)
        local backup_age=$(( $(date +%s) - $(stat -c %Y $latest_backup) ))
        
        if [ $backup_age -gt 7200 ]; then  # 2 hours
            print_warning "Latest PostgreSQL backup is older than 2 hours"
            backup_success=false
        else
            print_success "PostgreSQL backup verification passed"
        fi
    else
        print_error "No PostgreSQL backup found"
        backup_success=false
    fi
    
    # Check disk space
    local available_space=$(df $BACKUP_BASE_DIR | awk 'NR==2 {print $4}')
    if [ $available_space -lt 1048576 ]; then  # Less than 1GB
        print_warning "Low disk space for backups: $((available_space/1024)) MB available"
        backup_success=false
    fi
    
    if $backup_success; then
        send_notification "success" "✅ Database backup completed successfully at $(date)"
        return 0
    else
        send_notification "failed" "❌ Database backup failed or incomplete at $(date)"
        return 1
    fi
}

# Restore functions (for emergency use)
restore_postgres() {
    local backup_file=$1
    
    if [[ -z "$backup_file" ]]; then
        print_error "Backup file path is required for restore"
        return 1
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        print_error "Backup file not found: $backup_file"
        return 1
    fi
    
    print_warning "This will overwrite the current database! Continue? (yes/no)"
    read -r confirmation
    
    if [[ $confirmation != "yes" ]]; then
        print_status "Restore cancelled"
        return 0
    fi
    
    print_status "Restoring PostgreSQL from $backup_file..."
    
    # Drop and recreate database
    export PGPASSWORD=$POSTGRES_PASSWORD
    dropdb -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER $POSTGRES_DB
    createdb -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER $POSTGRES_DB
    
    # Restore from backup
    gunzip -c $backup_file | pg_restore -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB --verbose
    
    if [ $? -eq 0 ]; then
        print_success "PostgreSQL restore completed"
    else
        print_error "PostgreSQL restore failed"
    fi
    
    unset PGPASSWORD
}

# Main execution
main() {
    local action=${1:-backup}
    local restore_file=${2}
    
    print_status "Starting database backup script..."
    print_status "Action: $action"
    
    create_backup_dirs
    
    case $action in
        "backup")
            local backup_success=true
            
            backup_postgres || backup_success=false
            backup_redis || backup_success=false
            backup_configs || backup_success=false
            cleanup_old_backups
            verify_backup_completeness || backup_success=false
            
            if $backup_success; then
                print_success "All backup operations completed successfully"
                exit 0
            else
                print_error "Some backup operations failed"
                exit 1
            fi
            ;;
        "restore-postgres")
            restore_postgres $restore_file
            ;;
        "verify")
            verify_backup_completeness
            ;;
        *)
            echo "Usage: $0 [backup|restore-postgres <file>|verify]"
            echo "  backup              - Perform full backup"
            echo "  restore-postgres <file> - Restore PostgreSQL from backup"
            echo "  verify              - Verify backup completeness"
            exit 1
            ;;
    esac
}

# Handle script interruption
trap 'print_warning "Backup process interrupted"; exit 130' INT TERM

# Run main function
main "$@"