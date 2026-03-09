#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
详细诊断 lottery API 错误
"""
import sys
import os
import traceback

# 设置路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)

def test_imports():
    """测试所有导入"""
    print("=" * 60)
    print("1. 测试导入模块")
    print("=" * 60)
    
    try:
        from schemas.response import UnifiedResponse, PageResponse, ErrorResponse
        print("✓ schemas.response 导入成功")
    except Exception as e:
        print(f"✗ schemas.response 导入失败: {e}")
        traceback.print_exc()
        return False
    
    try:
        from core.cache_manager import get_cache_manager
        print("✓ core.cache_manager 导入成功")
    except Exception as e:
        print(f"✗ core.cache_manager 导入失败: {e}")
        traceback.print_exc()
        return False
    
    try:
        from scrapers.sporttery_scraper import sporttery_scraper
        print("✓ scrapers.sporttery_scraper 导入成功")
    except Exception as e:
        print(f"✗ scrapers.sporttery_scraper 导入失败: {e}")
        traceback.print_exc()
        return False
    
    try:
        from pathlib import Path
        print("✓ pathlib 导入成功")
    except Exception as e:
        print(f"✗ pathlib 导入失败: {e}")
        return False
    
    return True

def test_debug_file():
    """测试debug文件"""
    print("\n" + "=" * 60)
    print("2. 测试debug文件")
    print("=" * 60)
    
    try:
        from pathlib import Path
        import json
        
        project_root = Path(__file__).parent.parent
        debug_dir = project_root / "debug"
        
        print(f"项目根目录: {project_root}")
        print(f"Debug目录: {debug_dir}")
        print(f"Debug目录存在: {debug_dir.exists()}")
        
        if not debug_dir.exists():
            print("✗ debug目录不存在")
            return False
        
        files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
        print(f"找到 {len(files)} 个匹配文件: {files}")
        
        if not files:
            print("✗ 没有找到500彩票网数据文件")
            return False
        
        latest_file = sorted(files)[-1]
        file_path = debug_dir / latest_file
        print(f"最新文件: {file_path}")
        print(f"文件存在: {file_path.exists()}")
        
        if not file_path.exists():
            print("✗ 文件不存在")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"文件大小: {len(content)} 字节")
            
            # 尝试解析JSON
            data = json.loads(content)
            print(f"✓ JSON解析成功，包含 {len(data)} 条数据")
            
            if data:
                print(f"✓ 第一条数据:")
                for key, value in data[0].items():
                    print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()
        return False

def test_load_function():
    """测试加载函数"""
    print("\n" + "=" * 60)
    print("3. 测试 load_500_com_data 函数")
    print("=" * 60)
    
    try:
        from api.v1.lottery import load_500_com_data
        
        print("✓ 函数导入成功")
        
        result = load_500_com_data()
        print(f"✓ 函数执行完成，返回 {len(result)} 条数据")
        
        if result:
            print(f"✓ 第一条格式化数据:")
            for key, value in result[0].items():
                print(f"  {key}: {value} (类型: {type(value).__name__})")
        
        return True
        
    except Exception as e:
        print(f"✗ 函数执行失败: {e}")
        traceback.print_exc()
        return False

def test_get_lottery_matches():
    """测试get_lottery_matches函数"""
    print("\n" + "=" * 60)
    print("4. 测试 get_lottery_matches 函数")
    print("=" * 60)
    
    try:
        import asyncio
        from api.v1.lottery import get_lottery_matches
        
        print("✓ 函数导入成功")
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                get_lottery_matches(page=1, size=10, source="500")
            )
            print(f"✓ 异步函数执行完成")
            print(f"✓ 返回类型: {type(result).__name__}")
            
            if isinstance(result, dict):
                print(f"✓ 返回字典键: {list(result.keys())}")
                print(f"✓ success: {result.get('success')}")
                print(f"✓ 数据条数: {len(result.get('data', []))}")
                
                if result.get('data'):
                    print(f"✓ 第一条数据:")
                    for key, value in result['data'][0].items():
                        print(f"  {key}: {value}")
            else:
                print(f"✗ 返回类型不是dict: {type(result)}")
                print(f"  返回值: {result}")
        finally:
            loop.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 函数执行失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主流程"""
    print("\n" + "=" * 60)
    print("Lottery API 详细诊断")
    print("=" * 60)
    
    success1 = test_imports()
    success2 = test_debug_file()
    success3 = test_load_function()
    success4 = test_get_lottery_matches()
    
    print("\n" + "=" * 60)
    print("诊断结果")
    print("=" * 60)
    
    if all([success1, success2, success3, success4]):
        print("✓ 所有测试通过！API应该能正常工作")
        print("\n如果浏览器还显示500错误，请:")
        print("1. 确保后端已重启")
        print("2. 检查后端控制台是否有错误日志")
        print("3. 确保访问的是正确的URL")
    else:
        print("✗ 部分测试失败")
        print("\n请根据上面的错误信息进行修复")

if __name__ == '__main__':
    main()
