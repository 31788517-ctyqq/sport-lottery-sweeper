#!/usr/bin/env python3
"""
更新测试文件中的URL路径
"""
import re

# 读取测试文件
with open('backend/tests/unit/api/admin/test_data_source.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有 /api/admin/v1/sources 为 /api/v1/admin/sources
# 使用正则表达式确保只替换完整的URL路径
old_pattern = r'/api/admin/v1/sources'
new_path = '/api/v1/admin/sources'

# 执行替换
updated_content = re.sub(old_pattern, new_path, content)

# 写入更新后的文件
with open('backend/tests/unit/api/admin/test_data_source.py', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print(f'替换完成: {old_pattern} -> {new_path}')
print(f'替换次数: {len(re.findall(old_pattern, content))}')