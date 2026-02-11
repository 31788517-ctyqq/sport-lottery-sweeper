"""
扫描器命令行接口
提供便捷的命令行操作
"""
import argparse
import sys
import json
import os
from pathlib import Path

from .api_scanner import APIScanner
from .config import get_config, create_default_config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="API扫描器 - 自动化检测401/422/404/403/409问题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 扫描API目录
  python -m scanner.cli scan --api-dir api/v1
  
  # 扫描并生成测试用例
  python -m scanner.cli scan --api-dir api/v1 --generate-tests
  
  # 创建默认配置文件
  python -m scanner.cli init-config
  
  # 检查配置
  python -m scanner.cli check-config
        """
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # scan命令
    scan_parser = subparsers.add_parser("scan", help="扫描API目录")
    scan_parser.add_argument("--backend-dir", default="backend", help="backend目录路径")
    scan_parser.add_argument("--api-dir", default="api/v1", help="API目录路径")
    scan_parser.add_argument("--output-dir", default="reports", help="报告输出目录")
    scan_parser.add_argument("--generate-tests", action="store_true", help="生成测试用例")
    scan_parser.add_argument("--test-output-dir", default="generated_tests", help="测试输出目录")
    scan_parser.add_argument("--config-file", help="配置文件路径")
    
    # init-config命令
    init_parser = subparsers.add_parser("init-config", help="创建默认配置文件")
    init_parser.add_argument("--output", default="scanner_config.yaml", help="输出文件路径")
    
    # check-config命令
    check_parser = subparsers.add_parser("check-config", help="检查配置")
    check_parser.add_argument("--config-file", default="scanner_config.yaml", help="配置文件路径")
    
    # test命令
    test_parser = subparsers.add_parser("test", help="运行扫描器测试")
    test_parser.add_argument("--backend-dir", default="backend", help="backend目录路径")
    
    # parse参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "scan":
            run_scan(args)
        elif args.command == "init-config":
            run_init_config(args)
        elif args.command == "check-config":
            run_check_config(args)
        elif args.command == "test":
            run_test(args)
        else:
            parser.print_help()
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


def run_scan(args):
    """运行扫描"""
    print("🔍 开始API扫描...")
    
    # 加载配置
    if args.config_file and os.path.exists(args.config_file):
        config = get_config(args.config_file)
    else:
        config = get_config()
    
    # 创建扫描器
    scanner = APIScanner(
        backend_dir=args.backend_dir,
        output_dir=args.output_dir
    )
    
    # 执行扫描
    report = scanner.scan_directory(args.api_dir)
    
    # 生成测试用例
    if args.generate_tests:
        print("🧪 生成测试用例...")
        test_files = scanner.generate_test_cases(args.test_output_dir)
        print(f"✅ 已生成 {len(test_files)} 个测试文件")
    
    # 输出摘要
    summary = scanner.get_summary()
    print("\n📋 扫描摘要:")
    print(f"  状态: {summary['status']}")
    print(f"  时间: {summary['timestamp']}")
    print(f"  总路由数: {summary['total_routes']}")
    print(f"  总问题数: {summary['total_issues']}")
    print(f"  认证问题: {summary['auth_issues']}")
    print(f"  验证问题: {summary['validation_issues']}")
    print(f"  高优先级问题: {summary['high_priority_issues']}")
    
    # 保存报告路径
    report_file = Path(args.output_dir) / "latest_scan_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 报告已保存到: {report_file}")
    
    # 如果有高优先级问题，返回非零退出码
    if summary['high_priority_issues'] > 0:
        print(f"⚠️  发现 {summary['high_priority_issues']} 个高优先级问题，需要修复")
        sys.exit(1)
    else:
        print("✅ 扫描完成，未发现高优先级问题")
        sys.exit(0)


def run_init_config(args):
    """初始化配置"""
    print("📝 创建默认配置文件...")
    
    try:
        config_file = create_default_config(args.output)
        print(f"✅ 配置文件已创建: {config_file}")
        
        # 显示配置内容
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        print("\n📋 配置内容预览:")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        sys.exit(1)


def run_check_config(args):
    """检查配置"""
    print("🔍 检查配置文件...")
    
    if not os.path.exists(args.config_file):
        print(f"❌ 配置文件不存在: {args.config_file}")
        sys.exit(1)
    
    try:
        config = get_config(args.config_file)
        config_dict = config.to_dict()
        
        print("✅ 配置文件格式正确")
        print("\n📊 配置摘要:")
        print(f"  backend目录: {config.backend_dir}")
        print(f"  API目录: {config.api_dirs}")
        print(f"  输出目录: {config.output_dir}")
        print(f"  报告格式: {config.report_formats}")
        print(f"  生成测试: {config.generate_tests}")
        
        # 显示详细配置
        print("\n📋 详细配置:")
        print(json.dumps(config_dict, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ 配置文件格式错误: {e}")
        sys.exit(1)


def run_test(args):
    """运行测试"""
    print("🧪 运行扫描器测试...")
    
    # 添加测试目录到路径
    tests_dir = Path(args.backend_dir).parent / "tests" / "scanner"
    
    if not tests_dir.exists():
        print(f"❌ 测试目录不存在: {tests_dir}")
        sys.exit(1)
    
    import pytest
    
    # 运行测试
    test_result = pytest.main([
        str(tests_dir),
        "-v",
        "--tb=short"
    ])
    
    if test_result == 0:
        print("✅ 所有测试通过")
        sys.exit(0)
    else:
        print("❌ 测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()