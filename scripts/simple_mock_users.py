"""
简化版模拟数据生成脚本
直接向数据库插入数据，避免模型定义冲突
"""

import sqlite3
import hashlib
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid

fake = Faker('zh_CN')

# 模拟数据标识，便于后续清理
MOCK_DATA_TAG = "mock_data_2026_01_19"

def hash_password(password):
    """简单的密码哈希函数，仅用于演示"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_mock_data():
    """创建模拟数据"""
    print("开始创建模拟数据...")
    
    # 连接数据库
    conn = sqlite3.connect('../sport_lottery.db')
    cursor = conn.cursor()
    
    try:
        # 创建必要的表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                real_name TEXT NOT NULL,
                phone TEXT,
                department TEXT,
                position TEXT,
                role TEXT DEFAULT 'operator',
                status TEXT DEFAULT 'inactive',
                two_factor_enabled BOOLEAN DEFAULT 0,
                is_verified BOOLEAN DEFAULT 0,
                login_count INTEGER DEFAULT 0,
                last_login_at TIMESTAMP,
                last_login_ip TEXT,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                must_change_password BOOLEAN DEFAULT 1,
                created_by INTEGER,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                nickname TEXT,
                bio TEXT,
                avatar_url TEXT,
                phone TEXT,
                country TEXT,
                city TEXT,
                role TEXT DEFAULT 'regular_user',
                status TEXT DEFAULT 'active',
                is_verified BOOLEAN DEFAULT 0,
                is_online BOOLEAN DEFAULT 0,
                user_type TEXT DEFAULT 'normal',
                timezone TEXT DEFAULT 'UTC',
                language TEXT DEFAULT 'zh',
                login_count INTEGER DEFAULT 0,
                last_login_at TIMESTAMP,
                last_activity_at TIMESTAMP,
                followers_count INTEGER DEFAULT 0,
                following_count INTEGER DEFAULT 0,
                external_id TEXT,
                external_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT,
                resource_name TEXT,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                query_params TEXT,
                request_body TEXT,
                status_code INTEGER NOT NULL,
                response_data TEXT,
                ip_address TEXT NOT NULL,
                user_agent TEXT,
                changes_before TEXT,
                changes_after TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_ms INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                login_ip TEXT NOT NULL,
                user_agent TEXT,
                success BOOLEAN DEFAULT 1,
                failure_reason TEXT,
                country TEXT,
                region TEXT,
                city TEXT,
                device_type TEXT,
                os TEXT,
                browser TEXT,
                two_factor_used BOOLEAN DEFAULT 0,
                ip_whitelisted BOOLEAN DEFAULT 0
            )
        """)
        
        # 插入超级管理员
        super_admin_data = (
            f"sa_{MOCK_DATA_TAG}",
            f"sa_{MOCK_DATA_TAG}@example.com",
            hash_password("SuperAdmin@123456"),
            "超级管理员",
            fake.phone_number(),
            "技术部",
            "系统管理员",
            "super_admin",
            "active",
            1,  # two_factor_enabled
            1,  # is_verified
            0,  # login_count
            None,  # last_login_at
            None,  # last_login_ip
            0,  # failed_login_attempts
            None,  # locked_until
            0,  # must_change_password
            None,  # created_by
            "模拟超级管理员账户",
            datetime.now()
        )
        
        cursor.execute("""
            INSERT OR IGNORE INTO admin_users 
            (username, email, password_hash, real_name, phone, department, position, 
             role, status, two_factor_enabled, is_verified, login_count, 
             last_login_at, last_login_ip, failed_login_attempts, locked_until, 
             must_change_password, created_by, remarks, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, super_admin_data)
        
        conn.commit()
        
        # 获取超级管理员ID
        cursor.execute("SELECT id FROM admin_users WHERE username = ?", (f"sa_{MOCK_DATA_TAG}",))
        super_admin_result = cursor.fetchone()
        if super_admin_result:
            super_admin_id = super_admin_result[0]
        else:
            # 如果没插入成功，查询已有记录
            cursor.execute("SELECT id FROM admin_users WHERE username LIKE ?", (f"%{MOCK_DATA_TAG}%",))
            result = cursor.fetchone()
            super_admin_id = result[0] if result else 1
        
        print(f"超级管理员ID: {super_admin_id}")
        
        # 插入其他管理员
        roles = ['admin', 'moderator', 'auditor', 'operator']
        statuses = ['active', 'inactive', 'suspended', 'locked']
        departments = ['技术部', '运营部', '客服部', '审计部']
        
        admin_ids = []
        for i in range(10):
            role = random.choice(roles)
            status = random.choice(statuses)
            department = random.choice(departments)
            
            admin_data = (
                f"admin_{i}_{MOCK_DATA_TAG}",
                f"admin{i}_{MOCK_DATA_TAG}@example.com",
                hash_password("Admin@123456"),
                fake.name(),
                fake.phone_number(),
                department,
                random.choice(['主管', '专员', '经理', '总监']),
                role,
                status,
                random.choice([0, 1]),  # two_factor_enabled
                1,  # is_verified
                random.randint(0, 100),  # login_count
                fake.date_time_between(start_date="-30d", end_date="now").isoformat(),  # last_login_at
                fake.ipv4(),  # last_login_ip
                random.randint(0, 5),  # failed_login_attempts
                None,  # locked_until
                random.choice([0, 1]),  # must_change_password
                super_admin_id,  # created_by
                f"模拟{role}账户",
                datetime.now()
            )
            
            cursor.execute("""
                INSERT OR IGNORE INTO admin_users 
                (username, email, password_hash, real_name, phone, department, position, 
                 role, status, two_factor_enabled, is_verified, login_count, 
                 last_login_at, last_login_ip, failed_login_attempts, locked_until, 
                 must_change_password, created_by, remarks, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, admin_data)
            
            # 记录ID以便后续插入日志
            cursor.execute("SELECT id FROM admin_users WHERE username = ?", (f"admin_{i}_{MOCK_DATA_TAG}",))
            result = cursor.fetchone()
            if result:
                admin_ids.append(result[0])
        
        conn.commit()
        print(f"成功创建11个后台管理用户")
        
        # 插入操作日志
        actions = ["create", "read", "update", "delete", "login", "logout"]
        resources = ["user", "match", "intelligence", "config", "log"]
        
        for admin_id in admin_ids:
            for _ in range(random.randint(5, 20)):
                log_data = (
                    admin_id,
                    random.choice(actions),
                    random.choice(resources),
                    str(random.randint(1, 100)),
                    fake.word(),
                    random.choice(["GET", "POST", "PUT", "DELETE"]),
                    f"/api/v1/admin/{random.choice(resources)}/{random.randint(1, 100)}",
                    "{}",  # query_params
                    "{}",  # request_body
                    random.choice([200, 201, 400, 403, 404, 500]),
                    "{}",  # response_data
                    fake.ipv4(),
                    fake.user_agent(),
                    "{}",  # changes_before
                    "{}",  # changes_after
                    fake.date_time_between(start_date="-30d", end_date="now").isoformat(),
                    random.randint(10, 500)  # duration_ms
                )
                
                cursor.execute("""
                    INSERT INTO admin_operation_logs 
                    (admin_id, action, resource_type, resource_id, resource_name, 
                     method, path, query_params, request_body, status_code, 
                     response_data, ip_address, user_agent, changes_before, 
                     changes_after, created_at, duration_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, log_data)
        
        conn.commit()
        total_ops = sum(random.randint(5, 20) for _ in admin_ids)
        print(f"成功创建约{total_ops}条操作日志")
        
        # 插入登录日志
        for admin_id in admin_ids:
            for _ in range(random.randint(3, 15)):
                login_data = (
                    admin_id,
                    fake.date_time_between(start_date="-30d", end_date="now").isoformat(),
                    fake.ipv4(),
                    fake.user_agent(),
                    random.choice([True, False]),
                    None if random.choice([True, False]) else "Invalid credentials",
                    fake.country()[:50] if fake.country() else None,
                    None,  # region - 修复区域字段
                    fake.city()[:50] if fake.city() else None,
                    random.choice(["desktop", "mobile", "tablet"]),
                    random.choice(["Windows", "MacOS", "Linux", "iOS", "Android"]),
                    random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                    random.choice([True, False]),
                    random.choice([True, False])
                )
                
                cursor.execute("""
                    INSERT INTO admin_login_logs 
                    (admin_id, login_at, login_ip, user_agent, success, failure_reason,
                     country, region, city, device_type, os, browser, 
                     two_factor_used, ip_whitelisted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, login_data)
        
        conn.commit()
        total_logins = sum(random.randint(3, 15) for _ in admin_ids)
        print(f"成功创建约{total_logins}条登录日志")
        
        # 插入前台用户
        user_types = ['normal', 'premium', 'analyst']
        user_statuses = ['active', 'inactive', 'suspended', 'banned']
        
        print("开始创建前台用户...")
        created_users_count = 0
        for i in range(10):
            user_type = random.choice(user_types)
            status = random.choice(user_statuses)
            
            user_data = (
                f"user_{i}_{MOCK_DATA_TAG}",
                f"user{i}_{MOCK_DATA_TAG}@example.com",
                hash_password("User@123456"),
                fake.first_name(),
                fake.last_name(),
                fake.user_name(),
                fake.text(max_nb_chars=100)[:200],
                f"https://example.com/avatar/{str(uuid.uuid4())}.jpg",
                fake.phone_number(),
                "中国",
                fake.city(),
                "regular_user",
                status,
                random.choice([0, 1]),
                random.choice([0, 1]),
                user_type,
                "Asia/Shanghai",
                "zh-CN",
                random.randint(0, 100),
                fake.date_time_between(start_date="-30d", end_date="now").isoformat(),
                fake.date_time_between(start_date="-30d", end_date="now").isoformat(),
                random.randint(0, 1000),
                random.randint(0, 500),
                str(uuid.uuid4()),
                "registration",
                datetime.now()
            )
            
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO users 
                    (username, email, password_hash, first_name, last_name, nickname, 
                     bio, avatar_url, phone, country, city, role, status, 
                     is_verified, is_online, user_type, timezone, language, 
                     login_count, last_login_at, last_activity_at, 
                     followers_count, following_count, external_id, external_source, 
                     created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, user_data)
                
                if cursor.rowcount > 0:  # 如果插入成功
                    created_users_count += 1
            except sqlite3.Error as e:
                print(f"插入用户时出错 (user_{i}_{MOCK_DATA_TAG}): {e}")
        
        conn.commit()
        print(f"成功创建{created_users_count}个前台用户")
        
        print("\n所有模拟数据创建完成！")
        print(f"标识符: {MOCK_DATA_TAG}")
        print("如需清理数据，可运行: python simple_mock_users.py cleanup")
        
    except Exception as e:
        print(f"创建模拟数据时出错: {e}")
        conn.rollback()
    finally:
        conn.close()


def cleanup_mock_data():
    """清理模拟数据"""
    print("开始清理模拟数据...")
    
    # 连接数据库
    conn = sqlite3.connect('../sport_lottery.db')
    cursor = conn.cursor()
    
    try:
        # 删除后台用户相关数据
        cursor.execute("DELETE FROM admin_operation_logs WHERE admin_id IN (SELECT id FROM admin_users WHERE username LIKE ?)", (f'%{MOCK_DATA_TAG}%',))
        cursor.execute("DELETE FROM admin_login_logs WHERE admin_id IN (SELECT id FROM admin_users WHERE username LIKE ?)", (f'%{MOCK_DATA_TAG}%',))
        cursor.execute("DELETE FROM admin_users WHERE username LIKE ?", (f'%{MOCK_DATA_TAG}%',))
        
        # 删除前台用户
        cursor.execute("DELETE FROM users WHERE username LIKE ?", (f'%{MOCK_DATA_TAG}%',))
        
        conn.commit()
        print("模拟数据清理完成！")
        
    except Exception as e:
        print(f"清理模拟数据时出错: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "create"
    
    if action == "create":
        create_mock_data()
    elif action == "cleanup":
        cleanup_mock_data()
    else:
        print("无效操作，请使用 'create' 或 'cleanup'")