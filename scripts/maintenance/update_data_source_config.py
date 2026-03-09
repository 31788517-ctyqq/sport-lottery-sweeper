import requests
import json

def update_data_source_config():
    # 获取DS041数据源的详细信息
    sources_url = "http://localhost:3000/api/admin/crawler/sources"
    
    try:
        sources_response = requests.get(sources_url)
        if sources_response.status_code == 200:
            sources_data = sources_response.json()['data']['items']
            
            # 找到DS041数据源
            target_source = None
            for source in sources_data:
                if source.get('source_id') == 'DS041':
                    target_source = source
                    break
            
            if target_source:
                print(f"找到数据源DS041，ID为: {target_source['id']}")
                
                # 更新数据源配置，添加超时和其他参数
                update_url = f"http://localhost:3000/api/admin/crawler/sources/{target_source['id']}"
                
                updated_config = {
                    "name": target_source['name'],
                    "url": target_source['url'],
                    "type": target_source['type'],
                    "status": target_source['status'],
                    "config": {
                        "category": "match_data",
                        "timeout": 30,
                        "max_retries": 3,
                        "headers": {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        }
                    },
                    "source_id": target_source['source_id']
                }
                
                print("正在更新数据源配置...")
                update_response = requests.put(update_url, json=updated_config)
                
                if update_response.status_code == 200:
                    result = update_response.json()
                    print(f"✅ 数据源配置更新成功: {result['message']}")
                    print(f"   新配置: {json.dumps(result['data']['config'], indent=2, ensure_ascii=False)}")
                else:
                    print(f"❌ 数据源配置更新失败: {update_response.status_code} - {update_response.text}")
            else:
                print("❌ 未找到数据源DS041")
        else:
            print(f"❌ 获取数据源列表失败: {sources_response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    update_data_source_config()