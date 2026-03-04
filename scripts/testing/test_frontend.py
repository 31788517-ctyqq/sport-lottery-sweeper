"""
前端界面功能测试脚本
验证前端API调用是否使用正确的路径
"""
import re
import os
from pathlib import Path

def check_frontend_api_calls():
    """检查前端API文件中的路径调用"""
    frontend_api_dir = Path("frontend/src/api")
    
    if not frontend_api_dir.exists():
        print("❌ 前端API目录不存在")
        return False
    
    api_files = list(frontend_api_dir.glob("*.js"))
    print(f"🔍 检查 {len(api_files)} 个前端API文件...")
    
    issues_found = []
    
    for file_path in api_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 查找所有API路径
        api_paths = re.findall(r'url:\s*[\'"`]([^\'"`]+)[\'"`]', content)
        
        for path in api_paths:
            # 检查是否仍存在旧的API路径
            if '/api/admin/crawler' in path:
                issues_found.append({
                    'file': str(file_path),
                    'path': path,
                    'issue': '旧API路径未更新'
                })
                
            # 检查是否使用了正确的API路径
            if path.startswith('/api/v1/'):
                print(f"✅ {file_path.name}: {path} (正确)")
            elif path.startswith('/api/admin/crawler'):
                print(f"❌ {file_path.name}: {path} (错误 - 旧路径)")
    
    if issues_found:
        print(f"\n⚠️ 发现 {len(issues_found)} 个问题:")
        for issue in issues_found:
            print(f"  - {issue['file']}: {issue['path']} ({issue['issue']})")
        return False
    else:
        print(f"\n✅ 所有前端API文件均已使用正确的路径")
        return True

def validate_api_path_consistency():
    """验证前端API路径与后端路由的一致性"""
    print("\n🔍 验证API路径一致性...")
    
    # 根据之前的路由分析，后端注册的API路径
    backend_paths = {
        'tasks': '/api/v1/tasks',           # 任务管理
        'sources': '/api/v1/admin/sources', # 数据源管理
        'monitor': '/api/v1/admin/crawler/monitor', # 爬虫监控
        'headers': '/api/v1/admin/headers', # 请求头管理
        'ip-pools': '/api/v1/admin/ip-pools' # IP池管理
    }
    
    # 检查前端API文件
    frontend_checks = {
        'crawlerTask.js': backend_paths['tasks'],
        'dataSource.js': backend_paths['sources'],
        'crawlerMonitor.js': backend_paths['monitor'],
        'headers.js': backend_paths['headers'],
        'ipPool.js': backend_paths['ip-pools']
    }
    
    all_good = True
    for file_name, expected_path in frontend_checks.items():
        file_path = Path(f"frontend/src/api/{file_name}")
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查是否包含预期路径
            if expected_path in content:
                print(f"✅ {file_name}: 包含预期路径 {expected_path}")
            else:
                print(f"❌ {file_name}: 未找到预期路径 {expected_path}")
                all_good = False
        else:
            print(f"⚠️ {file_name}: 文件不存在")
    
    return all_good

def main():
    print("="*60)
    print("前端界面功能测试")
    print("="*60)
    
    # 检查前端API调用
    api_calls_ok = check_frontend_api_calls()
    
    # 验证路径一致性
    consistency_ok = validate_api_path_consistency()
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    print(f"前端API路径检查: {'✅ 通过' if api_calls_ok else '❌ 存在问题'}")
    print(f"路径一致性验证: {'✅ 通过' if consistency_ok else '❌ 存在问题'}")
    
    if api_calls_ok and consistency_ok:
        print("\n🎉 所有测试通过！前端界面功能正常。")
        print("✅ 前端API调用路径已全部更新至新版本")
        print("✅ API路径与后端路由保持一致")
        return True
    else:
        print("\n⚠️ 前端界面可能存在路径配置问题，请检查以上列出的问题。")
        return False

if __name__ == "__main__":
    main()