#!/usr/bin/env python
"""
测试模块结构优化迁移脚本
将扁平结构的测试文件按 unit/models, unit/schemas, unit/crud, unit/api, integration, e2e 分类
"""
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent  # 项目根目录
src_dir = ROOT / "tests" / "backend" / "unit"
target_base = ROOT / "tests"

# 映射规则: 关键词 -> (目标子目录, 新文件名)
mapping_rules = {
    "model": ("unit/models", "test_models.py"),
    "schema": ("unit/schemas", "test_schemas.py"),
    "crud": ("unit/crud", "test_crud.py"),
    "database_operation": ("integration/database", "test_database_operations.py"),
    "api": ("unit/api", "test_api_functions.py"),  # 若是端点则用 integration/api/test_api_endpoints.py
    "advanced_scraper": ("e2e/scenarios", "test_crawler_workflow.py"),
    "improved_sporttery_crawler": ("e2e/scenarios", "test_crawler_workflow.py"),
    "enhanced_scraper": ("e2e/scenarios", "test_enhanced_scraper_workflow.py"),
    "system": ("integration/services", "test_system.py"),
    "login": ("integration/api", "test_auth_endpoints.py"),
    "auth": ("integration/api", "test_auth_endpoints.py"),
    "notification": ("integration/services", "test_notification_service.py"),
    "admin": ("e2e/scenarios", "test_admin_workflow.py"),
    "config": ("e2e/scenarios", "test_config_workflow.py"),
    "monitor": ("e2e/scenarios", "test_system_monitoring.py"),
}

def classify_file(filename):
    lower = filename.lower()
    for keyword, (subdir, new_name) in mapping_rules.items():
        if keyword in lower:
            return subdir, new_name
    # 默认放入 unit/api
    return "unit/api", f"test_{filename}"

# 遍历源目录
for file in src_dir.glob("test_*.py"):
    target_subdir, new_name = classify_file(file.stem)
    target_dir = target_base / target_subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / new_name
    
    # 如果目标已存在，加后缀避免覆盖
    counter = 1
    orig_target = target_path
    while target_path.exists():
        stem = orig_target.stem
        suffix = orig_target.suffix
        target_path = target_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    
    shutil.move(str(file), str(target_path))
    print(f"Moved {file.name} -> {target_subdir}/{target_path.name}")

print("✅ 测试文件迁移完成，请检查并手动调整 import 路径与数据库配置一致性。")
