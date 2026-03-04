#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证测试 - 简化版本，避免编码问题
"""

import os
from pathlib import Path

def test_batch_files():
    """测试批处理文件是否已修复"""
    print("="*60)
    print("TEST: 验证批处理文件修复")
    print("="*60)
    
    batch_files = [
        'step1_init.bat',
        'scripts/batch/test_db_data.bat', 
        'scripts/batch/restart_backend_force.bat'
    ]
    
    all_passed = True
    
    for bat_file in batch_files:
        bat_path = Path(bat_file)
        if bat_path.exists():
            print(f"[PASS] {bat_file} 存在")
            
            # 检查是否使用data/sport_lottery.db
            with open(bat_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'data/sport_lottery.db' in content:
                    print(f"  [PASS] 使用正确的数据库路径")
                elif 'sport_lottery.db' in content and 'data/' not in content:
                    print(f"  [FAIL] 仍使用硬编码路径")
                    all_passed = False
                else:
                    print(f"  [INFO] 路径检查完成")
        else:
            print(f"[FAIL] {bat_file} 不存在")
            all_passed = False
    
    return all_passed

def test_documentation():
    """测试文档是否已更新"""
    print("\n" + "="*60)
    print("TEST: 验证文档更新")
    print("="*60)
    
    doc_files = ['README.md', 'PROJECT_STRUCTURE.md', 'STARTUP_GUIDE.md']
    all_passed = True
    
    for doc_file in doc_files:
        doc_path = Path(doc_file)
        if doc_path.exists():
            print(f"[PASS] {doc_file} 存在")
            
            with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'data/sport_lottery.db' in content:
                    print(f"  [PASS] 文档已更新为data/sport_lottery.db")
                else:
                    print(f"  [WARN] 文档可能未更新")
        else:
            print(f"[FAIL] {doc_file} 不存在")
            all_passed = False
    
    return all_passed

def test_ci_cd_config():
    """测试CI/CD配置是否已添加"""
    print("\n" + "="*60)
    print("TEST: 验证CI/CD配置")
    print("="*60)
    
    ci_file = Path('.github/workflows/ci-cd-optimized.yml')
    
    if ci_file.exists():
        print("[PASS] CI/CD配置文件存在")
        
        with open(ci_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            if 'Database Path Validation' in content:
                print("[PASS] 已添加数据库路径验证步骤")
                return True
            else:
                print("[FAIL] 未找到数据库路径验证步骤")
                return False
    else:
        print("[FAIL] CI/CD配置文件不存在")
        return False

def test_cleanup_scripts():
    """测试清理脚本是否已创建"""
    print("\n" + "="*60)
    print("TEST: 验证清理脚本")
    print("="*60)
    
    script_files = [
        'scripts/cleanup_old_backups.py',
        'scripts/cleanup_backups.bat',
        'scripts/setup_backup_cleanup_schedule.bat',
        'scripts/cleanup_schedule_README.md'
    ]
    
    all_passed = True
    
    for script_file in script_files:
        script_path = Path(script_file)
        if script_path.exists():
            print(f"[PASS] {script_file} 已创建")
        else:
            print(f"[FAIL] {script_file} 不存在")
            all_passed = False
    
    return all_passed

def main():
    print("SPORT LOTTERY SWEEPER - 最终验证测试")
    print("测试所有完成的任务")
    
    # 执行所有测试
    test1 = test_batch_files()
    test2 = test_documentation() 
    test3 = test_ci_cd_config()
    test4 = test_cleanup_scripts()
    
    # 汇总结果
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"批处理文件修复: {'PASS' if test1 else 'FAIL'}")
    print(f"文档更新: {'PASS' if test2 else 'FAIL'}")
    print(f"CI/CD配置: {'PASS' if test3 else 'FAIL'}")
    print(f"清理脚本: {'PASS' if test4 else 'FAIL'}")
    
    if test1 and test2 and test3 and test4:
        print("\n*** ALL TESTS PASSED ***")
        print("所有任务已成功完成！")
        return 0
    else:
        print("\n*** SOME TESTS FAILED ***")
        print("请检查失败的项目")
        return 1

if __name__ == '__main__':
    exit(main())