#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面修复BeidanFilterPanel.vue中的重复声明问题
"""

def comprehensive_fix():
    file_path = 'c:/Users/11581/Downloads/sport-lottery-sweeper/frontend/src/views/admin/BeidanFilterPanel.vue'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 记录已经声明过的变量
    declared_vars = set()
    new_lines = []
    
    for line in lines:
        # 检查是否是声明语句
        is_declaration = False
        var_name = None
        
        # 检查是否是响应式变量声明
        if 'const ' in line and (' = ref(' in line or ' = computed(' in line or ' = reactive(' in line):
            # 提取变量名
            start_idx = line.find('const ') + 6
            end_idx = line.find(' ', start_idx)
            if end_idx == -1:
                end_idx = line.find('=', start_idx)
            if end_idx != -1:
                var_name = line[start_idx:end_idx].strip()
                is_declaration = True
        
        # 如果是声明语句，并且已经声明过了，则跳过
        if is_declaration and var_name and var_name in declared_vars:
            # 替换为注释
            new_lines.append(f'    // {var_name} 已在前面声明，此处不再重复声明\n')
        elif is_declaration and var_name:
            # 第一次声明，记录下来
            declared_vars.add(var_name)
            new_lines.append(line)
        else:
            # 不是声明语句，直接添加
            new_lines.append(line)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"全面修复完成: {file_path}")
    print(f"去重变量列表: {list(declared_vars)}")


if __name__ == '__main__':
    comprehensive_fix()