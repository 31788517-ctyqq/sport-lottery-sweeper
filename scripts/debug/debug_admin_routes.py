"""
调试admin模块路由注册
"""
from fastapi import APIRouter
import logging
from backend.schemas.auth import LoginRequest, LoginResponse
from backend.database import get_db
from backend.api.deps import get_current_admin_user
from datetime import datetime

logger = logging.getLogger(__name__)

def safe_import(module_path, router_name="router"):
    try:
        module = __import__(module_path, fromlist=[router_name])
        return getattr(module, router_name)
    except ImportError as e:
        logger.warning(f"Failed to import {module_path}.{router_name}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error importing {module_path}.{router_name}: {e}")
        return None

def debug_admin_routes():
    print("开始调试admin路由注册...")
    
    # 创建路由器
    router = APIRouter()
    
    # 尝试导入各个路由模块
    try:
        print("正在导入users路由...")
        from backend.api.v1.users import router as users_router
        print(f"✓ 成功导入users路由，包含 {len(users_router.routes)} 个路由")
    except Exception as e:
        print(f"✗ 导入users路由失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        print("正在导入admin_user_management路由...")
        from backend.api.v1.admin_user_management import router as admin_user_management_router
        print(f"✓ 成功导入admin_user_management路由，包含 {len(admin_user_management_router.routes)} 个路由")
    except Exception as e:
        print(f"✗ 导入admin_user_management路由失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        print("正在导入frontend_user_management路由...")
        from backend.api.v1.frontend_user_management import router as frontend_user_management_router
        print(f"✓ 成功导入frontend_user_management路由，包含 {len(frontend_user_management_router.routes)} 个路由")
    except Exception as e:
        print(f"✗ 导入frontend_user_management路由失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        print("正在导入simple_user_api路由...")
        from backend.api.v1.simple_user_api import router as simple_user_api_router
        print(f"✓ 成功导入simple_user_api路由，包含 {len(simple_user_api_router.routes)} 个路由")
    except Exception as e:
        print(f"✗ 导入simple_user_api路由失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 检查初始路由数量
    print(f"初始路由数量: {len(router.routes)}")
    
    # 逐步注册路由并检查
    try:
        router.include_router(users_router, prefix="/users", tags=["users"])
        print(f"✓ users路由注册成功，当前数量: {len(router.routes)}")
    except Exception as e:
        print(f"✗ users路由注册失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        router.include_router(admin_user_management_router, prefix="/admin-users", tags=["admin-users"])
        print(f"✓ admin_user_management路由注册成功，当前数量: {len(router.routes)}")
    except Exception as e:
        print(f"✗ admin_user_management路由注册失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        router.include_router(frontend_user_management_router, prefix="/frontend-users", tags=["frontend-users"])
        print(f"✓ frontend_user_management路由注册成功，当前数量: {len(router.routes)}")
    except Exception as e:
        print(f"✗ frontend_user_management路由注册失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        router.include_router(simple_user_api_router, prefix="/simple-users", tags=["simple-users"])
        print(f"✓ simple_user_api路由注册成功，当前数量: {len(router.routes)}")
    except Exception as e:
        print(f"✗ simple_user_api路由注册失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 检查是否包含admin-users路由
    admin_users_count = 0
    for route in router.routes:
        if hasattr(route, 'path') and 'admin-users' in route.path:
            print(f"  发现admin-users路由: {route.path}")
            admin_users_count += 1
            
    print(f"总共找到 {admin_users_count} 个admin-users路由")
    
    # 添加登录路由
    @router.post(
        "/login",
        response_model=LoginResponse,
        summary="管理员登录",
        description="管理员用户通过用户名和密码进行登录认证",
    )
    async def login(login_data: LoginRequest, db=Depends(get_db)):
        """管理员登录接口"""
        from backend.auth.admin_auth import authenticate_admin_user
        admin_user = authenticate_admin_user(db, login_data.username, login_data.password)
        
        if not admin_user:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        admin_user.failed_login_attempts = 0
        admin_user.last_login_at = datetime.utcnow()
        db.commit()
        
        response = LoginResponse(
            access_token=admin_user.generate_token(),
            token_type="bearer",
            user_info={
                "id": admin_user.id,
                "username": admin_user.username,
                "email": admin_user.email,
                "role": admin_user.role,
                "permissions": admin_user.permissions,
                "last_login": admin_user.last_login_at.isoformat() if admin_user.last_login_at else None
            }
        )
        
        return response
    
    print(f"添加登录路由后，总路由数: {len(router.routes)}")
    
    # 检查是否包含登录路由
    login_count = 0
    for route in router.routes:
        if hasattr(route, 'path') and '/login' in route.path:
            print(f"  发现login路由: {route.path}")
            login_count += 1
            
    print(f"总共找到 {login_count} 个login路由")
    
    print("路由注册调试完成")

if __name__ == "__main__":
    debug_admin_routes()