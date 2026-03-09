#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.v1.lottery import load_500_com_data
    print('✓ load_500_com_data 导入成功')
    
    result = load_500_com_data()
    print(f'✓ 函数执行成功，返回 {len(result)} 条数据')
    if result:
        print(f'✓ 第一条: {result[0]}')
except Exception as e:
    print(f'✗ 错误: {e}')
    import traceback
    traceback.print_exc()
