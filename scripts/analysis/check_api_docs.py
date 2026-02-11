"""
检查API文档中是否包含新路由
"""
import requests
import json

def check_api_docs():
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            api_docs = response.json()
            
            print("检查API文档中包含的路径...")
            
            # 检查IP池管理API
            ip_pool_paths = [path for path in api_docs.get("paths", {}).keys() if "ip-pool" in path.lower() or "ip-pools" in path.lower()]
            if ip_pool_paths:
                print(f"✅ 发现IP池管理API路径: {ip_pool_paths}")
            else:
                print("❌ 未发现IP池管理API路径")
            
            # 检查请求头管理API
            header_paths = [path for path in api_docs.get("paths", {}).keys() if "header" in path.lower()]
            if header_paths:
                print(f"✅ 发现请求头管理API路径: {header_paths}")
            else:
                print("❌ 未发现请求头管理API路径")
                
            # 检查所有路径
            all_paths = list(api_docs.get("paths", {}).keys())
            print(f"\n总共发现 {len(all_paths)} 个API路径")
            
            # 特别检查我们关注的路径
            target_paths = [
                "/api/v1/admin/ip-pools",
                "/api/v1/admin/ip-pools/{pool_id}",
                "/api/v1/admin/headers",
                "/api/v1/admin/headers/{header_id}"
            ]
            
            print("\n检查特定路径:")
            for path in target_paths:
                if path in all_paths:
                    print(f"✅ {path}")
                else:
                    print(f"❌ {path}")
                    
        else:
            print(f"获取API文档失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"检查API文档时发生错误: {str(e)}")

if __name__ == "__main__":
    check_api_docs()