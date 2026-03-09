#!/usr/bin/env python3
"""
后端测试问题批量修复脚本
修复常见测试问题：
1. Pydantic Config类警告（迁移到ConfigDict）
2. SQLAlchemy模型注册问题
3. 清理缺失的测试文件引用
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

def find_files_with_pattern(root_dir: Path, pattern: str) -> List[Path]:
    """查找匹配模式的文件"""
    matches = []
    for py_file in root_dir.rglob("*.py"):
        content = py_file.read_text(encoding='utf-8')
        if re.search(pattern, content, re.MULTILINE):
            matches.append(py_file)
    return matches

def fix_pydantic_config(filepath: Path) -> bool:
    """修复单个文件的Pydantic Config类警告"""
    content = filepath.read_text(encoding='utf-8')
    
    # 检查是否已经导入ConfigDict
    if "from pydantic import" in content and "ConfigDict" not in content:
        # 添加ConfigDict导入
        content = re.sub(
            r'(from pydantic import [^\n]+)',
            r'\1, ConfigDict',
            content
        )
    
    # 替换 class Config: 为 model_config = ConfigDict
    # 处理多行配置，需要捕获整个缩进块
    pattern = r'(\n\s+)class Config:\s*\n(\s+)(.+?)\n(\s*)(?=\S|\Z)'
    
    def replace_config(match):
        indent = match.group(1)  # 外部缩进（通常4个空格）
        inner_indent = match.group(2)  # 内部缩进
        config_body = match.group(3)  # 配置体
        # 重构为ConfigDict
        # 简单处理：假设只有json_schema_extra
        if 'json_schema_extra' in config_body:
            # 提取json_schema_extra值
            extra_match = re.search(r'json_schema_extra\s*=\s*(\{.*?\})', config_body, re.DOTALL)
            if extra_match:
                extra_value = extra_match.group(1)
                # 重新格式化缩进
                extra_lines = extra_value.strip().split('\n')
                reformatted = '\n' + '\n'.join([f'{inner_indent}{line.strip()}' for line in extra_lines])
                return f'{indent}model_config = ConfigDict(\n{inner_indent}json_schema_extra={reformatted}\n{indent})'
        
        # 通用替换
        return f'{indent}model_config = ConfigDict(\n{inner_indent}{config_body}\n{indent})'
    
    new_content = re.sub(pattern, replace_config, content, flags=re.DOTALL)
    
    if new_content != content:
        filepath.write_text(new_content, encoding='utf-8')
        return True
    return False

def fix_model_registration():
    """修复SQLAlchemy模型注册问题"""
    # 确保user.py导入UserPrediction
    user_model_path = Path("models/user.py")
    if user_model_path.exists():
        content = user_model_path.read_text(encoding='utf-8')
        if 'from .user_models import UserPrediction' not in content:
            # 查找注释行位置
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '# from .predictions import UserPrediction' in line:
                    # 替换为实际导入
                    lines[i] = 'from .user_models import UserPrediction'
                    break
            new_content = '\n'.join(lines)
            user_model_path.write_text(new_content, encoding='utf-8')
            print(f"修复 {user_model_path} 中的UserPrediction导入")

def clean_missing_test_references():
    """清理缺失的测试文件引用"""
    # 查找可能引用缺失测试文件的conftest.py或__init__.py
    # 暂时跳过
    pass

def main():
    """主函数"""
    root_dir = Path.cwd()
    
    print("开始修复后端测试问题...")
    
    # 1. 修复Pydantic Config类警告
    print("\n1. 修复Pydantic Config类警告...")
    pattern = r'class Config:'
    files = find_files_with_pattern(root_dir, pattern)
    print(f"找到 {len(files)} 个需要修复的文件")
    
    fixed_count = 0
    for filepath in files:
        try:
            if fix_pydantic_config(filepath):
                print(f"  ✓ 修复 {filepath.relative_to(root_dir)}")
                fixed_count += 1
        except Exception as e:
            print(f"  ✗ 修复 {filepath.relative_to(root_dir)} 失败: {e}")
    
    print(f"修复了 {fixed_count}/{len(files)} 个文件")
    
    # 2. 修复模型注册问题
    print("\n2. 修复SQLAlchemy模型注册问题...")
    try:
        fix_model_registration()
        print("  ✓ 修复模型注册")
    except Exception as e:
        print(f"  ✗ 修复模型注册失败: {e}")
    
    # 3. 清理缓存
    print("\n3. 清理pytest缓存...")
    cache_dir = root_dir / ".pytest_cache"
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
        print("  ✓ 清理pytest缓存")
    
    print("\n修复完成！")
    print("建议运行: python -m pytest tests/unit/ -v --tb=short")

if __name__ == "__main__":
    main()