"""
手动创建部门表
"""
import sqlite3
from datetime import datetime


def create_department_table():
    # 连接到数据库
    conn = sqlite3.connect('./sport_lottery.db')
    cursor = conn.cursor()
    
    # 检查表是否已存在
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='departments';
    """)
    
    if cursor.fetchone():
        print("部门表已存在")
        conn.close()
        return
    
    # 创建部门表
    create_table_sql = """
    CREATE TABLE departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        parent_id INTEGER,
        description TEXT,
        leader_id INTEGER,
        status BOOLEAN DEFAULT 1 NOT NULL,
        sort_order INTEGER DEFAULT 0 NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP NULL,
        FOREIGN KEY (parent_id) REFERENCES departments(id) ON DELETE SET NULL,
        FOREIGN KEY (leader_id) REFERENCES admin_users(id) ON DELETE SET NULL
    );
    """
    
    try:
        cursor.execute(create_table_sql)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_departments_parent_id ON departments(parent_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_departments_status ON departments(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_departments_name ON departments(name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_departments_deleted_at ON departments(deleted_at);")
        
        # 创建检查约束（SQLite不直接支持，用触发器代替）
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS check_not_self_parent 
        BEFORE INSERT ON departments 
        BEGIN 
            SELECT CASE 
                WHEN NEW.id = NEW.parent_id THEN 
                    RAISE(ABORT, 'A department cannot be its own parent') 
            END; 
        END;
        """)
        
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS check_not_self_parent_update 
        BEFORE UPDATE ON departments 
        BEGIN 
            SELECT CASE 
                WHEN NEW.id = NEW.parent_id THEN 
                    RAISE(ABORT, 'A department cannot be its own parent') 
            END; 
        END;
        """)
        
        conn.commit()
        print("部门表创建成功")
        
    except Exception as e:
        print(f"创建部门表失败: {e}")
        conn.rollback()
    finally:
        conn.close()


def update_admin_users_table():
    """更新admin_users表，添加department_id字段"""
    conn = sqlite3.connect('./sport_lottery.db')
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(admin_users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'department_id' not in columns:
            # 添加department_id字段
            cursor.execute("ALTER TABLE admin_users ADD COLUMN department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL;")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_admin_users_department_id ON admin_users(department_id);")
            print("admin_users表已更新，添加department_id字段")
        else:
            print("admin_users表已有department_id字段")
        
        conn.commit()
    except Exception as e:
        print(f"更新admin_users表失败: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    create_department_table()
    update_admin_users_table()
    print("部门管理数据库结构更新完成")