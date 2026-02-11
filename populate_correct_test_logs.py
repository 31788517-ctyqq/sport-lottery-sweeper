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
        ("2026-01-30 10:30:00", "login", "admin", "1", "Admin Login", "POST", "/api/login", "{}", "", 200, "", "192.168.1.100", "Mozilla/5.0 Test Browser", "", "", 100),
        ("2026-01-30 11:15:22", "logout", "admin", "2", "Admin Logout", "POST", "/api/logout", "{}", "", 200, "", "192.168.1.100", "Mozilla/5.0 Test Browser", "", "", 50),
        ("2026-01-30 14:20:10", "view", "user", "5", "View User List", "GET", "/api/users", "{}", "", 200, "", "192.168.1.101", "Mozilla/5.0 Test Browser", "", "", 200),
        ("2026-01-31 09:45:33", "update", "setting", "1", "Update Settings", "PUT", "/api/settings/1", "{}", "", 200, "", "192.168.1.100", "Mozilla/5.0 Test Browser", "", "", 150),
        ("2026-01-31 16:30:45", "access", "report", "3", "Generate Report", "POST", "/api/reports/generate", "{}", "", 200, "", "192.168.1.102", "Mozilla/5.0 Test Browser", "", "", 300)
    ]
    
    for log in user_operations:
        cursor.execute("""
            INSERT INTO admin_operation_logs 
            (admin_id, action, resource_type, resource_id, resource_name, method, path, 
             query_params, request_body, status_code, response_data, ip_address, user_agent, 
             changes_before, changes_after, duration_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (random.randint(1, 5), log[1], log[2], log[3], log[4], log[5], log[6], 
               log[7], log[8], log[9], log[10], log[11], log[12], log[13], log[14], log[15], log[0]))
    
    print(f"Inserted {len(user_operations)} user operation logs")
    
    # 插入一些安全日志
    security_logs = [
        ("2026-01-30 10:30:05", 1, "192.168.1.100", "Mozilla/5.0 Test Browser", 1, None, "CN", "Beijing", "Beijing", "Desktop", "Windows", "Chrome", 0, 1),
        ("2026-01-30 11:45:12", 2, "192.168.1.101", "Mozilla/5.0 Test Browser", 0, "Invalid credentials", "US", "California", "San Francisco", "Mobile", "iOS", "Safari", 0, 1),
        ("2026-01-30 15:22:30", 3, "192.168.1.102", "Mozilla/5.0 Test Browser", 1, None, "JP", "Tokyo", "Tokyo", "Desktop", "MacOS", "Firefox", 1, 1),
        ("2026-01-31 08:15:44", 4, "192.168.1.103", "Mozilla/5.0 Test Browser", 1, None, "KR", "Seoul", "Seoul", "Tablet", "Android", "Chrome", 0, 0),
        ("2026-01-31 12:31:00", 5, "192.168.1.104", "Mozilla/5.0 Test Browser", 0, "Account locked", "DE", "Berlin", "Berlin", "Desktop", "Linux", "Edge", 0, 1)
    ]
    
    for log in security_logs:
        cursor.execute("""
            INSERT INTO admin_login_logs 
            (admin_id, login_at, login_ip, user_agent, success, failure_reason, 
             country, region, city, device_type, os, browser, two_factor_used, ip_whitelisted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (log[1], log[0], log[2], log[3], log[4], log[5], log[6], log[7], log[8], 
               log[9], log[10], log[11], log[12], log[13]))
    
    print(f"Inserted {len(security_logs)} security logs")
    
    # 插入一些API日志
    api_logs = [
        ("2026-01-30 10:31:10", 1, 1, "completed", "2026-01-30 10:31:15", 5.2, 100, 95, 5, None, None, 120.5, 1, "2026-01-30 10:31:10"),
        ("2026-01-30 11:46:15", 2, 2, "completed", "2026-01-30 11:46:22", 7.1, 50, 50, 0, None, None, 85.3, 2, "2026-01-30 11:46:15"),
        ("2026-01-30 15:23:35", 3, 3, "failed", "2026-01-30 15:23:40", 5.0, 25, 0, 25, "Connection timeout", '{"error": "timeout"}', 150.2, 3, "2026-01-30 15:23:35"),
        ("2026-01-31 08:16:50", 4, 4, "completed", "2026-01-31 08:16:55", 5.1, 80, 80, 0, None, None, 92.7, 4, "2026-01-31 08:16:50"),
        ("2026-01-31 12:31:00", 5, 5, "completed", "2026-01-31 12:31:08", 8.2, 120, 118, 2, None, None, 110.8, 5, "2026-01-31 12:31:00")
    ]
    
    for log in api_logs:
        cursor.execute("""
            INSERT INTO crawler_task_logs 
            (task_id, source_id, status, started_at, completed_at, duration_seconds, 
             records_processed, records_success, records_failed, error_message, error_details, 
             response_time_ms, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (log[1], log[2], log[3], log[0], log[4], log[5], log[6], log[7], log[8], 
               log[9], log[10], log[11], log[12], log[13]))
    
    print(f"Inserted {len(api_logs)} API logs")
    
    conn.commit()
    conn.close()
    
    print("Test log data populated successfully!")

if __name__ == "__main__":
    populate_test_logs()