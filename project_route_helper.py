# 项目路由助手 - 适用于本项目所有模块
import sys
import os

def check_module_routes(module_path):
    """检查项目中任意模块的路由"""
    sys.path.insert(0, '.')
    
    try:
        # 动态导入模块
        module = __import__(module_path, fromlist=['router'])
        if hasattr(module, 'router'):
            print(f"✅ 模块 {module_path} 路由检查:")
            routes = []
            for route in module.router.routes:
                if hasattr(route, 'path'):
                    methods = getattr(route, 'methods', 'NO_METHOD')
                    path = getattr(route, 'path', 'NO_PATH')
                    routes.append((methods, path))
            
            # 显示路由
            for methods, path in routes:
                print(f"  {methods} {path}")
            
            # 检查常见问题
            check_common_issues(routes)
            return True
        else:
            print(f"❌ 模块 {module_path} 没有router属性")
            return False
    except Exception as e:
        print(f"❌ 导入 {module_path} 失败: {e}")
        return False

def check_common_issues(routes):
    """检查路由常见问题"""
    print("\n🔍 常见问题检查:")
    
    paths = [path for _, path in routes]
    
    # 检查1: 前缀重复
    if any('/admin/sp/sp/' in str(paths) for _ in paths):
        print("  ⚠️  发现可能的路由前缀重复")
    
    # 检查2: 路径冲突
    similar_paths = [p for p in paths if '/data-source' in p and '/data-sources' in p]
    if similar_paths:
        print(f"  ⚠️  发现相似路径可能冲突: {similar_paths}")
    
    # 检查3: 必需路径缺失
    required = ['/data-sources', '/data-source']
    missing = [r for r in required if not any(r in str(p) for p in paths)]
    if missing:
        print(f"  ❌ 缺失关键路由: {missing}")
    else:
        print("  ✅ 关键路由完整")

def main():
    """主函数 - 检查项目所有API模块"""
    print("🚀 项目路由全面检查\n")
    
    # 定义要检查的模块
    modules_to_check = [
        'backend.api.v1.auth',
        'backend.api.v1.admin', 
        'backend.api.v1.users',
        'backend.api.v1.sp_data_source',
        'backend.api.v1.sp_management',
        'backend.api.v1.intelligence',
        'backend.api.v1.departments',
    ]
    
    success_count = 0
    for module in modules_to_check:
        print("="*50)
        if check_module_routes(module):
            success_count += 1
    
    print("\n" + "="*50)
    print(f"📊 检查完成: {success_count}/{len(modules_to_check)} 个模块正常")
    
    if success_count == len(modules_to_check):
        print("🎉 所有模块路由配置正常！")
    else:
        print("⚠️  部分模块可能有问题，请检查上述错误信息")

if __name__ == "__main__":
    main()