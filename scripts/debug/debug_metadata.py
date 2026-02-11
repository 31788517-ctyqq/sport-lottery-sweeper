#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def debug_metadata():
    """调试Base.metadata"""
    # 导入所有模型
    from backend.models.admin_user import AdminUser
    from backend.models.department import Department
    
    # 导入正确的Base
    from backend.models.base import Base
    
    print("Base.metadata.tables keys:")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"  - {table_name}")
    
    print(f"\nAdminUser.__tablename__: {AdminUser.__tablename__}")
    print(f"AdminUser in Base.metadata.tables: {AdminUser.__tablename__ in Base.metadata.tables}")

if __name__ == "__main__":
    debug_metadata()