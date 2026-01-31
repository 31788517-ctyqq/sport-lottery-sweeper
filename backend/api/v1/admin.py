from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import logging
from backend.database import get_db
from backend.schemas.auth import LoginRequest, LoginResponse
from backend.api.deps import get_current_admin_user

logger = logging.getLogger("api.v1.admin")

# 创建主路由器
router = APIRouter()

# Import other modules with error handling
import logging
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

# Import routers safely
from .users import router as users_router
from .admin_user_management import router as admin_user_management_router
from .frontend_user_management import router as frontend_user_management_router
from .simple_user_api import router as simple_user_api_router
crawler_router = safe_import(".crawler", "router")
from .sp_management import router as sp_management_router
from .draw_prediction import router as draw_prediction_router
from .hedging import router as hedging_router
from .intelligence import router as intelligence_router
from .match_admin import router as match_admin_router
from .admin.matches import router as admin_matches_router
from .monitoring_dashboard import router as monitoring_dashboard_router
from .logs import router as logs_router  # 添加日志模块路由

# ===== Login interface (from file A) =====
@router.post(
    "/login",
    response_model=LoginResponse,
    summary="管理员登录",
    description="管理员用户通过用户名和密码进行登录认证",
)
async def login(  # 添加缺失的函数定义
    login_data: LoginRequest,
    db=Depends(get_db)
):
    """管理员登录接口
    
    Args:
        login_data: 登录凭证
        
    Returns:
        LoginResponse: 包含token等信息的响应
        
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    # 导入认证函数
    from backend.auth.admin_auth import authenticate_admin_user
    
    # 尝试认证
    admin_user = authenticate_admin_user(db, login_data.username, login_data.password)
    
    if not admin_user:
        logger.warning(f"管理员登录失败: username={login_data.username}")
        # 检查是否为账户锁定状态
        from backend.models.admin_user import AdminUser
        user = db.query(AdminUser).filter(AdminUser.username == login_data.username).first()
        if user and user.is_locked:
            logger.error(f"尝试登录已锁定的管理员账号: username={login_data.username}")
            raise HTTPException(status_code=423, detail="账户已被锁定，请联系系统管理员")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 重置失败登录计数
    admin_user.failed_login_attempts = 0
    admin_user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 创建响应
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

# 注册子路由
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(admin_user_management_router, prefix="/admin-users", tags=["admin-users"])
router.include_router(frontend_user_management_router, prefix="/frontend-users", tags=["frontend-users"])
router.include_router(simple_user_api_router, prefix="/simple-users", tags=["simple-users"])
if crawler_router:
    router.include_router(crawler_router, prefix="/crawler", tags=["crawler"])
router.include_router(sp_management_router, prefix="/sp", tags=["sp-management"])
router.include_router(draw_prediction_router, prefix="/draw-prediction", tags=["draw-prediction"])
router.include_router(hedging_router, prefix="/hedging", tags=["hedging"])
router.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])
router.include_router(match_admin_router, prefix="/match", tags=["match-admin"])
router.include_router(admin_matches_router, prefix="/matches", tags=["admin-matches"])
router.include_router(monitoring_dashboard_router, prefix="/monitoring", tags=["monitoring"])
router.include_router(logs_router, prefix="/system", tags=["logs"])  # 注册日志模块到/system路径下，这样API端点就是 /api/v1/admin/system/logs/