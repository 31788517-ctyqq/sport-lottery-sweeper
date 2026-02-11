#!/usr/bin/env python3
"""
测试后端API路由是否全部注册成功
"""
import sys
import importlib
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, '.')

# ROUTE_CONFIG from backend/api/v1/__init__.py
ROUTE_CONFIG = [
    {"module": "backend.api.v1.admin", "prefix": "admin", "tags": ["admin"]},
    {"module": "backend.api.v1.crawler", "prefix": "crawler", "tags": ["crawler"]},
    {"module": "backend.api.v1.lottery", "prefix": "lottery", "tags": ["lottery"]},
    {"module": "backend.api.v1.hedging", "prefix": "hedging", "tags": ["hedging"]},
    {"module": "backend.api.v1.simple_hedging", "prefix": "simple_hedging", "tags": ["simple_hedging"]},
    {"module": "backend.api.v1.intelligence", "prefix": "intelligence", "tags": ["intelligence"]},
    {"module": "backend.api.v1.predictions", "prefix": "predictions", "tags": ["predictions"]},
    {"module": "backend.api.v1.llm", "prefix": "llm", "tags": ["llm"]},
    {"module": "backend.api.v1.real_time_decision", "prefix": "real_time_decision", "tags": ["real_time_decision"]},
    {"module": "backend.api.v1.agents", "prefix": "agents", "tags": ["agents"]},
    {"module": "backend.api.v1.caipiao_data", "prefix": "caipiao-data", "tags": ["caipiao-data"]}
]

def test_route_imports():
    """测试路由配置导入"""
    print('Testing route config imports...')
    errors = []
    for route_config in ROUTE_CONFIG:
        module_path = route_config["module"]
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, 'router'):
                print(f'[OK] {module_path}: OK')
            else:
                print(f'[ERROR] {module_path}: No router attribute')
                errors.append(f'{module_path}: No router attribute')
        except Exception as e:
            print(f'[ERROR] {module_path}: {e}')
            errors.append(f'{module_path}: {e}')

    if errors:
        print(f'\nTotal errors: {len(errors)}')
        for err in errors:
            print(f'  - {err}')
        return False
    else:
        print('\nAll route imports successful!')
        return True

def test_api_router():
    """测试API路由器创建"""
    print('\nTesting API router creation...')
    try:
        from backend.api.v1 import api_router
        print(f'[OK] API router imported successfully')
        print(f'  Number of routes: {len(api_router.routes)}')
        return True
    except Exception as e:
        print(f'[ERROR] API router import failed: {e}')
        traceback.print_exc()
        return False

def test_enhanced_inference():
    """测试增强推理服务"""
    print('\nTesting enhanced inference service...')
    try:
        from backend.services.enhanced_inference_service import get_enhanced_inference_service
        service = get_enhanced_inference_service()
        print(f'[OK] Enhanced inference service loaded')
        return True
    except Exception as e:
        print(f'[ERROR] Enhanced inference service failed: {e}')
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('Backend API Route Testing')
    print('=' * 60)
    
    success = True
    success &= test_route_imports()
    success &= test_api_router()
    success &= test_enhanced_inference()
    
    print('\n' + '=' * 60)
    if success:
        print('[PASS] All tests passed!')
        sys.exit(0)
    else:
        print('[FAIL] Some tests failed!')
        sys.exit(1)