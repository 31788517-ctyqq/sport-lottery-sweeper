#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复BeidanFilterPanel.vue中的重复声明问题
"""

def fix_duplicate_declarations():
    file_path = 'c:/Users/11581/Downloads/sport-lottery-sweeper/frontend/src/views/admin/BeidanFilterPanel.vue'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 修复从'const analysisData = ref(null);'开始到'const strategyPreviewMap = ref({});'结束的部分
    new_lines = []
    skip_section = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 检查是否是重复声明的起始部分
        if 'const analysisData = ref(null);' in line and not skip_section:
            # 添加注释说明，不再重复声明
            new_lines.append('    // 控制统计信息显示\n')
            new_lines.append('    // analysisData已在前面声明，此处不再重复声明\n')
            
            # 跳过接下来的重复声明行
            skip_section = True
            i += 1
            
            # 跳过所有相关的重复声明
            while i < len(lines):
                current_line = lines[i]
                
                # 检查是否到达重复声明的结尾
                if 'const strategyPreviewMap = ref({});' in current_line:
                    # 移动到下一个非空白行
                    i += 1
                    break
                
                # 跳过当前行
                i += 1
            
            continue
        
        # 检查是否是第二个pagedResults声明（computed版本）
        elif 'const pagedResults = computed(() =>' in line and i > 656:  # 第二次出现
            # 只保留第一个声明（ref版本），跳过这个computed声明
            # 找到这个computed的结束大括号
            new_lines.append('    // pagedResults已在前面声明为ref，此处使用相同的响应式变量\n')
            i += 1
            # 跳过整个computed函数体
            brace_count = 1
            while i < len(lines) and brace_count > 0:
                current_line = lines[i]
                if '{' in current_line:
                    brace_count += current_line.count('{')
                if '}' in current_line:
                    brace_count -= current_line.count('}')
                i += 1
            continue
        
        # 添加正常的行
        new_lines.append(line)
        i += 1
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"修复完成: {file_path}")


if __name__ == '__main__':
    fix_duplicate_declarations()