#!/usr/bin/env python3
"""
Ensure admin_users table contains all columns required by AdminUser model.
This is a lightweight SQLite migration to unblock login in dev environments.
"""
import sqlite3


DB_PATH = "sport_lottery.db"


REQUIRED_COLUMNS = [
    ("real_name", "TEXT", "''"),
    ("phone", "TEXT", "NULL"),
    ("department", "TEXT", "NULL"),
    ("position", "TEXT", "NULL"),
    ("two_factor_enabled", "INTEGER", "0"),
    ("two_factor_secret", "TEXT", "NULL"),
    ("login_allowed_ips", "TEXT", "NULL"),
    ("password_expires_at", "TEXT", "NULL"),
    ("must_change_password", "INTEGER", "1"),
    ("is_verified", "INTEGER", "0"),
    ("failed_login_attempts", "INTEGER", "0"),
    ("last_failed_login_at", "TEXT", "NULL"),
    ("locked_until", "TEXT", "NULL"),
    ("last_login_at", "TEXT", "NULL"),
    ("last_login_ip", "TEXT", "NULL"),
    ("created_by", "INTEGER", "NULL"),
    ("remarks", "TEXT", "NULL"),
    ("preferences", "TEXT", "'{}'"),
    ("created_at", "TEXT", "NULL"),
    ("updated_at", "TEXT", "NULL"),
    ("updated_by", "INTEGER", "NULL"),
    ("deleted_by", "INTEGER", "NULL"),
    ("department_id", "INTEGER", "NULL"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info('admin_users')")
        existing = {row[1] for row in cur.fetchall()}

        for name, col_type, default in REQUIRED_COLUMNS:
            if name in existing:
                continue
            sql = f"ALTER TABLE admin_users ADD COLUMN {name} {col_type} DEFAULT {default}"
            cur.execute(sql)
            print(f"Added column: {name}")

        # Ensure real_name has a value for existing rows
        cur.execute("UPDATE admin_users SET real_name = COALESCE(real_name, '')")
        conn.commit()
        print("admin_users schema ensured.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
