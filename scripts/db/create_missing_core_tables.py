# 体育彩票扫盘系统 - 缺失核心业务表创建脚本
# 创建5个关键业务表：投注订单、支付交易、系统配置、通知日志、反欺诈检测

import sqlite3
import os
from datetime import datetime

def create_missing_core_tables():
    print("🚀 创建缺失的核心业务表")
    print("="*60)
    
    db_path = "data/sport_lottery.db"
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 定义核心业务表结构
    core_tables = {
        'betting_orders': {
            'priority': '🔥 最高',
            'description': '投注订单表 - 系统核心业务',
            'sql': '''CREATE TABLE IF NOT EXISTS betting_orders (
                id BIGINT PRIMARY KEY AUTOINCREMENT COMMENT '主键ID',
                order_number VARCHAR(50) UNIQUE NOT NULL COMMENT '订单号',
                user_id BIGINT NOT NULL COMMENT '用户ID',
                match_id BIGINT NOT NULL COMMENT '比赛ID',
                bet_type ENUM('single', 'multiple', 'parlay') NOT NULL DEFAULT 'single' COMMENT '投注类型',
                bet_content TEXT NOT NULL COMMENT '投注内容(JSON格式)',
                bet_amount DECIMAL(12,2) NOT NULL COMMENT '投注金额',
                potential_win DECIMAL(12,2) NOT NULL COMMENT '预计奖金',
                actual_win DECIMAL(12,2) DEFAULT 0 COMMENT '实际中奖金额',
                status ENUM('pending', 'confirmed', 'settled', 'cancelled', 'won', 'lost') NOT NULL DEFAULT 'pending' COMMENT '订单状态',
                odds_snapshot JSON COMMENT '投注时的赔率快照',
                ip_address VARCHAR(45) COMMENT '投注IP地址',
                device_info TEXT COMMENT '设备信息',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                confirmed_at TIMESTAMP NULL COMMENT '确认时间',
                settled_at TIMESTAMP NULL COMMENT '结算时间',
                INDEX idx_user_id (user_id),
                INDEX idx_order_number (order_number),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at),
                INDEX idx_user_status_date (user_id, status, created_at),
                INDEX idx_match_status (match_id, status),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
                CHECK (bet_amount > 0),
                CHECK (potential_win >= 0)
            ) COMMENT='投注订单表'''
        },
        
        'payment_transactions': {
            'priority': '🔥 最高', 
            'description': '支付交易表 - 资金安全核心',
            'sql': '''CREATE TABLE IF NOT EXISTS payment_transactions (
                id BIGINT PRIMARY KEY AUTOINCREMENT COMMENT '主键ID',
                transaction_number VARCHAR(50) UNIQUE NOT NULL COMMENT '交易流水号',
                user_id BIGINT NOT NULL COMMENT '用户ID',
                order_id BIGINT COMMENT '关联订单ID',
                transaction_type ENUM('deposit', 'withdrawal', 'betting', 'winning', 'refund', 'bonus') NOT NULL COMMENT '交易类型',
                amount DECIMAL(12,2) NOT NULL COMMENT '交易金额',
                balance_before DECIMAL(12,2) NOT NULL COMMENT '交易前余额',
                balance_after DECIMAL(12,2) NOT NULL COMMENT '交易后余额',
                status ENUM('pending', 'processing', 'completed', 'failed', 'cancelled') NOT NULL DEFAULT 'pending' COMMENT '交易状态',
                payment_method VARCHAR(50) COMMENT '支付方式',
                external_transaction_id VARCHAR(100) COMMENT '外部交易ID',
                fee_amount DECIMAL(8,2) DEFAULT 0 COMMENT '手续费',
                remark TEXT COMMENT '备注',
                risk_level ENUM('low', 'medium', 'high') DEFAULT 'low' COMMENT '风险等级',
                processed_by BIGINT COMMENT '处理人员ID',
                ip_address VARCHAR(45) COMMENT '操作IP',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                processed_at TIMESTAMP NULL COMMENT '处理时间',
                completed_at TIMESTAMP NULL COMMENT '完成时间',
                INDEX idx_user_id (user_id),
                INDEX idx_transaction_number (transaction_number),
                INDEX idx_status (status),
                INDEX idx_type_status (transaction_type, status),
                INDEX idx_created_at (created_at),
                INDEX idx_external_id (external_transaction_id),
                INDEX idx_user_balance (user_id, balance_after),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (order_id) REFERENCES betting_orders(id) ON DELETE SET NULL,
                CHECK (amount != 0),
                CHECK (balance_after >= 0)
            ) COMMENT='支付交易表'''
        },
        
        'system_configs': {
            'priority': '🟡 高',
            'description': '系统配置表 - 运营管理必需', 
            'sql': '''CREATE TABLE IF NOT EXISTS system_configs (
                id INT PRIMARY KEY AUTOINCREMENT COMMENT '主键ID',
                config_key VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
                config_value TEXT COMMENT '配置值',
                config_type ENUM('string', 'number', 'boolean', 'json', 'array') NOT NULL DEFAULT 'string' COMMENT '配置类型',
                category VARCHAR(50) NOT NULL COMMENT '配置分类',
                description TEXT COMMENT '配置描述',
                is_public BOOLEAN DEFAULT FALSE COMMENT '是否公开',
                editable BOOLEAN DEFAULT TRUE COMMENT '是否可编辑',
                validation_rules JSON COMMENT '验证规则',
                default_value TEXT COMMENT '默认值',
                updated_by BIGINT COMMENT '更新人ID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_config_key (config_key),
                INDEX idx_category (category),
                INDEX idx_public (is_public),
                FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
            ) COMMENT='系统配置表'''
        },
        
        'notification_logs': {
            'priority': '🟢 中',
            'description': '通知日志表 - 用户体验支撑',
            'sql': '''CREATE TABLE IF NOT EXISTS notification_logs (
                id BIGINT PRIMARY KEY AUTOINCREMENT COMMENT '主键ID',
                user_id BIGINT NOT NULL COMMENT '用户ID',
                notification_type ENUM('email', 'sms', 'push', 'system', 'promotion') NOT NULL COMMENT '通知类型',
                title VARCHAR(200) NOT NULL COMMENT '通知标题',
                content TEXT NOT NULL COMMENT '通知内容',
                template_id BIGINT COMMENT '模板ID',
                variables JSON COMMENT '模板变量',
                status ENUM('pending', 'sent', 'delivered', 'failed', 'cancelled') NOT NULL DEFAULT 'pending' COMMENT '发送状态',
                send_method VARCHAR(50) COMMENT '发送方式',
                external_id VARCHAR(100) COMMENT '外部消息ID',
                retry_count INT DEFAULT 0 COMMENT '重试次数',
                max_retries INT DEFAULT 3 COMMENT '最大重试次数',
                error_message TEXT COMMENT '错误信息',
                scheduled_at TIMESTAMP NULL COMMENT '预定发送时间',
                sent_at TIMESTAMP NULL COMMENT '发送时间',
                delivered_at TIMESTAMP NULL COMMENT '送达时间',
                read_at TIMESTAMP NULL COMMENT '阅读时间',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                INDEX idx_user_id (user_id),
                INDEX idx_type_status (notification_type, status),
                INDEX idx_status_date (status, created_at),
                INDEX idx_scheduled_at (scheduled_at),
                INDEX idx_template_id (template_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (template_id) REFERENCES notification_templates(id) ON DELETE SET NULL
            ) COMMENT='通知日志表'''
        },
        
        'fraud_detection': {
            'priority': '🔥 高',
            'description': '反欺诈检测表 - 风控核心',
            'sql': '''CREATE TABLE IF NOT EXISTS fraud_detection (
                id BIGINT PRIMARY KEY AUTOINCREMENT COMMENT '主键ID',
                user_id BIGINT NOT NULL COMMENT '用户ID',
                detection_type ENUM('unusual_betting', 'rapid_orders', 'amount_anomaly', 'ip_change', 'device_change', 'multiple_accounts', 'collusion') NOT NULL COMMENT '检测类型',
                risk_score DECIMAL(5,2) NOT NULL COMMENT '风险评分(0-100)',
                risk_level ENUM('low', 'medium', 'high', 'critical') NOT NULL COMMENT '风险等级',
                trigger_data JSON NOT NULL COMMENT '触发数据',
                detection_rules JSON COMMENT '命中的检测规则',
                confidence_level DECIMAL(5,2) DEFAULT 0 COMMENT '置信度',
                status ENUM('detected', 'investigating', 'confirmed', 'false_positive', 'resolved') NOT NULL DEFAULT 'detected' COMMENT '处理状态',
                auto_action ENUM('none', 'block', 'limit', 'verify', 'freeze') DEFAULT 'none' COMMENT '自动处理动作',
                manual_action ENUM('none', 'block', 'limit', 'verify', 'freeze', 'warn') DEFAULT 'none' COMMENT '人工处理动作',
                handled_by BIGINT COMMENT '处理人员ID',
                handler_notes TEXT COMMENT '处理备注',
                expires_at TIMESTAMP NULL COMMENT '过期时间',
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '检测时间',
                handled_at TIMESTAMP NULL COMMENT '处理时间',
                resolved_at TIMESTAMP NULL COMMENT '解决时间',
                INDEX idx_user_id (user_id),
                INDEX idx_type_status (detection_type, status),
                INDEX idx_risk_level (risk_level),
                INDEX idx_risk_score (risk_score),
                INDEX idx_status_date (status, detected_at),
                INDEX idx_auto_action (auto_action),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (handled_by) REFERENCES users(id) ON DELETE SET NULL,
                CHECK (risk_score >= 0 AND risk_score <= 100)
            ) COMMENT='反欺诈检测表'''
        }
    }
    
    # 创建表
    success_count = 0
    total_count = len(core_tables)
    
    print("\n🎯 创建核心业务表...")
    
    for table_name, table_info in core_tables.items():
        try:
            print(f"\n[{success_count+1}/{total_count}] 创建表: {table_name}")
            print(f"优先级: {table_info['priority']}")
            print(f"说明: {table_info['description']}")
            
            cursor.execute(table_info['sql'])
            print(f"✅ {table_name} 创建成功")
            success_count += 1
            
        except Exception as e:
            if "already exists" in str(e):
                print(f"ℹ️  {table_name} 表已存在")
                success_count += 1
            else:
                print(f"❌ {table_name} 创建失败: {str(e)[:100]}")
    
    # 插入系统配置初始数据
    print("\n📊 插入系统配置初始数据...")
    init_configs = [
        ('site_name', '体育彩票扫盘系统', 'string', 'system', '网站名称', 1, 1, '', '体育彩票扫盘系统'),
        ('maintenance_mode', 'false', 'boolean', 'system', '维护模式', 0, 1, '', 'false'),
        ('max_bet_amount', '10000', 'number', 'betting', '单笔最大投注金额', 0, 1, '{"min": 1, "max": 999999}', '10000'),
        ('min_deposit', '10', 'number', 'payment', '最小充值金额', 0, 1, '{"min": 1, "max": 1000}', '10'),
        ('max_withdrawal_daily', '50000', 'number', 'payment', '每日最大提现金额', 0, 1, '{"min": 100, "max": 999999}', '50000'),
        ('fraud_detection_enabled', 'true', 'boolean', 'security', '欺诈检测开关', 0, 1, '', 'true'),
        ('session_timeout', '3600', 'number', 'security', '会话超时时间(秒)', 0, 1, '{"min": 300, "max": 86400}', '3600'),
        ('welcome_bonus', '100', 'number', 'promotion', '新用户注册奖励', 1, 1, '{"min": 0, "max": 1000}', '100'),
        ('daily_bonus_max', '50', 'number', 'promotion', '每日签到奖励上限', 1, 1, '{"min": 0, "max": 500}', '50'),
        ('email_notification', 'true', 'boolean', 'notification', '邮件通知开关', 1, 1, '', 'true')
    ]
    
    try:
        cursor.executemany(
            "INSERT OR IGNORE INTO system_configs (config_key, config_value, config_type, category, description, is_public, editable, default_value) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            init_configs
        )
        print(f"✅ 插入 {len(init_configs)} 条系统配置")
    except Exception as e:
        print(f"❌ 系统配置插入失败: {e}")
    
    # 创建通知模板表(依赖表)
    print("\n📧 创建通知模板表...")
    notification_templates_sql = '''
    CREATE TABLE IF NOT EXISTS notification_templates (
        id BIGINT PRIMARY KEY AUTOINCREMENT COMMENT '主键ID',
        template_name VARCHAR(100) NOT NULL COMMENT '模板名称',
        template_type ENUM('email', 'sms', 'push', 'system') NOT NULL COMMENT '模板类型',
        subject VARCHAR(200) COMMENT '邮件主题',
        template_content TEXT NOT NULL COMMENT '模板内容',
        variables JSON COMMENT '可用变量',
        is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
    ) COMMENT='通知模板表'''
    
    try:
        cursor.execute(notification_templates_sql)
        print("✅ notification_templates 表创建成功")
        
        # 插入默认模板
        default_templates = [
            ('welcome_email', 'email', '欢迎加入体育彩票扫盘系统', '亲爱的{{username}}，欢迎加入我们的平台！您的账户已成功创建。', '{"username": "用户名"}', 1),
            ('bet_confirmation', 'email', '投注确认 - {{order_number}}', '您的投注订单{{order_number}}已确认，投注金额{{amount}}元。', '{"order_number": "订单号", "amount": "投注金额"}', 1),
            ('deposit_success', 'email', '充值成功 - {{amount}}元', '您的充值{{amount}}元已成功到账，当前余额{{balance}}元。', '{"amount": "充值金额", "balance": "当前余额"}', 1),
            ('login_alert', 'email', '登录提醒', '检测到您的账户在新设备登录，IP: {{ip_address}}，时间: {{login_time}}', '{"ip_address": "IP地址", "login_time": "登录时间"}', 1)
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO notification_templates (template_name, template_type, subject, template_content, variables, is_active) VALUES (?, ?, ?, ?, ?, ?)",
            default_templates
        )
        print(f"✅ 插入 {len(default_templates)} 条通知模板")
        
    except Exception as e:
        print(f"❌ 通知模板表创建失败: {e}")
    
    # 验证表创建结果
    print("\n🔍 验证表创建结果...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('betting_orders', 'payment_transactions', 'system_configs', 'notification_logs', 'fraud_detection') ORDER BY name")
    created_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"✅ 成功创建 {len(created_tables)} 个核心业务表:")
    for table in created_tables:
        print(f"   • {table}")
    
    missing_tables = [name for name in core_tables.keys() if name not in created_tables]
    if missing_tables:
        print(f"❌ 未创建的表: {', '.join(missing_tables)}")
    
    # 检查表记录数
    print("\n📊 表记录统计:")
    for table_name in created_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   • {table_name}: {count} 条记录")
        except Exception as e:
            print(f"   • {table_name}: 查询失败 ({e})")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 核心业务表创建完成!")
    print(f"📊 成功率: {success_count}/{total_count}")
    print(f"🚀 系统功能完整性大幅提升!")
    
    return success_count == total_count

if __name__ == "__main__":
    create_missing_core_tables()