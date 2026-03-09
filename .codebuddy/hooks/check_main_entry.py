#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main.py入口文件保护钩子
防止创建main.py变体文件
"""
import os
import sys
import re
from pathlib import Path

def check_main_entry_violations():
    """检查main.py变体文件"""
    violations = []
    
    # 定义main.py变体模式
    main_variant_patterns = [
        r"main_fixed\.py$",
        r"main_final\.py$", 
        r"main_simple\.py$",
        r"main_backup\.py$",
        r"main_test\.py$",
        r"main_new\.py$",
        r"main_v2\.py$",
        r"main_.*\.py$"  # 任何包含main_前缀的py文件
    ]
    
    # 搜索项目中的Python文件
    project_root = Path(__file__).parent.parent.parent
    
    for py_file in project_root.rglob("*.py"):
        # 跳过一些特殊目录
        if any(part in str(py_file) for part in [
            ".git", "__pycache__", ".pytest_cache", ".venv", "venv",
            "node_modules", "build", "dist", ".coverage"
        ]):
            continue
            
        file_path = str(py_file)
        file_name = py_file.name
        
        # 检查是否为main.py变体
        for pattern in main_variant_patterns:
            if re.search(pattern, file_name, re.IGNORECASE):
                # 允许backend/main.py作为唯一入口
                if file_path.endswith("backend/main.py"):
                    continue
                    
                violations.append({
                    "file": file_path,
                    "pattern": pattern,
                    "type": "MAIN_ENTRY_VARIANT"
                })
    
    return violations

def check_import_consistency():
    """检查导入路径一致性"""
    violations = []
    
    # 检查是否还有旧的导入路径
    deprecated_imports = [
        r"from\s+\.\.\database\s+import",
        r"from\s+\.\.\models\s+import", 
        r"from\s+\.\.database_utils\s+import"
    ]
    
    project_root = Path(__file__).parent.parent.parent
    
    for py_file in project_root.rglob("*.py"):
        # 跳过一些目录
        if any(part in str(py_file) for part in [
            ".git", "__pycache__", ".pytest_cache", ".venv", "venv",
            "node_modules", "build", "dist"
        ]):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            for line_num, line in enumerate(lines, 1):
                for deprecated_pattern in deprecated_imports:
                    if re.search(deprecated_pattern, line):
                        violations.append({
                            "file": str(py_file),
                            "line": line_num,
                            "content": line.strip(),
                            "pattern": deprecated_pattern,
                            "type": "DEPRECATED_IMPORT"
                        })
        except Exception:
            continue
    
    return violations

def main():
    """主函数"""
    all_violations = []
    
    # 检查main.py变体
    main_violations = check_main_entry_violations()
    all_violations.extend(main_violations)
    
    # 检查导入一致性
    import_violations = check_import_consistency()
    all_violations.extend(import_violations)
    
    if all_violations:
        print("❌ 代码审查门禁检查失败:")
        print()
        
        main_violations = [v for v in all_violations if v["type"] == "MAIN_ENTRY_VARIANT"]
        import_violations = [v for v in all_violations if v["type"] == "DEPRECATED_IMPORT"]
        
        if main_violations:
            print("[MAIN_ENTRY_VARIANT] 发现main.py变体文件:")
            for violation in main_violations:
                print(f"  - {violation['file']}")
            print()
            print("根据项目规则，backend/main.py是唯一入口文件！")
            print("请删除变体文件或使用feature分支开发新功能。")
            print()
        
        if import_violations:
            print("[DEPRECATED_IMPORT] 发现废弃的导入路径:")
            for violation in import_violations[:10]:  # 只显示前10个
                print(f"  - {violation['file']}:{violation['line']}")
                print(f"    {violation['content']}")
            if len(import_violations) > 10:
                print(f"  ... 还有 {len(import_violations) - 10} 个问题")
            print()
            print("请使用新的导入路径规范（...database_utils, ...models等）")
            print()
        
        sys.exit(1)
    else:
        print("✅ 代码审查门禁检查通过")
        sys.exit(0)

if __name__ == "__main__":
    main()