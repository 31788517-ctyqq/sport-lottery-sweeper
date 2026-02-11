#!/usr/bin/env python3
"""
分析422验证错误，找出需要修复的端点
"""

import re
from collections import defaultdict

def extract_422_endpoints(results_file):
    """从结果文件中提取所有422错误的端点"""
    endpoints = []
    
    with open(results_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = line.split('\t')
        if len(parts) >= 2:
            path = parts[0]
            status = parts[1]
            
            if status == '422':
                endpoints.append(path)
    
    return endpoints

def categorize_endpoints(endpoints):
    """将端点按模式分类"""
    categories = defaultdict(list)
    
    # 定义分类模式
    patterns = {
        'path_param_id': [
            r'\{header_id\}',
            r'\{source_id\}',
            r'\{task_id\}',
            r'\{caipiao_data_id\}',
            r'\{job_id\}',
            r'\{execution_id\}',
            r'\{admin_id\}',
            r'\{id\}',
            r'\{user_id\}',
            r'\{record_id\}',
            r'\{agent_id\}',
            r'\{match_id\}',
            r'\{schedule_id\}',
        ],
        'specific_endpoints': [
            r'/api/v1/admin/matches/league/config',
            r'/api/v1/admin/tree',
            r'/api/v1/hedging/parlay-opportunities',
            r'/api/v1/odds/odds/history',
            r'/api/v1/simple-hedging/parlay-opportunities',
            r'/api/v1/logs/system/logs/db/search',
            r'/api/v1/matches/admin/matches/league/config',
        ]
    }
    
    for endpoint in endpoints:
        categorized = False
        
        # 检查路径参数模式
        for pattern in patterns['path_param_id']:
            if re.search(pattern, endpoint):
                # 提取基本路径
                base_path = endpoint.split('/{')[0] + '/{id}'
                categories['需要路径参数'].append({
                    'endpoint': endpoint,
                    'base_path': base_path,
                    'param_type': pattern.strip('{}')
                })
                categorized = True
                break
        
        # 检查特定端点
        if not categorized:
            for pattern in patterns['specific_endpoints']:
                if re.search(pattern, endpoint):
                    categories['特定业务端点'].append(endpoint)
                    categorized = True
                    break
        
        # 未分类的端点
        if not categorized:
            categories['其他'].append(endpoint)
    
    return categories

def analyze_required_params(endpoint):
    """分析端点可能需要的参数（简化版）"""
    # 基于常见模式猜测
    if '{header_id}' in endpoint:
        return {'path_params': {'header_id': '需要有效的header ID'}}
    elif '{source_id}' in endpoint:
        return {'path_params': {'source_id': '需要有效的source ID'}}
    elif '{task_id}' in endpoint:
        return {'path_params': {'task_id': '需要有效的task ID'}}
    elif '{caipiao_data_id}' in endpoint:
        return {'path_params': {'caipiao_data_id': '需要有效的彩票数据ID'}}
    elif '{job_id}' in endpoint:
        return {'path_params': {'job_id': '需要有效的训练任务ID'}}
    elif '{execution_id}' in endpoint:
        return {'path_params': {'execution_id': '需要有效的执行ID'}}
    elif '{admin_id}' in endpoint:
        return {'path_params': {'admin_id': '需要有效的管理员ID'}}
    elif '{id}' in endpoint:
        return {'path_params': {'id': '需要有效的ID'}}
    elif '{user_id}' in endpoint:
        return {'path_params': {'user_id': '需要有效的用户ID'}}
    
    # 特定端点
    elif endpoint == '/api/v1/admin/matches/league/config':
        return {'query_params': {'可能需要league_id或其他过滤参数'}}
    elif endpoint == '/api/v1/admin/tree':
        return {'query_params': {'可能需要type或parent_id参数'}}
    elif endpoint == '/api/v1/hedging/parlay-opportunities':
        return {'query_params': {'可能需要match_id或odds_type参数'}}
    elif endpoint == '/api/v1/odds/odds/history':
        return {'query_params': {'可能需要match_id或company_id参数'}}
    
    return {'unknown': '需要查看API定义'}

def main():
    results_file = 'auth_smoke_get_results_latest.txt'
    
    print("=" * 80)
    print("422验证错误分析报告")
    print("=" * 80)
    
    # 提取422端点
    endpoints = extract_422_endpoints(results_file)
    print(f"\n共发现 {len(endpoints)} 个422错误端点:")
    for i, endpoint in enumerate(sorted(endpoints), 1):
        print(f"  {i:3}. {endpoint}")
    
    # 分类
    categories = categorize_endpoints(endpoints)
    
    print(f"\n分类统计:")
    for category, items in categories.items():
        print(f"  {category}: {len(items)}个")
    
    # 详细分析
    print(f"\n详细分析:")
    
    for category, items in categories.items():
        print(f"\n{category}:")
        
        if category == '需要路径参数':
            # 按基本路径分组
            grouped = defaultdict(list)
            for item in items:
                grouped[item['base_path']].append(item['param_type'])
            
            for base_path, param_types in grouped.items():
                param_str = ', '.join(sorted(set(param_types)))
                print(f"  {base_path}")
                print(f"    参数类型: {param_str}")
                print(f"    示例端点: {items[0]['endpoint'] if items else 'N/A'}")
        
        elif category == '特定业务端点':
            for endpoint in items:
                params = analyze_required_params(endpoint)
                print(f"  {endpoint}")
                for param_type, param_info in params.items():
                    print(f"    需要: {param_type} - {param_info}")
        
        else:
            for endpoint in items[:10]:  # 只显示前10个
                print(f"  {endpoint}")
            if len(items) > 10:
                print(f"  还有 {len(items) - 10} 个...")
    
    # 生成修复建议
    print(f"\n" + "=" * 80)
    print("修复建议:")
    print("=" * 80)
    
    print(f"\n1. 路径参数端点 ({len(categories.get('需要路径参数', []))}个):")
    print("   • 需要提供有效的ID值")
    print("   • 建议从现有数据中获取有效ID，或创建测试数据")
    print("   • 可以修改测试脚本，在调用前先获取有效ID列表")
    
    print(f"\n2. 特定业务端点 ({len(categories.get('特定业务端点', []))}个):")
    print("   • 需要提供特定查询参数")
    print("   • 建议查看API文档或源码，了解必需参数")
    print("   • 可以提供合理的默认值或测试值")
    
    print(f"\n3. 其他端点 ({len(categories.get('其他', []))}个):")
    print("   • 需要进一步分析具体原因")
    print("   • 建议查看错误响应详情")
    
    print(f"\n总体策略:")
    print("  1. 首先修复路径参数端点 - 提供有效的ID值")
    print("  2. 然后修复特定业务端点 - 提供必要查询参数")
    print("  3. 最后处理其他复杂情况")
    
    # 保存分析结果
    output_file = '422_errors_analysis.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("422验证错误分析报告\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"总端点数: {len(endpoints)}\n\n")
        
        f.write("按分类统计:\n")
        for category, items in categories.items():
            f.write(f"  {category}: {len(items)}个\n")
        
        f.write("\n详细端点列表:\n")
        for endpoint in sorted(endpoints):
            f.write(f"  {endpoint}\n")
    
    print(f"\n分析结果已保存到: {output_file}")

if __name__ == "__main__":
    main()