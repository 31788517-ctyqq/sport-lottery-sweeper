from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import logging
from backend.database import get_db
from backend.schemas.auth import LoginRequest, LoginResponse
from backend.api.deps import get_current_admin_user

logger = logging.getLogger("api.v1.admin")

# 创建主路由器
router = APIRouter()

print("Admin module: Starting to import user management modules...")

# 直接导入用户管理模块
try:
    from backend.api.v1.users import router as users_router
    print(f"Admin module: Successfully imported users router with {len(users_router.routes)} routes")
    router.include_router(users_router, prefix="/users", tags=["users"])
    print(f"Admin module: Added users router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add users router: {e}")
    import traceback
    traceback.print_exc()

try:
    from backend.api.v1.admin_user_management import router as admin_user_management_router
    print(f"Admin module: Successfully imported admin_user_management router with {len(admin_user_management_router.routes)} routes")
    router.include_router(admin_user_management_router, prefix="/admin-users", tags=["admin-users"])
    print(f"Admin module: Added admin_user_management router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add admin_user_management router: {e}")
    import traceback
    traceback.print_exc()

try:
    from backend.api.v1.frontend_user_management import router as frontend_user_management_router
    print(f"Admin module: Successfully imported frontend_user_management router with {len(frontend_user_management_router.routes)} routes")
    router.include_router(frontend_user_management_router, prefix="/frontend-users", tags=["frontend-users"])
    print(f"Admin module: Added frontend_user_management router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add frontend_user_management router: {e}")
    import traceback
    traceback.print_exc()

try:
    from backend.api.v1.simple_user_api import router as simple_user_api_router
    print(f"Admin module: Successfully imported simple_user_api router with {len(simple_user_api_router.routes)} routes")
    router.include_router(simple_user_api_router, prefix="/simple-users", tags=["simple-users"])
    print(f"Admin module: Added simple_user_api router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add simple_user_api router: {e}")
    import traceback
    traceback.print_exc()

# Handle crawler router import safely
try:
    from backend.api.v1.crawler import router as crawler_router
    print(f"Admin module: Successfully imported crawler router")
    router.include_router(crawler_router, prefix="/crawler", tags=["crawler"])
    print(f"Admin module: Added crawler router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add crawler router: {e}")

try:
    from backend.api.v1.sp_management import router as sp_management_router
    print(f"Admin module: Successfully imported sp_management router")
    router.include_router(sp_management_router, prefix="/sp", tags=["sp-management"])
    print(f"Admin module: Added sp_management router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add sp_management router: {e}")
    import traceback
    traceback.print_exc()

try:
    from backend.api.v1.draw_prediction import router as draw_prediction_router
    print(f"Admin module: Successfully imported draw_prediction router")
    router.include_router(draw_prediction_router, prefix="/draw-prediction", tags=["draw-prediction"])
    print(f"Admin module: Added draw_prediction router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add draw_prediction router: {e}")
    import traceback
    traceback.print_exc()

try:
    from backend.api.v1.hedging import router as hedging_router
    print(f"Admin module: Successfully imported hedging router")
    router.include_router(hedging_router, prefix="/hedging", tags=["hedging"])
    print(f"Admin module: Added hedging router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add hedging router: {e}")
    import traceback
    traceback.print_exc()

try:
    from backend.api.v1.intelligence import router as intelligence_router
    print(f"Admin module: Successfully imported intelligence router")
    router.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])
    print(f"Admin module: Added intelligence router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add intelligence router: {e}")
    import traceback
    traceback.print_exc()

try:
    from backend.api.v1.match_admin import router as match_admin_router
    print(f"Admin module: Successfully imported match_admin router")
    router.include_router(match_admin_router, prefix="/match", tags=["match-admin"])
    print(f"Admin module: Added match_admin router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add match_admin router: {e}")
    import traceback
    traceback.print_exc()

# Skip admin.matches since it may not exist
try:
    from backend.api.v1.admin.matches import router as admin_matches_router
    print(f"Admin module: Successfully imported admin_matches router")
    router.include_router(admin_matches_router, prefix="/matches", tags=["admin-matches"])
    print(f"Admin module: Added admin_matches router, now has {len(router.routes)} routes")
except ImportError:
    print("Admin module: admin.matches module not found, skipping...")

# Skip monitoring_dashboard since it has dependency issues
print("Admin module: Skipping monitoring_dashboard due to dependency issues")

# Note: We're not including monitoring_dashboard_router due to import issues

try:
    from backend.api.v1.admin.logs import router as logs_router
    print(f"Admin module: Successfully imported logs router")
    router.include_router(logs_router, prefix="/system", tags=["logs"])  # Register logs module to /system path so the API endpoint is /api/v1/admin/system/logs/
    print(f"Admin module: Added logs router, now has {len(router.routes)} routes")
except Exception as e:
    print(f"Admin module: Failed to import/add logs router: {e}")
    import traceback
    traceback.print_exc()

print(f"Admin module: Final route count: {len(router.routes)}")

# ===== Login interface =====
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
        logger.warning(f"管理员登录失败: username={login_data.username}")
        from backend.models.admin_user import AdminUser
        user = db.query(AdminUser).filter(AdminUser.username == login_data.username).first()
        if user and user.is_locked:
            logger.error(f"尝试登录已锁定的管理员账号: username={login_data.username}")
            raise HTTPException(status_code=423, detail="账户已被锁定，请联系系统管理员")
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

print("Admin module: Module loaded successfully")