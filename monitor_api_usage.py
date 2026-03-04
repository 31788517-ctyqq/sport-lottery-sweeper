"""
API路径重定向使用情况监控脚本
用于监控新旧API路径的使用情况，帮助确定迁移进度
"""
import re
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import json

def analyze_log_file(log_file_path, days_back=7):
    """
    分析日志文件，统计API路径重定向使用情况
    
    Args:
        log_file_path: 日志文件路径
        days_back: 分析最近几天的日志
    """
    if not os.path.exists(log_file_path):
        print(f"日志文件不存在: {log_file_path}")
        return
    
    # 计算起始日期
    start_date = datetime.now() - timedelta(days=days_back)
    
    # 正则表达式匹配重定向日志
    redirect_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*API路径重定向: (.+) -> (.+)'
    
    redirect_stats = defaultdict(int)
    daily_stats = defaultdict(lambda: defaultdict(int))
    
    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.search(redirect_pattern, line)
            if match:
                timestamp_str, old_path, new_path = match.groups()
                
                # 解析时间戳
                try:
                    log_time = datetime.strptime(timestamp_str.split()[0], "%Y-%m-%d")
                    if log_time >= start_date:
                        redirect_stats[(old_path, new_path)] += 1
                        daily_stats[log_time.strftime("%Y-%m-%d")][(old_path, new_path)] += 1
                except ValueError:
                    continue
    
    return redirect_stats, daily_stats

def display_migration_status(redirect_stats, daily_stats):
    """
    显示迁移状态报告
    """
    print("=" * 80)
    print("API迁移状态报告")
    print("=" * 80)
    
    if not redirect_stats:
        print("近期未检测到API路径重定向使用")
        print("可能表示:")
        print("  1. 所有客户端已迁移到新API路径")
        print("  2. 服务未产生相关请求")
        print("  3. 日志级别过高，未记录重定向信息")
        return
    
    total_redirects = sum(redirect_stats.values())
    print(f"总计重定向次数: {total_redirects}")
    print()
    
    print("重定向详情:")
    print(f"{'旧路径':<50} {'新路径':<50} {'次数':<10} {'占比':<10}")
    print("-" * 120)
    
    for (old_path, new_path), count in sorted(redirect_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_redirects) * 100
        print(f"{old_path:<50} {new_path:<50} {count:<10} {percentage:.2f}%")
    
    print()
    print("每日重定向统计:")
    print(f"{'日期':<12} {'重定向次数':<15}")
    print("-" * 30)
    for date, stats in sorted(daily_stats.items()):
        daily_total = sum(stats.values())
        print(f"{date:<12} {daily_total:<15}")
    
    print()
    print("迁移建议:")
    if total_redirects > 0:
        max_redirects = max(redirect_stats.values())
        max_percentage = (max_redirects / total_redirects) * 100
        
        if max_percentage < 5:
            print("  ✅ 旧路径使用率 < 5%，可以考虑移除重定向中间件")
        elif max_percentage < 20:
            print("  ⚠️  旧路径使用率 < 20%，建议加强前端迁移工作")
        else:
            print("  ❌ 旧路径使用率较高，需要加速前端迁移工作")
    else:
        print("  ✅ 未检测到旧路径使用，可考虑移除重定向中间件")

def monitor_api_usage():
    """
    主监控函数
    """
    # 默认日志路径
    log_file_path = "logs/app.log"
    if not os.path.exists(log_file_path):
        # 尝试其他可能的日志路径
        possible_paths = [
            "backend/logs/app.log",
            "logs/app.log",
            "app.log",
            "backend/app.log"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                log_file_path = path
                break
        else:
            print("未找到日志文件，使用默认路径: logs/app.log")
    
    print(f"正在分析日志文件: {log_file_path}")
    
    try:
        redirect_stats, daily_stats = analyze_log_file(log_file_path)
        display_migration_status(redirect_stats, daily_stats)
    except Exception as e:
        print(f"分析日志时出错: {e}")

def check_frontend_references():
    """
    检查前端代码中是否还有旧API路径引用
    """
    print("\n" + "=" * 80)
    print("前端代码中旧API路径引用检查")
    print("=" * 80)
    
    import subprocess
    import glob
    
    # 搜索前端代码中的旧API路径
    frontend_dirs = [
        "frontend/src/**/*.vue",
        "frontend/src/**/*.js",
        "frontend/src/**/*.ts",
        "frontend/src/**/*.jsx",
        "frontend/src/**/*.tsx"
    ]
    
    old_api_patterns = [
        "/api/admin/crawler",
        "api/admin/crawler"
    ]
    
    found_references = []
    
    for pattern in frontend_dirs:
        files = glob.glob(pattern, recursive=True)
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for old_pattern in old_api_patterns:
                        if old_pattern in content:
                            # 查找包含旧路径的行
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if old_pattern in line:
                                    found_references.append((file_path, i, line.strip()))
            except Exception:
                # 忽略无法读取的文件
                continue
    
    if found_references:
        print(f"发现 {len(found_references)} 处旧API路径引用:")
        print(f"{'文件':<50} {'行号':<8} {'代码'}")
        print("-" * 80)
        for file_path, line_num, code in found_references[:20]:  # 只显示前20个
            print(f"{file_path:<50} {line_num:<8} {code}")
        
        if len(found_references) > 20:
            print(f"... 还有 {len(found_references) - 20} 处未显示")
        
        print("\n需要更新这些文件以使用新API路径!")
        return False
    else:
        print("✅ 未发现前端代码中有旧API路径引用")
        return True

def main():
    print("开始API迁移监控...")
    
    # 执行日志分析
    monitor_api_usage()
    
    # 检查前端引用
    frontend_clean = check_frontend_references()
    
    print("\n" + "=" * 80)
    print("总体评估")
    print("=" * 80)
    
    if frontend_clean:
        print("✅ 前端代码中未发现旧API路径引用")
    else:
        print("❌ 前端代码中发现旧API路径引用，需要更新")
    
    print("\n监控完成!")

if __name__ == "__main__":
    main()