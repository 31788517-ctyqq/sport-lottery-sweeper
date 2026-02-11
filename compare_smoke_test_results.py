#!/usr/bin/env python3
"""
比较前后两次冒烟测试结果，分析修复情况
"""

import sys
from collections import defaultdict

def parse_results_file(file_path):
    """解析结果文件，返回路径到状态码的映射"""
    results = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 跳过注释行
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # 格式: /path\tstatus_code
        parts = line.split('\t')
        if len(parts) >= 2:
            path = parts[0]
            try:
                status = int(parts[1])
                results[path] = status
            except ValueError:
                # 如果状态码不是数字（如0表示超时）
                results[path] = parts[1]
    
    return results

def analyze_comparison(old_file, new_file):
    """分析比较结果"""
    old_results = parse_results_file(old_file)
    new_results = parse_results_file(new_file)
    
    print("=" * 80)
    print("冒烟测试结果对比分析")
    print("=" * 80)
    
    print(f"\n旧测试文件: {old_file}")
    print(f"  路由总数: {len(old_results)}")
    print(f"新测试文件: {new_file}")
    print(f"  路由总数: {len(new_results)}")
    
    # 统计旧结果中的500错误
    old_500_paths = [path for path, status in old_results.items() if status == 500]
    new_500_paths = [path for path, status in new_results.items() if status == 500]
    
    print(f"\n500错误统计:")
    print(f"  旧测试中500错误数: {len(old_500_paths)}")
    print(f"  新测试中500错误数: {len(new_500_paths)}")
    
    # 修复的500错误
    fixed_500 = [path for path in old_500_paths if path in new_results and new_results[path] != 500]
    
    print(f"\n已修复的500错误 ({len(fixed_500)}个):")
    for path in sorted(fixed_500):
        old_status = old_results[path]
        new_status = new_results[path]
        print(f"  {path}: {old_status} -> {new_status}")
    
    # 仍然存在的500错误
    still_500 = [path for path in old_500_paths if path in new_results and new_results[path] == 500]
    
    print(f"\n仍然存在的500错误 ({len(still_500)}个):")
    for path in sorted(still_500):
        print(f"  {path}")
    
    # 新出现的500错误（如果有）
    new_appearing_500 = [path for path in new_500_paths if path not in old_results or old_results.get(path) != 500]
    
    if new_appearing_500:
        print(f"\n新出现的500错误 ({len(new_appearing_500)}个):")
        for path in sorted(new_appearing_500):
            print(f"  {path}")
    
    # 状态码分布对比
    old_status_dist = defaultdict(int)
    for status in old_results.values():
        if isinstance(status, int):
            if 200 <= status < 300:
                old_status_dist['2xx'] += 1
            elif status == 401 or status == 403:
                old_status_dist['auth_fail'] += 1
            elif status == 404:
                old_status_dist['404'] += 1
            elif status == 422:
                old_status_dist['422'] += 1
            elif status == 500:
                old_status_dist['500'] += 1
            else:
                old_status_dist['other'] += 1
        else:
            old_status_dist['error'] += 1
    
    new_status_dist = defaultdict(int)
    for status in new_results.values():
        if isinstance(status, int):
            if 200 <= status < 300:
                new_status_dist['2xx'] += 1
            elif status == 401 or status == 403:
                new_status_dist['auth_fail'] += 1
            elif status == 404:
                new_status_dist['404'] += 1
            elif status == 422:
                new_status_dist['422'] += 1
            elif status == 500:
                new_status_dist['500'] += 1
            else:
                new_status_dist['other'] += 1
        else:
            new_status_dist['error'] += 1
    
    print(f"\n状态码分布对比:")
    print(f"  {'类别':<12} {'旧测试':<10} {'新测试':<10} {'变化':<10}")
    print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*10}")
    
    categories = ['2xx', 'auth_fail', '404', '422', '500', 'other', 'error']
    for cat in categories:
        old_count = old_status_dist[cat]
        new_count = new_status_dist[cat]
        change = new_count - old_count
        change_sign = '+' if change > 0 else '' if change == 0 else '-'
        print(f"  {cat:<12} {old_count:<10} {new_count:<10} {change_sign}{abs(change):<9}")
    
    # 成功率变化
    old_success_rate = old_status_dist['2xx'] / len(old_results) * 100
    new_success_rate = new_status_dist['2xx'] / len(new_results) * 100
    
    print(f"\n成功率变化:")
    print(f"  旧测试成功率: {old_success_rate:.1f}%")
    print(f"  新测试成功率: {new_success_rate:.1f}%")
    print(f"  提升: {new_success_rate - old_success_rate:.1f}个百分点")
    
    # 详细修复情况
    print(f"\n详细修复进展:")
    print(f"  500错误修复率: {len(fixed_500)}/{len(old_500_paths)} = {len(fixed_500)/len(old_500_paths)*100:.1f}%")
    
    # 列出修复的具体端点（最多10个）
    if fixed_500:
        print(f"\n部分已修复的500错误端点 (前10个):")
        for i, path in enumerate(sorted(fixed_500)[:10]):
            old_status = old_results[path]
            new_status = new_results[path]
            print(f"  {i+1:2}. {path}: {old_status} -> {new_status}")
    
    return {
        'old_total': len(old_results),
        'new_total': len(new_results),
        'old_500_count': len(old_500_paths),
        'new_500_count': len(new_500_paths),
        'fixed_500_count': len(fixed_500),
        'still_500_count': len(still_500),
        'success_rate_improvement': new_success_rate - old_success_rate
    }

def main():
    if len(sys.argv) != 3:
        print("用法: python compare_smoke_test_results.py <旧结果文件> <新结果文件>")
        print("示例: python compare_smoke_test_results.py auth_smoke_get_results.txt auth_smoke_get_results_latest.txt")
        sys.exit(1)
    
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    
    try:
        results = analyze_comparison(old_file, new_file)
        
        print(f"\n{'='*80}")
        print("总结:")
        print(f"  • 总路由数: {results['old_total']} -> {results['new_total']}")
        print(f"  • 500错误: {results['old_500_count']} -> {results['new_500_count']} (减少{results['old_500_count'] - results['new_500_count']}个)")
        print(f"  • 修复的500错误: {results['fixed_500_count']}个")
        print(f"  • 成功率提升: {results['success_rate_improvement']:.1f}个百分点")
        
        if results['new_500_count'] > 0:
            print(f"\n⚠️  仍有{results['new_500_count']}个端点返回500错误，需要进一步调试")
        else:
            print(f"\n✅ 所有500错误已修复!")
        
    except FileNotFoundError as e:
        print(f"错误: 文件未找到 - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()