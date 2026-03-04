#!/usr/bin/env python3
"""
数据库路径健康检查脚本
验证所有数据库访问路径是否一致，避免未来再次出现分歧。

功能：
1. 检查项目根目录、backend目录、data目录下的数据库文件是否为同一物理文件（硬链接）
2. 验证脚本中使用的路径是否与 backend.database.DATABASE_PATH 一致
3. 检查常见脚本中的硬编码路径
4. 生成健康报告

使用方法：
python check_database_paths.py
"""

import os
import sys
from pathlib import Path
import sqlite3

def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent

def check_hardlinks():
    """检查硬链接情况"""
    project_root = get_project_root()
    paths = [
        project_root / "sport_lottery.db",
        project_root / "backend" / "sport_lottery.db",
        project_root / "data" / "sport_lottery.db"
    ]
    
    results = []
    for path in paths:
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        inode = path.stat().st_ino if exists else None
        results.append({
            "path": str(path),
            "exists": exists,
            "size": size,
            "inode": inode
        })
    
    # 检查是否为同一文件（相同inode）
    inodes = [r["inode"] for r in results if r["exists"]]
    same_file = len(set(inodes)) == 1 if inodes else False
    
    return {
        "paths": results,
        "same_file": same_file,
        "message": "所有路径指向同一物理文件" if same_file else "警告：存在多个不同的数据库文件"
    }

def check_database_path_config():
    """检查 backend.database.DATABASE_PATH 配置"""
    try:
        # 添加backend目录到Python路径
        sys.path.append(str(get_project_root() / "backend"))
        from backend.database import DATABASE_PATH
        
        db_path = Path(str(DATABASE_PATH))
        exists = db_path.exists()
        size = db_path.stat().st_size if exists else 0
        
        return {
            "config_path": str(db_path),
            "exists": exists,
            "size": size,
            "relative_to_root": str(db_path.relative_to(get_project_root())) if exists else None
        }
    except Exception as e:
        return {
            "config_path": "无法获取",
            "error": str(e)
        }

def check_script_hardcoded_paths():
    """检查常见脚本中的硬编码路径"""
    project_root = get_project_root()
    scripts_to_check = [
        project_root / "update_status_column_clean.py",
        project_root / "update_data_source_structure.py",
        project_root / "show_data.py",
        project_root / "sync_roles_data.py"
    ]
    
    hardcoded_patterns = [
        "backend/sport_lottery.db",
        "data/sport_lottery.db",
        "./backend/sport_lottery.db",
        "./data/sport_lottery.db",
        "sport_lottery.db"
    ]
    
    results = []
    for script_path in scripts_to_check:
        if not script_path.exists():
            results.append({
                "script": str(script_path),
                "status": "文件不存在",
                "hardcoded": []
            })
            continue
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found = []
            for pattern in hardcoded_patterns:
                if pattern in content:
                    found.append(pattern)
            
            results.append({
                "script": str(script_path),
                "status": "已检查",
                "hardcoded": found,
                "uses_database_module": "from backend.database import DATABASE_PATH" in content or "backend.database.DATABASE_PATH" in content
            })
        except Exception as e:
            results.append({
                "script": str(script_path),
                "status": f"读取失败: {e}",
                "hardcoded": []
            })
    
    return results

def check_database_connection():
    """测试数据库连接"""
    project_root = get_project_root()
    db_path = project_root / "sport_lottery.db"
    
    if not db_path.exists():
        return {
            "success": False,
            "error": f"数据库文件不存在: {db_path}"
        }
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查一些关键表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 检查数据源表是否有数据
        has_data = False
        count = 0
        if 'data_sources' in tables:
            cursor.execute("SELECT COUNT(*) FROM data_sources")
            count = cursor.fetchone()[0]
            has_data = count > 0
        
        conn.close()
        
        return {
            "success": True,
            "tables": tables,
            "table_count": len(tables),
            "has_data": has_data,
            "data_source_count": count if has_data else 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    print("=" * 60)
    print("数据库路径健康检查")
    print("=" * 60)
    
    print("\n1. 检查硬链接情况...")
    hardlink_result = check_hardlinks()
    for path_info in hardlink_result["paths"]:
        status = "[OK] 存在" if path_info["exists"] else "[WARN] 不存在"
        size_mb = path_info["size"] / (1024 * 1024) if path_info["exists"] else 0
        print(f"   {status} {path_info['path']}")
        if path_info["exists"]:
            print(f"      大小: {size_mb:.2f} MB, inode: {path_info['inode']}")
    
    if hardlink_result["same_file"]:
        print("   [OK] 所有路径指向同一物理文件")
    else:
        print("   [WARN] 警告：存在多个不同的数据库文件")
    
    print("\n2. 检查数据库路径配置...")
    config_result = check_database_path_config()
    if "error" in config_result:
        print(f"   [ERROR] 无法获取配置: {config_result['error']}")
    else:
        status = "[OK] 存在" if config_result["exists"] else "[WARN] 不存在"
        print(f"   {status} DATABASE_PATH = {config_result['config_path']}")
        if config_result["exists"]:
            size_mb = config_result["size"] / (1024 * 1024)
            print(f"      大小: {size_mb:.2f} MB, 相对路径: {config_result['relative_to_root']}")
    
    print("\n3. 检查脚本中的硬编码路径...")
    script_results = check_script_hardcoded_paths()
    for script in script_results:
        print(f"   [FILE] {script['script']}")
        print(f"      状态: {script['status']}")
        if script.get('hardcoded'):
            print(f"      [WARN] 发现硬编码路径: {', '.join(script['hardcoded'])}")
        if script.get('uses_database_module'):
            print(f"      [OK] 使用 backend.database.DATABASE_PATH")
    
    print("\n4. 检查数据库连接...")
    db_conn_result = check_database_connection()
    if db_conn_result["success"]:
        print(f"   [OK] 数据库连接成功")
        print(f"      表数量: {db_conn_result['table_count']}")
        print(f"      关键表: {', '.join(db_conn_result['tables'][:10])}{'...' if len(db_conn_result['tables']) > 10 else ''}")
        if db_conn_result["has_data"]:
            print(f"      数据源数量: {db_conn_result['data_source_count']}")
    else:
        print(f"   [ERROR] 数据库连接失败: {db_conn_result['error']}")
    
    print("\n" + "=" * 60)
    print("健康检查总结")
    print("=" * 60)
    
    issues = []
    
    if not hardlink_result["same_file"]:
        issues.append("存在多个不同的数据库文件，可能导致数据不一致")
    
    if not config_result.get("exists", False):
        issues.append("DATABASE_PATH 指向的文件不存在")
    
    hardcoded_count = sum(len(s.get('hardcoded', [])) for s in script_results)
    if hardcoded_count > 0:
        issues.append(f"发现 {hardcoded_count} 处硬编码数据库路径，建议统一使用 DATABASE_PATH")
    
    if not db_conn_result["success"]:
        issues.append("数据库连接失败")
    
    if issues:
        print("[WARN] 发现以下问题：")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print("\n[INFO] 建议：")
        print("   1. 确保所有数据库访问通过 backend.database.DATABASE_PATH")
        print("   2. 使用硬链接统一数据库文件位置")
        print("   3. 更新脚本中的硬编码路径")
        return 1
    else:
        print("[OK] 所有检查通过，数据库路径配置一致")
        return 0

if __name__ == "__main__":
    sys.exit(main())