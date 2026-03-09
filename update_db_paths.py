#!/usr/bin/env python3
"""
批量更新数据库路径脚本
将项目中所有硬编码的数据库路径从 'sport_lottery.db' 或 'backend/sport_lottery.db' 
更新为 'data/sport_lottery.db'
"""

import os
import re
import sys
from pathlib import Path

def update_file(file_path):
    """更新单个文件中的数据库路径"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 模式1: 单引号包裹的 'sport_lottery.db'，但不包含 'data/'
        pattern1 = r"'sport_lottery\.db'"
        if re.search(pattern1, content) and "'data/sport_lottery.db'" not in content:
            content = re.sub(pattern1, "'data/sport_lottery.db'", content)
        
        # 模式2: 双引号包裹的 "sport_lottery.db"，但不包含 "data/"
        pattern2 = r'"sport_lottery\.db"'
        if re.search(pattern2, content) and '"data/sport_lottery.db"' not in content:
            content = re.sub(pattern2, '"data/sport_lottery.db"', content)
        
        # 模式3: backend/sport_lottery.db 路径
        pattern3 = r'backend/sport_lottery\.db'
        if re.search(pattern3, content, re.IGNORECASE):
            # 根据文件位置计算正确的相对路径
            file_dir = os.path.dirname(file_path)
            # 简单替换为 data/sport_lottery.db
            content = re.sub(pattern3, 'data/sport_lottery.db', content, flags=re.IGNORECASE)
        
        # 模式4: os.path.join 或 Path 连接中的 'sport_lottery.db'
        pattern4 = r"(os\.path\.join\([^)]*|Path\([^)]*|/|\\\\)\s*['\"]sport_lottery\.db['\"]"
        # 这个更复杂，需要更精确的处理
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  错误: {e}")
        return False

def find_files_to_update(root_dir):
    """查找需要更新的文件"""
    files_to_update = []
    
    # 搜索所有Python文件
    for root, dirs, files in os.walk(root_dir):
        # 排除一些目录
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', 'venv', '.venv']]
        
        for file in files:
            if file.endswith('.py') or file.endswith('.bat') or file.endswith('.ps1') or file.endswith('.js'):
                file_path = os.path.join(root, file)
                files_to_update.append(file_path)
    
    return files_to_update

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"项目根目录: {project_root}")
    print("开始搜索需要更新的文件...")
    
    files_to_update = find_files_to_update(project_root)
    print(f"找到 {len(files_to_update)} 个文件需要检查")
    
    updated_count = 0
    for i, file_path in enumerate(files_to_update):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 检查是否包含数据库路径模式
            patterns = [
                r"'sport_lottery\.db'",
                r'"sport_lottery\.db"',
                r'backend/sport_lottery\.db',
                r'backend\\\\sport_lottery\.db',
                r'backend/sport_lottery\.db',
            ]
            
            has_pattern = any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
            has_correct_path = ('data/sport_lottery.db' in content) or ('data\\\\sport_lottery.db' in content)
            
            if has_pattern and not has_correct_path:
                print(f"[{i+1}/{len(files_to_update)}] 需要更新: {os.path.relpath(file_path, project_root)}")
                # 尝试更新
                try:
                    updated = update_file(file_path)
                    if updated:
                        updated_count += 1
                        print(f"    已更新")
                    else:
                        print(f"    未更新（可能格式不匹配）")
                except Exception as e:
                    print(f"    更新失败: {e}")
        except Exception as e:
            # 跳过无法读取的文件
            continue
    
    print(f"\n更新完成！共更新了 {updated_count} 个文件")
    
    # 最后检查一些关键文件
    print("\n检查关键文件:")
    key_files = [
        'backend/config.py',
        'backend/database.py',
        'backend/config_fixed.py',
        'scripts/batch/test_db_data.bat',
        'scripts/batch/restart_backend_force.bat',
        'step1_init.bat',
    ]
    
    for key_file in key_files:
        file_path = os.path.join(project_root, key_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'data/sport_lottery.db' in content or 'data\\\\sport_lottery.db' in content:
                    print(f"  ✓ {key_file}: 使用正确路径")
                elif 'sport_lottery.db' in content:
                    print(f"  ✗ {key_file}: 仍包含硬编码路径")
                else:
                    print(f"  ? {key_file}: 未找到数据库路径引用")
            except:
                print(f"  ! {key_file}: 无法读取")

if __name__ == "__main__":
    main()