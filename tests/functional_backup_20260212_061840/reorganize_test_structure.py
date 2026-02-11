"""
测试目录结构重组脚本
将项目根目录的测试文件重新组织到tests/目录下
"""
import os
import shutil
from pathlib import Path

def reorganize_test_structure():
    """
    重新组织测试目录结构
    """
    print("开始重新组织测试目录结构...")
    
    # 定义目标目录
    base_test_dir = Path("tests")
    unit_test_dir = base_test_dir / "unit"
    integration_test_dir = base_test_dir / "integration"
    e2e_test_dir = base_test_dir / "e2e"
    functional_test_dir = base_test_dir / "functional"
    
    # 创建目标目录
    for dir_path in [unit_test_dir, integration_test_dir, e2e_test_dir, functional_test_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"已确保目录存在: {dir_path}")
    
    # 定义根目录中的测试文件
    root_test_files = [f for f in Path(".").glob("test_*.py")]
    
    # 分类处理测试文件
    unit_tests = []
    integration_tests = []
    e2e_tests = []
    functional_tests = []
    
    for file_path in root_test_files:
        file_name = file_path.name.lower()
        
        # 单元测试文件
        if any(keyword in file_name for keyword in [
            '_model', 'model_', '_unit', 'unit_', 'simple_', 'basic_', 
            '_auth', 'auth_', 'password', '_service', 'service_'
        ]):
            unit_tests.append(file_path)
        # 集成测试文件
        elif any(keyword in file_name for keyword in [
            '_integration', 'integration_', '_api', 'api_', '_db', 'database_',
            '_endpoint', 'endpoint_', '_route', 'route_', '_merge', 'merged_'
        ]):
            integration_tests.append(file_path)
        # 端到端测试文件
        elif any(keyword in file_name for keyword in [
            '_e2e', 'e2e_', '_complete', 'complete_', '_workflow', 'workflow_',
            '_full', 'full_', '_end_to_end', 'end_to_end_'
        ]):
            e2e_tests.append(file_path)
        # 功能测试文件（其余的）
        else:
            functional_tests.append(file_path)
    
    # 移动文件到对应目录
    move_test_files(unit_tests, unit_test_dir)
    move_test_files(integration_tests, integration_test_dir)
    move_test_files(e2e_tests, e2e_test_dir)
    move_test_files(functional_tests, functional_test_dir)
    
    # 处理其他测试相关文件
    move_remaining_test_files()
    
    print("\n测试目录结构重组完成!")
    print("\n新的目录结构:")
    print_tree(base_test_dir, prefix="")
    
    print("\n建议接下来的操作:")
    print("1. 检查并更新所有导入路径以适应新的目录结构")
    print("2. 更新CI/CD配置中的测试路径")
    print("3. 验证所有测试仍能正常运行")


def move_test_files(files, target_dir):
    """移动测试文件到目标目录"""
    for file_path in files:
        target_path = target_dir / file_path.name
        if file_path != target_path:  # 避免移动到相同路径
            try:
                shutil.move(str(file_path), str(target_path))
                print(f"  移动 {file_path} -> {target_path}")
            except Exception as e:
                print(f"  移动 {file_path} 时出错: {e}")


def move_remaining_test_files():
    """移动其他测试相关文件"""
    # 查找根目录中的其他测试相关文件
    remaining_test_files = []
    
    # 搜索包含测试关键词的文件
    for file_path in Path(".").iterdir():
        if (file_path.is_file() and 
            file_path.suffix == '.py' and 
            'test' in file_path.name.lower()):
            # 已经处理过的文件跳过
            if not str(file_path).startswith('tests/'):
                remaining_test_files.append(file_path)
    
    functional_test_dir = Path("tests") / "functional"
    
    for file_path in remaining_test_files:
        target_path = functional_test_dir / file_path.name
        if file_path != target_path:
            try:
                shutil.move(str(file_path), str(target_path))
                print(f"  移动 {file_path} -> {target_path}")
            except Exception as e:
                print(f"  移动 {file_path} 时出错: {e}")


def print_tree(path, prefix="", max_depth=3, current_depth=0):
    """打印目录树结构"""
    if current_depth >= max_depth:
        return
    
    entries = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
    
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        
        if entry.is_dir():
            print(f"{prefix}{connector}{entry.name}/")
            extension = "    " if is_last else "│   "
            print_tree(entry, prefix=prefix+extension, max_depth=max_depth, current_depth=current_depth+1)
        else:
            print(f"{prefix}{connector}{entry.name}")


if __name__ == "__main__":
    reorganize_test_structure()