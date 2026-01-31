"""
后台管理用户管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

# 简化的导入，避免复杂依赖
from backend import crud, models, schemas
from backend.database_async import get_async_db
from backend.core.security import get_current_active_admin_user
from backend.utils.response import UnifiedResponse

router = APIRouter()


@router.get("/", response_model=UnifiedResponse[schemas.AdminUserListResponse])
async def list_admin_users(
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页最大记录数"),
    role: Optional[schemas.AdminRoleEnum] = Query(None, description="按角色筛选"),
    status: Optional[schemas.AdminStatusEnum] = Query(None, description="按状态筛选"),
    department: Optional[str] = Query(None, description="按部门筛选"),
    search: Optional[str] = Query(None, description="按用户名/真实姓名/邮箱搜索")
):
    """
    获取后台用户列表（分页）
    """
    users, total = await crud.admin_user.get_multi(
        db, skip=skip, limit=limit, role=role, status=status,
        department=department, search=search
    )
    
    return UnifiedResponse.success(data=schemas.AdminUserListResponse(
        items=users,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    ))


@router.post("/", response_model=UnifiedResponse[schemas.AdminUserResponse])
async def create_admin_user(
    user_in: schemas.AdminUserCreate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    创建后台用户
    """
    # 检查用户名和邮箱是否已存在
    existing_user = await crud.admin_user.get_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    existing_email = await crud.admin_user.get_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被使用")
    
    user = await crud.admin_user.create(db, obj_in=user_in, created_by=current_admin.id)
    return UnifiedResponse.success(data=user)


@router.get("/{user_id}", response_model=UnifiedResponse[schemas.AdminUserResponse])
async def get_admin_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取后台用户详情
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 添加创建者姓名信息
    if user.created_by:
        creator = await crud.admin_user.get(db, id=user.created_by)
        user.creator_name = creator.real_name if creator else None
    else:
        user.creator_name = "系统"
    
    return UnifiedResponse.success(data=user)


@router.put("/{user_id}", response_model=UnifiedResponse[schemas.AdminUserResponse])
async def update_admin_user(
    user_id: int,
    user_update: schemas.AdminUserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    更新后台用户信息
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    updated_user = await crud.admin_user.update(db, db_obj=user, obj_in=user_update)
    return UnifiedResponse.success(data=updated_user)


@router.put("/{user_id}/status", response_model=UnifiedResponse[schemas.AdminUserResponse])
async def update_admin_user_status(
    user_id: int,
    status: schemas.AdminStatusEnum = Query(..., description="新状态"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    更新后台用户状态
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    updated_user = await crud.admin_user.update_status(db, db_obj=user, status=status)
    return UnifiedResponse.success(data=updated_user)


@router.put("/{user_id}/reset-password", response_model=UnifiedResponse[dict])
async def reset_admin_user_password(
    user_id: int,
    password_reset: schemas.AdminUserResetPassword,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    重置后台用户密码
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    await crud.admin_user.reset_password(db, db_obj=user, obj_in=password_reset)
    return UnifiedResponse.success(data={"message": "密码重置成功"})


@router.delete("/{user_id}", response_model=UnifiedResponse[dict])
async def delete_admin_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    删除后台用户（软删除）
    """
    success = await crud.admin_user.remove(db, id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UnifiedResponse.success(data={"message": "用户删除成功"})


@router.get("/current-user", response_model=UnifiedResponse[schemas.AdminUserResponse])
async def get_current_user_info(
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取当前登录的管理员用户信息
    """
    # 从依赖中获取当前用户，无需额外查询
    return UnifiedResponse.success(data=current_admin)


@router.put("/current-user", response_model=UnifiedResponse[schemas.AdminUserResponse])
async def update_current_user(
    user_update: schemas.AdminUserUpdate,
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新当前登录的管理员用户信息
    """
    # 更新当前用户的信息
    updated_user = await crud.admin_user.update(db, db_obj=current_admin, obj_in=user_update)
    return UnifiedResponse.success(data=updated_user)


@router.get("/stats", response_model=UnifiedResponse[schemas.AdminUserStatsResponse])
async def get_admin_user_stats(
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取后台用户统计信息
    """
    stats = await crud.admin_user.get_stats(db)
    return UnifiedResponse.success(data=schemas.AdminUserStatsResponse(**stats))


@router.get("/login-history", response_model=UnifiedResponse[List[dict]])
async def get_current_user_login_history(
    limit: int = Query(10, ge=1, le=100, description="返回记录数量"),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取当前管理员的登录历史
    """
    # 获取当前用户的登录历史
    try:
        _, login_logs = await crud.admin_login_log.get_multi(
            db, 
            skip=0, 
            limit=limit, 
            admin_id=current_admin.id
        )
        # 转换为前端需要的格式
        result = []
        for log in login_logs:
            result.append({
                "id": log.id,
                "loginTime": log.login_at.isoformat() if log.login_at else None,
                "ip": log.login_ip,
                "location": "未知",  # 可以通过IP查询地理位置
                "device": "未知",  # 设备信息可以从前端传入
                "browser": "未知",  # 浏览器信息可以从前端传入
                "success": log.success
            })
        return UnifiedResponse.success(data=result)
    except Exception as e:
        # 如果出现错误，返回空数组
        return UnifiedResponse.success(data=[])


@router.get("/stats/overview", response_model=UnifiedResponse[dict])
async def get_current_user_personal_stats(
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取当前管理员的个人统计数据
    """
    try:
        # 查询当前用户的登录历史统计
        _, login_logs = await crud.admin_login_log.get_multi(
            db,
            skip=0,
            limit=1000,  # 获取全部登录记录
            admin_id=current_admin.id
        )
        
        # 计算统计信息
        total_logins = len(login_logs)
        
        # 计算本月登录次数
        from datetime import datetime
        this_month = 0
        current_month = datetime.now().month
        current_year = datetime.now().year
        for log in login_logs:
            if log.login_at.month == current_month and log.login_at.year == current_year and log.success:
                this_month += 1
        
        # 这里可以根据需要计算更多的统计信息
        # 比如操作日志数量等
        total_operations = 0  # 暂时设为0，需要查询操作日志表
        
        return UnifiedResponse.success(data={
            "totalLogins": total_logins,
            "thisMonthLogins": this_month,
            "totalOperations": total_operations
        })
    except Exception as e:
        # 如果没有实现相关查询函数，返回默认值
        return UnifiedResponse.success(data={
            "totalLogins": 0,
            "thisMonthLogins": 0,
            "totalOperations": 0
        })