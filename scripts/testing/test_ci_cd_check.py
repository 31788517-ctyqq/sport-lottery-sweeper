#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟CI/CD数据库路径检查
验证能否捕获硬编码的数据库路径
"""

import os
import re
import subprocess
from pathlib import Path

def check_hardcoded_paths():
    """检查硬编码数据库路径"""
    print("[CHECK] 开始CI/CD数据库路径验证...")
    print("="*60)
    
    project_root = Path(__file__).parent
    
    # 定义要检查的文件类型和排除目录
    include_patterns = ['*.py', '*.bat', '*.sh']
    exclude_dirs = ['.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules']
    
    violations = []
    
    # 遍历所有文件
    for pattern in include_patterns:
        for file_path in project_root.rglob(pattern):
            # 跳过排除目录
            if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
                continue
                
            # 跳过测试文件本身
            if 'test_ci_cd_check.py' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    # 查找硬编码数据库路径的模式
                    # 匹配 sport_lottery.db 但不是注释中的
                    if re.search(r'sport_lottery\\.db', line, re.IGNORECASE):
                        # 排除注释行
                        stripped_line = line.strip()
                        if not stripped_line.startswith('#') and not stripped_line.startswith('//'):
                            # 排除正常的配置引用
                            if 'config' not in line.lower() and 'settings' not in line.lower():
                                violation = {
                                    'file': str(file_path),
                                    'line': line_num,
                                    'content': line.strip()
                                }
                                violations.append(violation)
                                print(f"[ERROR] 发现硬编码路径: {file_path}:{line_num}")
                                print(f"   内容: {line.strip()}")
                                
            except Exception as e:
                print(f"⚠️  读取文件失败 {file_path}: {e}")
    
    print("="*60)
    
    if violations:
        print(f"[FAIL] 检查失败: 发现 {len(violations)} 处硬编码数据库路径")
        print("\n建议修复方案:")
        print("1. 使用配置系统: from backend.config import settings")
        print("2. 使用数据库工具: from backend.database_utils import get_db_connection")
        print("3. 通过环境变量或配置文件指定数据库路径")
        return False
    else:
        print("[PASS] 检查通过: 未发现硬编码数据库路径")
        return True

def check_config_files():
    """检查配置文件中的数据库路径设置"""
    print("\n[CHECK] 检查配置文件中的数据库路径...")
    print("="*60)
    
    config_file = Path('backend/config.py')
    
    if not config_file.exists():
        print("[FAIL] 配置文件 backend/config.py 不存在")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否指向 data/sport_lottery.db
        if 'data/sport_lottery.db' in content:
            print("[PASS] 配置文件正确指向 data/sport_lottery.db")
            return True
        elif 'sport_lottery.db' in content:
            print("[WARN] 配置文件包含 sport_lottery.db，但未明确指向 data/ 目录")
            return False
        else:
            print("[FAIL] 配置文件中未找到数据库路径配置")
            return False
            
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False

def main():
    print("[TEST] CI/CD数据库路径验证测试")
    print("="*60)
    
    # 检查硬编码路径
    path_check = check_hardcoded_paths()
    
    # 检查配置文件
    config_check = check_config_files()
    
    print("\n" + "="*60)
    print("[RESULT] 验证结果汇总")
    print("="*60)
    print(f"硬编码路径检查: {'[PASS] 通过' if path_check else '[FAIL] 失败'}")
    print(f"配置文件检查: {'[PASS] 通过' if config_check else '[FAIL] 失败'}")
    
    if path_check and config_check:
        print("\n[SUCCESS] 所有检查通过！可以安全部署。")
        return 0
    else:
        print("\n[ERROR] 检查失败！请修复上述问题后再部署。")
        return 1

if __name__ == '__main__':
    exit(main())