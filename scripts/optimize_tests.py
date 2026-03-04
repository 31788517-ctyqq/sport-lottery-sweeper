#!/usr/bin/env python3
"""
测试系统优化自动化脚本

这个脚本可以帮助你逐步执行测试优化计划中的各项任务。
使用方法:
    python scripts/optimize_tests.py --phase 1    # 执行第一阶段优化
    python scripts/optimize_tests.py --dry-run    # 预览将要执行的操作
    python scripts/optimize_tests.py --help       # 查看帮助
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

class TestOptimizer:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.actions_taken = []
        
    def log_action(self, action):
        """记录执行的操作"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {action}"
        print(log_entry)
        self.actions_taken.append(log_entry)
        
    def execute(self, command, description):
        """执行命令（支持dry-run模式）"""
        self.log_action(f"{description}: {command}")
        if not self.dry_run:
            try:
                result = os.system(command)
                if result != 0:
                    print(f"⚠️  命令执行返回非零状态码: {result}")
                return result == 0
            except Exception as e:
                print(f"❌ 执行命令时出错: {e}")
                return False
        return True
        
    def create_backup(self, source, backup_name=None):
        """创建文件或目录备份"""
        if backup_name is None:
            backup_name = f"{source.name}_backup_{self.backup_timestamp}"
            
        backup_path = source.parent / backup_name
        self.log_action(f"创建备份: {source} -> {backup_path}")
        
        if not self.dry_run:
            try:
                if source.is_file():
                    shutil.copy2(source, backup_path)
                else:
                    shutil.copytree(source, backup_path)
                return True
            except Exception as e:
                print(f"❌ 备份失败: {e}")
                return False
        return True
        
    def phase_1_immediate_fixes(self):
        """第一阶段：立即执行的关键修复"""
        print("\n🚀 开始执行第一阶段优化...")
        
        # 1. 创建E2E目录结构
        print("\n📁 创建E2E测试目录结构...")
        e2e_base = self.project_root / "tests" / "e2e" / "datasource"
        
        if not self.dry_run:
            e2e_base.mkdir(parents=True, exist_ok=True)
            
        # 创建基础文件
        init_file = e2e_base / "__init__.py"
        if not init_file.exists():
            self.execute(f"touch {init_file}", "创建__init__.py")
            
        # 2. 备份原E2E文件
        original_file = self.project_root / "tests" / "e2e" / "test_datasource_management_e2e.py"
        if original_file.exists():
            self.create_backup(original_file)
            
        # 3. 创建conftest.py模板
        conftest_content = '''"""
E2E测试共享配置和Fixture
"""
import pytest
import os
from typing import Dict, Any

@pytest.fixture(scope="session")
def base_url():
    """基础URL配置"""
    return os.getenv("TEST_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def admin_headers():
    """管理员认证头"""
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "demo-jwt-token")
    return {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }

@pytest.fixture
def base_api_url(base_url):
    """API基础URL"""
    return f"{base_url}/api/admin/v1"

@pytest.fixture
def sample_datasource_data():
    """示例数据源数据"""
    return {
        "name": "测试数据源",
        "category": "match_data",
        "source_type": "api",
        "api_url": "https://test-api.example.com/data",
        "method": "GET",
        "timeout": 30,
        "description": "测试用数据源"
    }
'''
        
        conftest_file = e2e_base / "conftest.py"
        if not conftest_file.exists():
            self.log_action(f"创建conftest.py文件")
            if not self.dry_run:
                with open(conftest_file, 'w', encoding='utf-8') as f:
                    f.write(conftest_content)
                    
        # 4. 创建CRUD测试文件模板
        crud_test_content = '''"""
数据源CRUD操作测试
从原test_datasource_management_e2e.py拆分而来
"""
import pytest
import os
from typing import Dict, Any

# 导入共享fixture
from conftest import base_url, admin_headers, base_api_url, sample_datasource_data

class TestDataSourceCRUD:
    """数据源CRUD测试类"""
    
    def test_create_datasource(self, base_api_url, admin_headers, sample_datasource_data):
        """测试创建数据源"""
        # TODO: 从原文件提取创建测试逻辑
        pass
        
    def test_get_datasource_list(self, base_api_url, admin_headers):
        """测试获取数据源列表"""
        # TODO: 从原文件提取列表测试逻辑
        pass
        
    def test_get_datasource_detail(self, base_api_url, admin_headers):
        """测试获取数据源详情"""
        # TODO: 从原文件提取详情测试逻辑
        pass
        
    def test_update_datasource(self, base_api_url, admin_headers, sample_datasource_data):
        """测试更新数据源"""
        # TODO: 从原文件提取更新测试逻辑
        pass
        
    def test_delete_datasource(self, base_api_url, admin_headers):
        """测试删除数据源"""
        # TODO: 从原文件提取删除测试逻辑
        pass
'''
        
        crud_file = e2e_base / "test_datasource_crud.py"
        if not crud_file.exists():
            self.log_action(f"创建test_datasource_crud.py文件")
            if not self.dry_run:
                with open(crud_file, 'w', encoding='utf-8') as f:
                    f.write(crud_test_content)
                    
        print("✅ 第一阶段优化完成！")
        
    def phase_1_functional_cleanup(self):
        """第一阶段：功能测试目录整理"""
        print("\n🧹 开始功能测试目录整理...")
        
        functional_dir = self.project_root / "tests" / "functional"
        if not functional_dir.exists():
            print("⚠️  功能测试目录不存在，跳过整理")
            return
            
        # 创建备份
        self.create_backup(functional_dir, f"functional_backup_{self.backup_timestamp}")
        
        # 定义文件分类
        categories = {
            'archived': [
                'simple_test.py', 'simple_test.db', 'quick_test.py',
                'final_login_test.py', 'simple_login_test.py'
            ],
            'debug_tools': [
                'debug_test_env.py', 'fix_test_imports.py', 
                'verify_async_tests.py', 'test_multiprocess_logging.py'
            ],
            'maintenance': [
                'run_tests.py', 'run_test.py', 'setup_admin_and_test.py',
                'reorganize_test_structure.py'
            ]
        }
        
        # 创建目录结构
        for category in categories.keys():
            category_dir = functional_dir / category
            if not self.dry_run:
                category_dir.mkdir(exist_ok=True)
            self.log_action(f"创建目录: {category_dir}")
            
        # 移动文件
        for category, files in categories.items():
            for filename in files:
                source_file = functional_dir / filename
                if source_file.exists():
                    target_dir = functional_dir / category
                    self.log_action(f"移动文件: {filename} -> {category}/")
                    if not self.dry_run:
                        shutil.move(str(source_file), str(target_dir / filename))
                        
        # 创建README
        readme_content = '''# 功能测试目录说明

## 目录结构
- archived/: 已废弃或过时的测试文件
- debug_tools/: 开发和调试用的工具脚本  
- maintenance/: 测试环境维护和执行的脚本
- validation/: 验证工具

## 使用说明
- 日常开发请使用 tests/unit/ 和 tests/integration/
- 调试工具请在必要时使用，不建议在CI中执行
- 维护脚本可用于本地环境设置和测试执行
'''
        
        readme_file = functional_dir / "README.md"
        self.log_action("创建README.md")
        if not self.dry_run:
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
                
        print("✅ 功能测试目录整理完成！")
        
    def generate_report(self):
        """生成优化报告"""
        report_file = self.project_root / "test_optimization_report.md"
        
        report_content = f'''# 测试优化执行报告

**执行时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**执行模式**: {'预览模式 (Dry Run)' if self.dry_run else '实际执行'}
**备份时间戳**: {self.backup_timestamp}

## 执行的操作

{chr(10).join(f"- {action}" for action in self.actions_taken)}

## 后续步骤

1. 验证修改后的测试是否能正常运行
2. 运行完整的测试套件确保没有破坏现有功能
3. 根据实际运行情况调整优化策略
4. 继续执行下一阶段的优化计划

## 注意事项

- 所有原始文件已备份，如有问题可随时恢复
- 建议在修改后运行 `python scripts/validate-test-environment.py` 验证环境
- 如需回滚，参考项目中的回滚脚本
'''
        
        self.log_action(f"生成报告: {report_file}")
        if not self.dry_run:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
        print(f"\n📊 优化报告已生成: {report_file}")
        
def main():
    parser = argparse.ArgumentParser(description="测试系统优化自动化脚本")
    parser.add_argument('--phase', type=int, choices=[1, 2, 3], 
                       help='执行指定阶段的优化')
    parser.add_argument('--all', action='store_true',
                       help='执行所有优化阶段')
    parser.add_argument('--dry-run', action='store_true',
                       help='预览模式，不实际执行操作')
    parser.add_argument('--report-only', action='store_true',
                       help='仅生成当前状态报告')
    
    args = parser.parse_args()
    
    optimizer = TestOptimizer(dry_run=args.dry_run)
    
    if args.report_only:
        optimizer.generate_report()
        return
        
    try:
        if args.all or args.phase == 1:
            print("🔥 执行第一阶段优化（高优先级）")
            optimizer.phase_1_immediate_fixes()
            optimizer.phase_1_functional_cleanup()
            
        if args.all or args.phase == 2:
            print("⏳ 第二阶段优化暂未实现，请参考 TEST_OPTIMIZATION_PLAN.md")
            
        if args.all or args.phase == 3:
            print("⏳ 第三阶段优化暂未实现，请参考 TEST_OPTIMIZATION_PLAN.md")
            
        optimizer.generate_report()
        
        if args.dry_run:
            print("\n💡 这是预览模式，没有实际执行任何操作")
            print("   使用 --all 参数来执行实际的优化操作")
        else:
            print("\n🎉 优化完成！请检查生成的报告和执行结果")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        optimizer.generate_report()
    except Exception as e:
        print(f"\n❌ 执行过程中发生错误: {e}")
        optimizer.generate_report()
        sys.exit(1)

if __name__ == "__main__":
    main()