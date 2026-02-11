#!/usr/bin/env python3
"""测试数据库CRUD函数"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_crud_operations():
    """测试CRUD操作"""
    try:
        print("正在测试CRUD操作...")
        
        # 导入必要的模块
        from backend.database import SessionLocal
        from backend.crud.crud_caipiao_data import (
            get_caipiao_data_list, 
            get_caipiao_data_count
        )
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 测试获取列表
            print("正在测试 get_caipiao_data_list...")
            data_list = get_caipiao_data_list(db, skip=0, limit=20)
            print(f"✅ 获取到 {len(data_list)} 条数据")
            
            # 测试计数
            print("正在测试 get_caipiao_data_count...")
            count = get_caipiao_data_count(db)
            print(f"✅ 总共 {count} 条数据")
            
            print("✅ CRUD操作测试通过")
            
        finally:
            db.close()
            
        return True
        
    except Exception as e:
        print(f"❌ CRUD操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始CRUD测试...")
    
    if test_crud_operations():
        print("\n🎉 CRUD测试通过！")
    else:
        print("\n💥 CRUD测试失败！")