#!/usr/bin/env python3
"""
简单语法检查脚本
检查Python脚本的基本语法
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_syntax(file_path: Path) -> bool:
    """检查Python文件语法"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(file_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ {file_path}: 语法正确")
            return True
        else:
            print(f"❌ {file_path}: 语法错误")
            print(f"   错误: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⚠️  {file_path}: 检查超时")
        return False
    except Exception as e:
        print(f"❌ {file_path}: 检查失败 - {e}")
        return False

def main():
    """主函数"""
    print("🔍 检查Python脚本语法...")
    print("="*50)
    
    # 检查scripts目录下的Python文件
    scripts_dir = Path(__file__).parent
    python_files = list(scripts_dir.glob("*.py"))
    
    all_pass = True
    for py_file in python_files:
        if py_file.name == "check-syntax.py":
            continue  # 跳过自己
        
        if not check_python_syntax(py_file):
            all_pass = False
    
    print("\n" + "="*50)
    if all_pass:
        print("✅ 所有Python脚本语法检查通过")
        return 0
    else:
        print("❌ 部分Python脚本语法检查失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())