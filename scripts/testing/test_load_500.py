#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

try:
    from backend.api.v1.lottery_final import load_500_com_data_direct
    print("导入成功")
    data = load_500_com_data_direct()
    print(f"返回数据长度: {len(data)}")
    if data:
        print("第一条数据:")
        print(data[0])
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()