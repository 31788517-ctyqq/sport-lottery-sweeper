#!/usr/bin/env python3
"""
前端测试批量修复脚本 (Python版本)
修复以下问题：
1. 修复导入路径，使用别名 @ 代替相对路径
2. 确保测试文件有正确的 describe 块
3. 添加缺失的 Pinia store 模拟
"""

import os
import re
import sys
from pathlib import Path

def find_test_files(root_dir):
    """查找所有测试文件"""
    test_files = []
    patterns = ['*.test.js', '*.spec.js', '*.test.ts', '*.spec.ts']
    
    for pattern in patterns:
        for path in Path(root_dir).rglob(pattern):
            # 排除 node_modules
            if 'node_modules' in str(path):
                continue
            test_files.append(path)
    
    return test_files

def fix_import_paths(content, file_path):
    """修复导入路径，使用别名 @"""
    # 将相对路径转换为别名
    # 例如: ../views/... -> @/views/...
    #      ../../components/... -> @/components/...
    
    # 计算相对于 src 的路径
    src_path = None
    if '/src/' in str(file_path):
        # 找到 src 目录的位置
        parts = str(file_path).split('/src/')
        if len(parts) > 1:
            # 文件在 src 目录下
            src_path = '/src/' + parts[1]
    
    # 替换常见的相对路径模式
    patterns = [
        (r"from\s+'(\.\./)+views/(.+)'", r"from '@/views/\2'"),
        (r"from\s+'(\.\./)+components/(.+)'", r"from '@/components/\2'"),
        (r"from\s+'(\.\./)+stores/(.+)'", r"from '@/stores/\2'"),
        (r"from\s+'(\.\./)+api/(.+)'", r"from '@/api/\2'"),
        (r"from\s+'(\.\./)+utils/(.+)'", r"from '@/utils/\2'"),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def ensure_test_suite(content):
    """确保文件包含测试套件"""
    # 检查是否有 describe 块
    if 'describe(' not in content:
        # 这是一个没有测试套件的文件，可能是一个工具文件
        # 我们不需要修复它
        return content
    
    # 确保导入 vitest 的函数
    if "import { describe" not in content and "import describe" not in content:
        # 如果使用了 globals: true，可能不需要导入
        # 但为了安全，我们添加导入
        lines = content.split('\n')
        new_lines = []
        added_import = False
        
        for line in lines:
            new_lines.append(line)
            if line.strip().startswith('import') and not added_import:
                # 在第一个导入语句后添加 vitest 导入
                new_lines.append("import { describe, it, expect, vi } from 'vitest'")
                added_import = True
        
        if not added_import:
            # 如果没有导入语句，在文件开头添加
            new_lines.insert(0, "import { describe, it, expect, vi } from 'vitest'")
        
        content = '\n'.join(new_lines)
    
    return content

def add_pinia_mocks(content):
    """添加缺失的 Pinia store 模拟"""
    # 检查是否使用了 useAppStore 或 useUserStore
    if 'useAppStore' in content or 'useUserStore' in content:
        # 检查是否已经有模拟
        if "vi.mock('@/stores" not in content:
            # 在文件顶部添加模拟
            lines = content.split('\n')
            new_lines = []
            added_mock = False
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip().startswith('import') and not added_mock:
                    # 在导入语句后添加模拟
                    # 找到导入块的结束
                    j = i + 1
                    while j < len(lines) and (lines[j].strip().startswith('import') or lines[j].strip() == ''):
                        j += 1
                    # 在 j 处插入模拟
                    mock_code = """
// 模拟 Pinia stores
vi.mock('@/stores/app', () => ({
  useAppStore: () => ({
    showLoginModal: false,
    setShowLoginModal: vi.fn(),
    user: null,
    isLoggedIn: false,
    currentView: 'home',
    setCurrentView: vi.fn(),
    theme: 'light'
  })
}))

vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    isLoggedIn: true,
    user: { username: 'testuser', nickname: 'Test User' },
    logout: vi.fn(),
    login: vi.fn()
  })
}))"""
                    new_lines.append(mock_code)
                    added_mock = True
            
            content = '\n'.join(new_lines)
    
    return content

def fix_element_plus_warnings(content):
    """修复 Element Plus 重复注册警告"""
    # 检查是否在测试文件中注册了 Element Plus
    # 通常不应该在测试文件中注册，应该在 setup.js 中注册
    if 'app.use(ElementPlus)' in content and 'setup.js' not in str(content):
        print("  警告: 测试文件中发现 ElementPlus 注册，建议移至 setup.js")
    
    return content

def fix_file(file_path):
    """修复单个测试文件"""
    print(f"处理文件: {file_path}")
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # 应用修复
        content = fix_import_paths(content, file_path)
        content = ensure_test_suite(content)
        content = add_pinia_mocks(content)
        content = fix_element_plus_warnings(content)
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print("  ✓ 文件已修复")
            return True
        else:
            print("  - 无需修复")
            return False
            
    except Exception as e:
        print(f"  ✗ 处理文件时出错: {e}")
        return False

def clean_test_cache():
    """清理测试缓存"""
    cache_dirs = [
        '.pytest_cache',
        '.vitest',
        'node_modules/.vite',
        'test-results'
    ]
    
    cleaned = False
    for cache_dir in cache_dirs:
        cache_path = Path(cache_dir)
        if cache_path.exists():
            print(f"  删除缓存目录: {cache_dir}")
            import shutil
            shutil.rmtree(cache_path, ignore_errors=True)
            cleaned = True
    
    return cleaned

def main():
    """主函数"""
    print("开始修复前端测试问题...\n")
    
    # 获取前端目录
    frontend_dir = Path.cwd()
    if not frontend_dir.exists():
        print("错误: 无法找到前端目录")
        sys.exit(1)
    
    # 1. 清理缓存
    print("1. 清理测试缓存...")
    clean_test_cache()
    
    # 2. 查找并修复测试文件
    print("\n2. 查找测试文件...")
    test_files = find_test_files(frontend_dir)
    print(f"找到 {len(test_files)} 个测试文件\n")
    
    fixed_count = 0
    for file_path in test_files:
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\n修复完成。共检查 {len(test_files)} 个文件，修复了 {fixed_count} 个文件。")
    print("\n建议下一步:")
    print("1. 运行测试: npm run test:run")
    print("2. 如果仍有问题，检查控制台输出并针对性修复")
    print("3. 考虑更新测试配置确保正确模拟依赖项")

if __name__ == '__main__':
    main()