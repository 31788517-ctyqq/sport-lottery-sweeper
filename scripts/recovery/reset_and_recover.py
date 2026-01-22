#!/usr/bin/env python
"""
一键恢复脚本
功能：删除现有数据库并重新初始化结构、导入种子数据、执行健康检查
适用于数据库损坏或结构不一致时的快速恢复
"""
import os
import sys
import shutil
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'sport_lottery.db')
ALEMBIC_INI = os.path.join(PROJECT_ROOT, 'alembic.ini')

def print_step(msg):
    print(f"\n>>> {msg}")

def run_cmd(cmd, cwd=PROJECT_ROOT):
    """执行命令并返回成功状态"""
    print_step(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    if result.returncode != 0:
        print(f"❌ 命令执行失败: {' '.join(cmd)}")
        return False
    return True

def remove_database():
    """删除现有数据库文件"""
    if os.path.exists(DB_PATH):
        print_step(f"删除数据库文件: {DB_PATH}")
        try:
            os.remove(DB_PATH)
            print("✅ 数据库文件已删除")
            return True
        except Exception as e:
            print(f"❌ 删除数据库失败: {e}")
            return False
    else:
        print("ℹ️ 数据库文件不存在，跳过删除")
        return True

def recreate_structure():
    """重新创建数据库结构（通过空迁移 + stamp）"""
    print_step("重新创建 Alembic 空迁移并标记版本")
    # 生成新的空迁移
    if not run_cmd(['alembic', 'revision', '-m', 'initial_structure_recovery']):
        return False
    # 找到最新版本号文件
    versions_dir = os.path.join(PROJECT_ROOT, 'alembic', 'versions')
    py_files = [f for f in os.listdir(versions_dir) if f.endswith('.py')]
    if not py_files:
        print("❌ 未找到迁移文件")
        return False
    latest_file = sorted(py_files)[-1]
    version_id = latest_file.split('_')[0]
    # 清空 upgrade/downgrade 内容
    rev_path = os.path.join(versions_dir, latest_file)
    with open(rev_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(
        'def upgrade():\n    pass',
        'def upgrade():\n    # 空迁移，用于接管已有数据库结构\n    pass'
    )
    content = content.replace(
        'def downgrade():\n    pass',
        'def downgrade():\n    # 空迁移，无法自动降级\n    pass'
    )
    with open(rev_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已清空迁移脚本内容，版本号: {version_id}")
    # stamp 版本
    if not run_cmd(['alembic', 'stamp', version_id]):
        return False
    return True

def import_seed_data():
    """导入种子数据"""
    print_step("导入种子数据")
    if not run_cmd(['python', 'scripts/seed/seed_runner.py']):
        return False
    return True

def health_check():
    """执行健康检查"""
    print_step("执行数据库健康检查")
    if not run_cmd(['python', 'scripts/health_check/db_health_check.py']):
        return False
    return True

def main():
    print("========================================")
    print("🔧 一键数据库恢复脚本")
    print("========================================")
    confirm = input("此操作将删除现有数据库并重新初始化，确认继续? (y/N): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        sys.exit(0)

    steps = [
        ("删除数据库", remove_database),
        ("重建结构", recreate_structure),
        ("导入种子数据", import_seed_data),
        ("健康检查", health_check)
    ]
    for desc, func in steps:
        if not func():
            print(f"❌ 恢复过程在【{desc}】阶段失败，终止")
            sys.exit(1)

    print("\n========================================")
    print("🎉 数据库恢复完成，可正常运行 start_backend.bat 启动服务")
    print("========================================")

if __name__ == '__main__':
    main()
