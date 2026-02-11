#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
体育彩票扫盘系统 - 统一问题修复工具
整合所有重复的修复脚本，提供统一的命令行接口

常见问题：
1. 导入路径问题（相对导入、双点导入）
2. 文件编码问题（非UTF-8编码）
3. 管理员登录问题（用户表/管理员表混淆）
4. 数据库字段问题（datetime格式、notification_preferences）
5. 目录结构问题（缺少__init__.py）

使用方式：
python issue_fixer.py --help
python issue_fixer.py import-paths     # 修复导入路径
python issue_fixer.py encoding         # 检测并修复文件编码
python issue_fixer.py admin-login      # 修复管理员登录
python issue_fixer.py db-fields        # 修复数据库字段
python issue_fixer.py check-dirs       # 检查目录结构
python issue_fixer.py all              # 执行所有修复
"""

# AI_WORKING: coder1 @2026-01-29T15:30:00 - 创建统一问题修复工具，整合所有重复的修复脚本

import os
import sys
import re
import json
import sqlite3
import datetime
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False
    print("⚠️ chardet模块未安装，编码检测功能受限")

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    print("⚠️ bcrypt模块未安装，密码哈希功能受限")

# ============================================================================
# 配置
# ============================================================================

import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# 导入配置
try:
    from backend.config import DATABASE_PATH, PROJECT_ROOT
    DB_PATH = DATABASE_PATH
except ImportError:
    # 回退方案
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    BACKEND_DIR = PROJECT_ROOT / "backend"
    DB_PATH = BACKEND_DIR / "sport_lottery.db"

# ============================================================================
# 工具函数
# ============================================================================

def print_header(title: str) -> None:
    """打印标题"""
    print("\n" + "="*60)
    print(f"🔧 {title}")
    print("="*60)

def print_success(msg: str) -> None:
    """打印成功消息"""
    print(f"✅ {msg}")

def print_warning(msg: str) -> None:
    """打印警告消息"""
    print(f"⚠️  {msg}")

def print_error(msg: str) -> None:
    """打印错误消息"""
    print(f"❌ {msg}")

def get_py_files(directory: Path) -> List[Path]:
    """获取目录下所有Python文件"""
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(Path(root) / file)
    return py_files

# ============================================================================
# 1. 导入路径修复
# ============================================================================

def fix_relative_imports_in_file(filepath: Path) -> bool:
    """修复单个文件中的相对导入（from ... 到 backend.）"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    modified = False
    
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        # 匹配 from ... 导入
        if stripped.startswith('from ...'):
            indent = line[:len(line) - len(stripped)]
            rest = stripped[7:]  # 'from ...' 长度为7
            new_line = indent + 'from backend.' + rest
            new_lines.append(new_line)
            print(f'修复 {filepath}:{i+1}: {stripped[:50]}...')
            modified = True
        # 匹配 from .. 导入（双点）
        elif stripped.startswith('from ..'):
            indent = line[:len(line) - len(stripped)]
            rest = stripped[6:]  # 'from ..' 长度为6
            # 需要根据文件位置确定正确的导入路径
            # 暂时记录警告
            print_warning(f'文件 {filepath} 第 {i+1} 行包含双点导入: {stripped[:50]}...')
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    if modified:
        new_content = '\n'.join(new_lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def fix_double_dot_imports_in_file(filepath: Path) -> bool:
    """修复backend..和backend...导入"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换 backend... 为 backend..
    new_content = re.sub(r'backend\.\.\.', 'backend..', content)
    # 替换 backend.. 为 backend.
    new_content = re.sub(r'backend\.\.', 'backend.', new_content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print_success(f'修复双点导入: {filepath}')
        return True
    return False

def fix_import_paths() -> bool:
    """修复所有导入路径问题"""
    print_header("修复导入路径问题")
    
    if not BACKEND_DIR.exists():
        print_error(f"Backend目录不存在: {BACKEND_DIR}")
        return False
    
    api_dir = BACKEND_DIR / "api" / "v1"
    if not api_dir.exists():
        print_error(f"API目录不存在: {api_dir}")
        return False
    
    total_fixed = 0
    py_files = get_py_files(api_dir)
    
    for py_file in py_files:
        if fix_relative_imports_in_file(py_file):
            total_fixed += 1
        if fix_double_dot_imports_in_file(py_file):
            total_fixed += 1
    
    print_success(f"导入路径修复完成，共处理 {total_fixed} 个文件")
    return True

# ============================================================================
# 2. 文件编码修复
# ============================================================================

def detect_and_fix_encoding(filepath: Path) -> Tuple[bool, str]:
    """检测并修复文件编码问题"""
    if not CHARDET_AVAILABLE:
        return False, "chardet模块未安装"
    
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read()
        
        detected = chardet.detect(raw_data)
        encoding = detected.get('encoding', 'utf-8')
        confidence = detected.get('confidence', 0)
        
        encodings_to_try = ['utf-8', 'gbk', 'latin-1', 'cp936']
        
        for enc in encodings_to_try:
            try:
                content = raw_data.decode(enc)
                if enc.lower() != 'utf-8':
                    # 转换为UTF-8
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    return True, f"从 {encoding} (置信度: {confidence:.2f}) 转换为 UTF-8"
                else:
                    return True, f"文件已经是 UTF-8 编码 (置信度: {confidence:.2f})"
            except UnicodeDecodeError:
                continue
        
        return False, f"无法解码文件，检测到的编码: {encoding} (置信度: {confidence:.2f})"
    except Exception as e:
        return False, f"处理文件时出错: {e}"

def fix_encoding() -> bool:
    """修复文件编码问题"""
    print_header("检测并修复文件编码")
    
    # 检查可能有问题的文件
    problematic_files = [
        BACKEND_DIR / "models" / "user.py",
        BACKEND_DIR / "schemas" / "response.py",
        BACKEND_DIR / "schemas" / "user.py",
        BACKEND_DIR / "services" / "service_registry.py",
    ]
    
    fixed_count = 0
    for filepath in problematic_files:
        if filepath.exists():
            success, msg = detect_and_fix_encoding(filepath)
            if success:
                print_success(f"{filepath.name}: {msg}")
                fixed_count += 1
            else:
                print_warning(f"{filepath.name}: {msg}")
        else:
            print_warning(f"文件不存在: {filepath}")
    
    print_success(f"编码修复完成，处理了 {fixed_count} 个文件")
    return True

# ============================================================================
# 3. 管理员登录修复
# ============================================================================

def create_bcrypt_hash(password: str) -> Optional[str]:
    """生成bcrypt哈希"""
    if not BCRYPT_AVAILABLE:
        print_error("bcrypt模块未安装，无法创建哈希")
        return None
    
    try:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except Exception as e:
        print_error(f"创建哈希失败: {e}")
        return None

def verify_bcrypt_hash(password: str, hashed: str) -> bool:
    """验证bcrypt哈希"""
    if not BCRYPT_AVAILABLE:
        return False
    
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False

def fix_admin_login() -> bool:
    """修复管理员登录问题"""
    print_header("修复管理员登录问题")
    
    if not DB_PATH.exists():
        print_error(f"数据库文件不存在: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查users表中的admin用户
        cursor.execute("SELECT id, username, password_hash, role, status FROM users WHERE username='admin'")
        admin_row = cursor.fetchone()
        
        admin_password = "admin123"
        
        if admin_row:
            print_success(f"找到admin用户 (ID: {admin_row['id']}, 角色: {admin_row['role']})")
            
            current_hash = admin_row['password_hash']
            needs_update = False
            
            # 验证当前哈希
            if BCRYPT_AVAILABLE:
                bcrypt_valid = verify_bcrypt_hash(admin_password, current_hash)
                if bcrypt_valid:
                    print_success("密码哈希格式正确 (bcrypt)")
                else:
                    print_warning("密码哈希格式不正确，需要更新")
                    needs_update = True
            else:
                print_warning("无法验证密码哈希 (bcrypt模块未安装)")
                needs_update = True
            
            # 更新密码哈希
            if needs_update:
                new_hash = create_bcrypt_hash(admin_password)
                if new_hash:
                    cursor.execute(
                        "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                        (new_hash, datetime.datetime.now().isoformat(), admin_row['id'])
                    )
                    conn.commit()
                    print_success(f"已更新admin用户密码哈希")
        else:
            print_warning("未找到admin用户，正在创建...")
            
            new_hash = create_bcrypt_hash(admin_password)
            if not new_hash:
                return False
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, first_name, last_name, nickname, 
                                role, status, is_verified, is_active, user_type, login_count,
                                created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'admin', 'admin@example.com', new_hash, '系统', '管理员', 'Admin',
                'admin', 'active', 1, 1, 'admin', 0,
                datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat()
            ))
            
            conn.commit()
            print_success("admin用户创建成功")
        
        # 最终验证
        cursor.execute("SELECT username, role, status FROM users WHERE username='admin'")
        final_row = cursor.fetchone()
        
        if final_row:
            print_success(f"验证通过 - 用户: {final_row['username']}, 角色: {final_row['role']}, 状态: {final_row['status']}")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"修复管理员登录时出错: {e}")
        return False

# ============================================================================
# 4. 数据库字段修复
# ============================================================================

def fix_database_fields() -> bool:
    """修复数据库字段问题（datetime格式、notification_preferences等）"""
    print_header("修复数据库字段问题")
    
    if not DB_PATH.exists():
        print_error(f"数据库文件不存在: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        now = datetime.datetime.now().isoformat()
        fixed_count = 0
        
        # 1. 修复admin用户的created_at和updated_at
        cursor.execute("SELECT username, created_at, updated_at FROM users WHERE username='admin'")
        admin = cursor.fetchone()
        
        if admin:
            username, created_at, updated_at = admin
            
            # 修复created_at
            if created_at == 'datetime("now")' or not created_at:
                cursor.execute("UPDATE users SET created_at = ? WHERE username = 'admin'", (now,))
                print_success(f"修复created_at: {created_at or '空'} -> {now}")
                fixed_count += 1
            else:
                try:
                    datetime.datetime.fromisoformat(created_at)
                    print_success(f"created_at格式正确: {created_at}")
                except:
                    cursor.execute("UPDATE users SET created_at = ? WHERE username = 'admin'", (now,))
                    print_success(f"修复created_at: {created_at} -> {now}")
                    fixed_count += 1
            
            # 修复updated_at
            if updated_at == 'datetime("now")' or not updated_at:
                cursor.execute("UPDATE users SET updated_at = ? WHERE username = 'admin'", (now,))
                print_success(f"修复updated_at: {updated_at or '空'} -> {now}")
                fixed_count += 1
            else:
                try:
                    datetime.datetime.fromisoformat(updated_at)
                    print_success(f"updated_at格式正确: {updated_at}")
                except:
                    cursor.execute("UPDATE users SET updated_at = ? WHERE username = 'admin'", (now,))
                    print_success(f"修复updated_at: {updated_at} -> {now}")
                    fixed_count += 1
            
            # 2. 修复notification_preferences
            cursor.execute("SELECT notification_preferences FROM users WHERE username='admin'")
            pref_value = cursor.fetchone()[0]
            
            new_pref = "{}"
            if pref_value:
                try:
                    parsed = json.loads(pref_value)
                    new_pref = json.dumps(parsed)
                    print_success(f"notification_preferences是有效JSON: {pref_value[:50]}...")
                except json.JSONDecodeError:
                    print_warning(f"notification_preferences不是有效JSON，设置为空字典")
                    new_pref = "{}"
                    fixed_count += 1
            else:
                print_warning(f"notification_preferences为空，设置为空字典")
                new_pref = "{}"
                fixed_count += 1
            
            cursor.execute("UPDATE users SET notification_preferences = ? WHERE username = 'admin'", (new_pref,))
        
        conn.commit()
        conn.close()
        
        print_success(f"数据库字段修复完成，修复了 {fixed_count} 个问题")
        return True
        
    except Exception as e:
        print_error(f"修复数据库字段时出错: {e}")
        return False

# ============================================================================
# 5. 目录结构检查
# ============================================================================

def check_directory_structure() -> bool:
    """检查关键目录结构"""
    print_header("检查目录结构")
    
    try:
        print(f"📁 Backend目录路径: {BACKEND_DIR}")
        print(f"📁 绝对路径: {BACKEND_DIR.absolute()}")
        print(f"📁 是否存在: {BACKEND_DIR.exists()}")
        
        if not BACKEND_DIR.exists():
            print_error(f"Backend目录不存在: {BACKEND_DIR}")
            return False
    except Exception as e:
        print_error(f"检查Backend目录时出错: {e}")
        return False
    
    key_dirs = [
        BACKEND_DIR / "models",
        BACKEND_DIR / "schemas",
        BACKEND_DIR / "api",
        BACKEND_DIR / "services",
        BACKEND_DIR / "tests" / "unit",
        BACKEND_DIR / "tests" / "unit" / "models",
        BACKEND_DIR / "tests" / "unit" / "services",
    ]
    
    all_good = True
    
    for dir_path in key_dirs:
        try:
            if dir_path.exists():
                # 显示相对路径以便阅读
                rel_path = dir_path.relative_to(PROJECT_ROOT) if dir_path.is_relative_to(PROJECT_ROOT) else dir_path
                print_success(f"{rel_path}/ 目录存在")
                
                # 检查是否有__init__.py
                init_file = dir_path / "__init__.py"
                if init_file.exists():
                    print_success(f"    {init_file.name} 存在")
                else:
                    print_warning(f"    {init_file.name} 缺失")
                    # 可以选择自动创建
                    try:
                        init_file.touch()
                        print_success(f"    已创建 {init_file.name}")
                    except Exception as e:
                        print_error(f"    创建失败: {e}")
                        all_good = False
            else:
                rel_path = dir_path.relative_to(PROJECT_ROOT) if dir_path.is_relative_to(PROJECT_ROOT) else dir_path
                print_warning(f"{rel_path}/ 目录不存在")
                all_good = False
        except Exception as e:
            print_error(f"检查目录 {dir_path} 时出错: {e}")
            all_good = False
    
    if all_good:
        print_success("目录结构检查通过")
    else:
        print_warning("目录结构存在问题，建议修复")
    
    return all_good

# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="体育彩票扫盘系统 - 统一问题修复工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "command",
        choices=[
            "import-paths", "encoding", "admin-login", 
            "db-fields", "check-dirs", "all", "help"
        ],
        help="要执行的修复命令"
    )
    
    args = parser.parse_args()
    
    if args.command == "help":
        parser.print_help()
        return
    
    print("🎯 体育彩票扫盘系统 - 统一问题修复工具")
    print(f"📁 项目根目录: {PROJECT_ROOT}")
    print(f"📁 Backend目录: {BACKEND_DIR}")
    
    success = False
    
    if args.command == "import-paths":
        success = fix_import_paths()
    elif args.command == "encoding":
        success = fix_encoding()
    elif args.command == "admin-login":
        success = fix_admin_login()
    elif args.command == "db-fields":
        success = fix_database_fields()
    elif args.command == "check-dirs":
        success = check_directory_structure()
    elif args.command == "all":
        # 按顺序执行所有修复
        results = []
        results.append(("导入路径修复", fix_import_paths()))
        results.append(("文件编码修复", fix_encoding()))
        results.append(("管理员登录修复", fix_admin_login()))
        results.append(("数据库字段修复", fix_database_fields()))
        results.append(("目录结构检查", check_directory_structure()))
        
        print_header("所有修复完成")
        successful = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✅" if result else "❌"
            print(f"{status} {name}: {'成功' if result else '失败'}")
        
        success = successful == total
        if success:
            print_success(f"所有 {total} 项修复均成功完成")
        else:
            print_warning(f"完成 {successful}/{total} 项修复")
    
    if success:
        print("\n🎉 修复任务完成！")
        print("💡 建议：重启后端服务以应用修复")
    else:
        print("\n⚠️  修复过程中出现问题")
        print("💡 建议：检查错误信息并手动修复")
    
    sys.exit(0 if success else 1)

# ============================================================================
# 入口点
# ============================================================================

if __name__ == "__main__":
    # AI_WORKING: coder1 @2026-01-29T15:30:00 - 开始执行统一修复工具
    main()
    # AI_DONE: coder1 @2026-01-29T15:30:00