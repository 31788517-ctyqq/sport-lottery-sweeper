"""
比较API响应和数据库内容
"""
import requests
from backend.database import get_db
from backend.models.data_sources import DataSource

def compare_api_and_db():
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("比较API响应和数据库内容")
    print("="*60)
    
    # 1. 从API获取数据
    print("\n1. 从API获取数据源列表:")
    try:
        response = requests.get(f"{base_url}/api/v1/admin/sources")
        api_data = response.json()
        
        print(f"   状态码: {response.status_code}")
        api_sources = api_data.get('data', {}).get('items', [])
        print(f"   API返回数据源数量: {len(api_sources)}")
        
        for i, source in enumerate(api_sources, 1):
            print(f"   {i}. ID: {source.get('id')}, 名称: {source.get('name')}, URL: {source.get('url')}")
            
    except Exception as e:
        print(f"   API请求错误: {e}")
        return
    
    print()
    
    # 2. 从数据库获取数据
    print("2. 从数据库获取数据源列表:")
    db = next(get_db())
    try:
        db_sources = db.query(DataSource).all()
        print(f"   数据库中数据源数量: {len(db_sources)}")
        
        for i, source in enumerate(db_sources, 1):
            print(f"   {i}. ID: {source.id}, 名称: {source.name}, URL: {source.url}")
            
    except Exception as e:
        print(f"   数据库查询错误: {e}")
        return
    finally:
        db.close()
    
    print()
    
    # 3. 比较差异
    print("3. 比较差异:")
    api_ids = {s['id'] for s in api_sources}
    db_ids = {s.id for s in db_sources}
    
    print(f"   API独有的ID: {api_ids - db_ids}")
    print(f"   数据库独有的ID: {db_ids - api_ids}")
    print(f"   共同的ID: {api_ids & db_ids}")
    
    print()
    
    # 4. 检查是否包含100qiu数据源
    qiu_in_api = any("100qiu" in s.get('name', '') for s in api_sources)
    qiu_in_db = any("100qiu" in s.name for s in db_sources)
    
    print(f"   100qiu数据源在API中: {'是' if qiu_in_api else '否'}")
    print(f"   100qiu数据源在数据库中: {'是' if qiu_in_db else '否'}")
    
    if qiu_in_db and not qiu_in_api:
        print("   ❌ 问题: 数据库中有100qiu数据源，但API没有返回")
    elif qiu_in_api and not qiu_in_db:
        print("   ❌ 问题: API返回100qiu数据源，但数据库中没有")
    elif qiu_in_api and qiu_in_db:
        print("   ✅ 正常: API和数据库中都有100qiu数据源")
    else:
        print("   ❌ 问题: API和数据库中都没有100qiu数据源")
    
    print("\n" + "="*60)
    print("比较完成")
    print("="*60)

if __name__ == "__main__":
    compare_api_and_db()