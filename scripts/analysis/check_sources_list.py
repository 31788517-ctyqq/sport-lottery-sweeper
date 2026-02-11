import requests
import json

def check_sources_list():
    print("获取数据源列表...")
    
    sources_url = "http://localhost:3000/api/admin/crawler/sources"
    try:
        sources_response = requests.get(sources_url)
        print(f"数据源列表请求状态: {sources_response.status_code}")
        print(f"原始响应内容: {sources_response.text[:1000]}...")  # 只打印前1000字符
        
        if sources_response.status_code == 200:
            response_json = sources_response.json()
            print(f"完整响应JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)[:2000]}...")
            
            # 检查响应结构
            if 'data' in response_json:
                data = response_json['data']
                print(f"数据类型: {type(data)}")
                
                if isinstance(data, list):
                    print(f"列表长度: {len(data)}")
                    for idx, item in enumerate(data):
                        print(f"  项目 {idx+1}: 类型={type(item)}, 内容={item}")
                else:
                    print(f"数据不是列表，而是: {data}")
            else:
                print(f"响应中没有'data'字段，而是: {response_json.keys()}")
        else:
            print(f"获取数据源列表失败: {sources_response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sources_list()