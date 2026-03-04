#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
移除BeidanFilterPanel.vue中pagedResults的ref声明，只保留computed定义
"""

def remove_pagedresults_ref():
    file_path = 'c:/Users/11581/Downloads/sport-lottery-sweeper/frontend/src/views/admin/BeidanFilterPanel.vue'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 创建新内容，跳过pagedResults的ref声明
    new_lines = []
    for line in lines:
        # 跳过const pagedResults = ref([]); 这一行
        if 'const pagedResults = ref([]);' in line:
            continue
        new_lines.append(line)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"已移除pagedResults的ref声明: {file_path}")


if __name__ == '__main__':
    remove_pagedresults_ref()