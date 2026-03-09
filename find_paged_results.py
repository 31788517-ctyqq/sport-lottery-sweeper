#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查找BeidanFilterPanel.vue中可能的pagedResults computed定义
"""

def find_paged_results():
    file_path = 'c:/Users/11581/Downloads/sport-lottery-sweeper/frontend/src/views/admin/BeidanFilterPanel.vue'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("Searching for pagedResults...")
    for idx, line in enumerate(lines):
        if 'pagedResults' in line:
            print(f"Line {idx + 1}: {line.strip()}")
    
    print("\nSearching for computed definitions...")
    for idx, line in enumerate(lines):
        if 'const ' in line and 'computed' in line and '=' in line:
            if 'pagedResults' in line:
                print(f"FOUND pagedResults computed definition at line {idx + 1}: {line.strip()}")


if __name__ == '__main__':
    find_paged_results()