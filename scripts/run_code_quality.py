#!/usr/bin/env python3
"""
代码质量检查脚本
运行所有代码质量检查工具，确保代码符合项目标准
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 检查工具配置
TOOLS = [
    {
        "name": "black",
        "command": ["python", "-m", "black", "--check", "."],
        "description": "代码格式化检查",
        "fix_command": ["python", "-m", "black", "."],
    },
    {
        "name": "isort",
        "command": ["python", "-m", "isort", "--check-only", "--diff", "."],
        "description": "导入排序检查",
        "fix_command": ["python", "-m", "isort", "."],
    },
    {
        "name": "flake8",
        "command": ["python", "-m", "flake8", "."],
        "description": "代码风格检查",
        "fix_command": None,  # flake8不提供自动修复
    },
    {
        "name": "mypy",
        "command": ["python", "-m", "mypy", "backend", "shared", "scripts"],
        "description": "类型检查",
        "fix_command": None,  # mypy不提供自动修复
    },
    {
        "name": "bandit",
        "command": ["python", "-m", "bandit", "-r", "backend", "-ll"],
        "description": "安全漏洞检查",
        "fix_command": None,  # bandit不提供自动修复
    },
]


def run_command(cmd: List[str], cwd: Path) -> Tuple[int, str, str]:
    """
    运行命令并返回结果
    
    Args:
        cmd: 命令列表
        cwd: 工作目录
    
    Returns:
        (返回码, 标准输出, 标准错误)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def print_result(tool_name: str, description: str, success: bool, output: str = ""):
    """
    打印检查结果
    
    Args:
        tool_name: 工具名称
        description: 工具描述
        success: 是否成功
        output: 输出内容
    """
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {tool_name}: {description}")
    if output and not success:
        print(f"  输出:\n{output.strip()[:500]}...")  # 限制输出长度


def run_tools(fix: bool = False) -> bool:
    """
    运行所有代码质量检查工具
    
    Args:
        fix: 是否尝试自动修复问题
    
    Returns:
        是否所有检查都通过
    """
    print("=" * 60)
    print("代码质量检查开始")
    print("=" * 60)
    
    all_passed = True
    os.chdir(PROJECT_ROOT)
    
    for tool in TOOLS:
        print(f"\n🔧 检查 {tool['name']} - {tool['description']}...")
        
        # 如果有修复命令并且启用了修复模式，运行修复命令
        if fix and tool["fix_command"]:
            print(f"  运行修复命令...")
            fix_code, fix_stdout, fix_stderr = run_command(tool["fix_command"], PROJECT_ROOT)
            if fix_code != 0:
                print(f"  ⚠️  修复命令执行失败: {fix_stderr}")
        
        # 运行检查命令
        code, stdout, stderr = run_command(tool["command"], PROJECT_ROOT)
        success = code == 0
        
        if not success:
            all_passed = False
        
        print_result(tool["name"], tool["description"], success, stdout + stderr)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有代码质量检查通过！")
    else:
        print("⚠️  代码质量检查发现问题，请查看上方输出")
        if fix:
            print("💡 已尝试自动修复，请重新运行检查")
    
    return all_passed


def setup_pre_commit() -> bool:
    """
    设置pre-commit钩子
    
    Returns:
        是否设置成功
    """
    print("\n" + "=" * 60)
    print("设置pre-commit钩子")
    print("=" * 60)
    
    pre_commit_config = PROJECT_ROOT / ".pre-commit-config.yaml"
    if not pre_commit_config.exists():
        print("❌ 找不到.pre-commit-config.yaml文件")
        return False
    
    # 检查是否已安装pre-commit
    check_code, _, _ = run_command(["pre-commit", "--version"], PROJECT_ROOT)
    if check_code != 0:
        print("❌ pre-commit未安装，请运行: pip install pre-commit")
        return False
    
    # 安装pre-commit钩子
    print("📦 安装pre-commit钩子...")
    install_code, install_out, install_err = run_command(
        ["pre-commit", "install"], PROJECT_ROOT
    )
    
    if install_code != 0:
        print(f"❌ pre-commit钩子安装失败: {install_err}")
        return False
    
    print("✅ pre-commit钩子安装成功")
    
    # 运行pre-commit对所有文件
    print("🔍 运行pre-commit对所有文件...")
    run_code, run_out, run_err = run_command(
        ["pre-commit", "run", "--all-files"], PROJECT_ROOT
    )
    
    if run_code != 0:
        print(f"⚠️  pre-commit检查发现问题:\n{run_out}{run_err}")
        return False
    
    print("✅ pre-commit检查通过")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="代码质量检查脚本")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="尝试自动修复发现的问题"
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="设置pre-commit钩子"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="显示详细输出"
    )
    
    args = parser.parse_args()
    
    # 如果需要设置pre-commit
    if args.setup:
        success = setup_pre_commit()
        return 0 if success else 1
    
    # 运行代码质量检查
    success = run_tools(fix=args.fix)
    
    if success:
        print("\n📋 建议后续操作:")
        print("1. 运行单元测试: pytest tests/unit/ -v")
        print("2. 运行集成测试: pytest tests/integration/ -v")
        print("3. 检查API文档: http://localhost:8000/docs")
        print("4. 使用pre-commit确保代码质量: git add . && git commit -m 'your message'")
        return 0
    else:
        print("\n🚨 代码质量问题需要修复:")
        print("1. 查看上方错误信息")
        print("2. 运行带--fix参数的脚本尝试自动修复")
        print("3. 手动修复剩余问题")
        print("4. 重新运行检查")
        return 1


if __name__ == "__main__":
    sys.exit(main())