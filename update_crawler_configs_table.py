import sqlite3
from backend.database import engine
from sqlalchemy import text

def update_crawler_configs_table():
    """
    检查并更新crawler_configs表结构，确保包含source_id列
    """
    print("正在检查crawler_configs表结构...")
    
    # 使用SQLAlchemy引擎连接数据库
    with engine.connect() as conn:
        # 检查表中是否已有source_id列
        result = conn.execute(text("""
            SELECT name FROM pragma_table_info('crawler_configs') 
            WHERE name = 'source_id';
        """))
        
        existing_column = result.fetchone()
        
        if existing_column:
            print("✓ crawler_configs表已包含source_id列")
        else:
            print("× crawler_configs表缺少source_id列，正在添加...")
            
            # 添加source_id列
            try:
                conn.execute(text("""
                    ALTER TABLE crawler_configs 
                    ADD COLUMN source_id INTEGER REFERENCES data_sources(id);
                """))
                
                # 提交事务
                conn.commit()
                
                print("✓ 成功添加source_id列到crawler_configs表")
            except Exception as e:
                print(f"✗ 添加source_id列失败: {e}")
                return False
    
    return True

if __name__ == "__main__":
    update_crawler_configs_table()