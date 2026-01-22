#!/usr/bin/env python3
"""
批量修复测试文件中的导入路径问题
将 'from backend.app.scrapers' 替换为 'from backend.scrapers'
"""

import os
import glob
import re

def fix_import_paths():
    """修复所有测试文件中的导入路径"""
    # 获取所有测试文件
    test_files = glob.glob("tests/backend/unit/*.py")
    
    fixed_count = 0
    for file_path in test_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含需要修复的导入
            if 'backend.app.scrapers' in content:
                # 替换导入路径
                new_content = content.replace('backend.app.scrapers', 'backend.scrapers')
                
                # 写回文件
                with open(file_path, 'w', encoding=' utf-8') as f:
                    f.write(new_content)
                
                print(f"✓ 修复了: {file_path}")
                fixed_count += 1
            else:
                print(f"- 跳过: {file_path} (无需修复)")
                
        except Exception as e:
            print(f"✗ 修复失败 {file_path}: {e}")
    
    print(f"\n总共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    fix_import_paths()