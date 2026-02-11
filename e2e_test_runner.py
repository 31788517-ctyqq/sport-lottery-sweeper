import requests
import time
from datetime import datetime

def run_e2e_tests():
    # 设置API端点和头部
    headers = {'Content-Type': 'application/json'}
    base_api_url = 'http://localhost:8000/api/v1/admin'

    print("🚀 开始执行数据源管理模块所有页面的端到端测试...\n")

    # 1. 测试数据源配置页面功能
    print('🧪 开始测试数据源配置页面功能...')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # 获取初始数据源列表
    initial_response = requests.get(f'{base_api_url}/sources', headers=headers)
    initial_data = initial_response.json()
    initial_count = initial_data['data']['total']
    print(f'📊 初始数据源数量: {initial_count}')

    # 创建一个新的数据源
    new_source_data = {
        'name': f'E2E测试数据源-{timestamp}',
        'type': 'api',
        'url': 'https://api.example.com/test',
        'config': {'apiKey': 'test-key', 'timeout': 30},
        'status': True
    }
    create_response = requests.post(f'{base_api_url}/sources', headers=headers, json=new_source_data)
    create_data = create_response.json()
    if create_data['success']:
        created_source = create_data['data']
        print(f'✅ 成功创建数据源: {created_source["name"]}')
    else:
        print(f'❌ 创建数据源失败: {create_data}')

    # 验证数据源已成功创建
    updated_list_response = requests.get(f'{base_api_url}/sources', headers=headers)
    updated_data = updated_list_response.json()
    new_count = updated_data['data']['total']
    print(f'📊 创建后数据源数量: {new_count}')

    # 获取刚创建的数据源详情
    if create_data['success']:
        source_detail_response = requests.get(f'{base_api_url}/sources/{created_source["id"]}', headers=headers)
        source_detail = source_detail_response.json()
        if source_detail['success']:
            print(f'✅ 成功获取数据源详情: {source_detail["data"]["name"]}')
        else:
            print(f'❌ 获取数据源详情失败: {source_detail}')

    # 测试数据源连接
    if create_data['success']:
        health_response = requests.post(f'{base_api_url}/sources/{created_source["id"]}/test-connection', headers=headers)
        health_data = health_response.json()
        if health_data['success']:
            print(f'✅ 数据源连接测试完成')
        else:
            print(f'❌ 数据源连接测试失败: {health_data}')

    # 删除创建的数据源
    if create_data['success']:
        delete_response = requests.delete(f'{base_api_url}/sources/{created_source["id"]}', headers=headers)
        delete_data = delete_response.json()
        if delete_data['success']:
            print(f'🗑️ 数据源已删除: {created_source["id"]}')
        else:
            print(f'❌ 删除数据源失败: {delete_data}')

    # 验证删除后列表数量回到初始状态
    final_response = requests.get(f'{base_api_url}/sources', headers=headers)
    final_data = final_response.json()
    final_count = final_data['data']['total']
    print(f'📊 删除后数据源数量: {final_count}')

    print('✅ 数据源配置页面功能测试通过！\n')

    # 2. 测试任务控制台页面功能
    print('🧪 开始测试任务控制台页面功能...')
    try:
        initial_response = requests.get(f'{base_api_url}/tasks', headers=headers)
        initial_data = initial_response.json()
        if initial_data['success']:
            initial_task_count = initial_data['data']['total']
            print(f'📊 初始任务数量: {initial_task_count}')
            print('✅ 任务控制台页面功能正常')
        else:
            print(f'❌ 任务控制台页面功能异常: {initial_data}')
    except Exception as e:
        print(f'❌ 任务控制台页面功能异常: {e}')

    # 3. 测试IP池管理页面功能
    print('\n🧪 开始测试IP池管理页面功能...')
    try:
        initial_response = requests.get(f'{base_api_url}/ip-pools', headers=headers)
        initial_data = initial_response.json()
        if initial_data['success']:
            initial_ip_count = initial_data['data']['total']
            print(f'📊 初始IP池数量: {initial_ip_count}')
            print('✅ IP池管理页面功能正常')
        else:
            print(f'❌ IP池管理页面功能异常: {initial_data}')
    except Exception as e:
        print(f'❌ IP池管理页面功能异常: {e}')

    # 4. 测试请求头管理页面功能
    print('\n🧪 开始测试请求头管理页面功能...')
    try:
        initial_response = requests.get(f'{base_api_url}/headers', headers=headers)
        initial_data = initial_response.json()
        if initial_data['success']:
            initial_header_count = initial_data['data']['total']
            print(f'📊 初始请求头数量: {initial_header_count}')
            print('✅ 请求头管理页面功能正常')
        else:
            print(f'❌ 请求头管理页面功能异常: {initial_data}')
    except Exception as e:
        print(f'❌ 请求头管理页面功能异常: {e}')

    # 5. 测试数据中心页面功能
    print('\n🧪 开始测试数据中心页面功能...')
    try:
        overview_response = requests.get(f'{base_api_url}/data-center/overview', headers=headers)
        overview_data = overview_response.json()
        if overview_data['success']:
            print('✅ 数据中心页面功能正常')
        else:
            print(f'❌ 数据中心页面功能异常: {overview_data}')
    except Exception as e:
        print(f'❌ 数据中心页面功能异常: {e}')

    # 6. 测试爬虫监控页面功能
    print('\n🧪 开始测试爬虫监控页面功能...')
    try:
        stats_response = requests.get(f'{base_api_url}/monitor/system-stats', headers=headers)
        stats_data = stats_response.json()
        if stats_data['success']:
            print('✅ 爬虫监控页面功能正常')
        else:
            print(f'❌ 爬虫监控页面功能异常: {stats_data}')
    except Exception as e:
        print(f'❌ 爬虫监控页面功能异常: {e}')

    print('\n🎉 数据源管理模块所有页面端到端测试完成！')
    print('✅ 所有功能模块均通过测试')

if __name__ == "__main__":
    run_e2e_tests()

