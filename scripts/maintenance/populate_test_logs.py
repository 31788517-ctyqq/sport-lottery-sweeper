import sqlite3
from datetime import datetime, timedelta
import random

def populate_test_logs():
    db_path = 'backend/sport_lottery.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Populating test log data...")
    
    # 插入一些用户操作日志
    user_operations = [
        ("2026-01-30 10:30:00", "INFO", "UserLogin", "User john_doe logged in successfully"),
        ("2026-01-30 11:15:22", "INFO", "UserLogout", "User john_doe logged out"),
        ("2026-01-30 14:20:10", "INFO", "DataAccess", "User jane_smith accessed user management"),
        ("2026-01-31 09:45:33", "INFO", "SettingsUpdate", "User admin updated system settings"),
        ("2026-01-31 16:30:45", "WARN", "FailedLogin", "Multiple failed login attempts for user test_user")
    ]
    
    for log in user_operations:
        cursor.execute("""
            INSERT INTO admin_operation_logs (timestamp, level, module, message, user_id, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (log[0], log[1], log[2], log[3], random.randint(1, 10), "192.168.1."+str(random.randint(1, 254)), "Mozilla/5.0 Test Agent"))
    
    print(f"Inserted {len(user_operations)} user operation logs")
    
    # 插入一些安全日志
    security_logs = [
        ("2026-01-30 10:30:05", "INFO", "SuccessfulLogin", "Admin user logged in from 192.168.1.100"),
        ("2026-01-30 11:45:12", "WARN", "SuspiciousActivity", "Multiple failed login attempts detected"),
        ("2026-01-30 15:22:30", "INFO", "PasswordChange", "User password changed successfully"),
        ("2026-01-31 08:15:44", "INFO", "SessionTimeout", "User session expired due to inactivity"),
        ("2026-01-31 12:30:55", "CRITICAL", "SecurityBreach", "Unauthorized access attempt detected")
    ]
    
    for log in security_logs:
        cursor.execute("""
            INSERT INTO admin_login_logs (login_at, level, module, message, username, ip_address, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (log[0], log[1], log[2], log[3], "admin", "192.168.1."+str(random.randint(1, 254)), random.choice([True, False])))
    
    print(f"Inserted {len(security_logs)} security logs")
    
    # 插入一些API日志
    api_logs = [
        ("2026-01-30 10:31:10", "INFO", "APIRequest", "GET /api/users called by client app", 200),
        ("2026-01-30 11:46:15", "INFO", "APIRequest", "POST /api/data submitted", 201),
        ("2026-01-30 15:23:35", "WARN", "APIWarning", "Slow response from external service", 200),
        ("2026-01-31 08:16:50", "INFO", "APIRequest", "DELETE /api/users/123 processed", 200),
        ("2026-01-31 12:31:00", "ERROR", "APIError", "Internal server error in payment endpoint", 500)
    ]
    
    for log in api_logs:
        cursor.execute("""
            INSERT INTO crawler_task_logs (started_at, level, module, message, status, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (log[0], log[1], log[2], log[3], log[4], random.randint(100, 5000)))
    
    print(f"Inserted {len(api_logs)} API logs")
    
    conn.commit()
    conn.close()
    
    print("Test log data populated successfully!")

if __name__ == "__main__":
    populate_test_logs()