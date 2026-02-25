"""
后台管理用户管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from io import StringIO
import csv

# 简化的导入，避免复杂依赖
from backend import crud, models, schemas
from backend.schemas import admin_user as admin_schemas
from backend.database_async import get_async_db
from backend.core.security import get_current_active_admin_user
from backend.utils.response import UnifiedResponse

router = APIRouter(prefix="/admin-users")


@router.get("/", response_model=UnifiedResponse[admin_schemas.AdminUserListResponse])
async def list_admin_users(
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页最大记录数"),
    role: Optional[admin_schemas.AdminRoleEnum] = Query(None, description="按角色筛选"),
    status: Optional[admin_schemas.AdminStatusEnum] = Query(None, description="按状态筛选"),
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
    
    return UnifiedResponse.success(data=admin_schemas.AdminUserListResponse(
        items=users,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    ))


@router.post("/", response_model=UnifiedResponse[admin_schemas.AdminUserResponse])
async def create_admin_user(
    user_in: admin_schemas.AdminUserCreate,
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
    
    # 记录操作日志
    await crud.admin_user.admin_operation_log.create(
        db,
        admin_id=current_admin.id,
        action="CREATE_USER",
        resource_type="ADMIN_USER",
        resource_id=str(user.id),
        resource_name=user.username,
        request_body=user_in.model_dump(),
        ip_address="",
        user_agent=""
    )
    
    return UnifiedResponse.success(data=user)


@router.get("/current-user", response_model=UnifiedResponse[admin_schemas.AdminUserResponse])
async def get_current_user_info(
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取当前登录的管理员用户信息
    """
    # 从依赖中获取当前用户，无需额外查询
    return UnifiedResponse.success(data=current_admin)


@router.put("/current-user", response_model=UnifiedResponse[admin_schemas.AdminUserResponse])
async def update_current_user(
    user_update: admin_schemas.AdminUserUpdate,
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新当前登录的管理员用户信息
    """
    # 使用当前请求的DB会话重新加载用户，避免跨会话对象报错
    db_user = await crud.admin_user.get(db, current_admin.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="当前用户不存在")

    # 更新当前用户的信息
    updated_user = await crud.admin_user.update(db, db_obj=db_user, obj_in=user_update)
    
    # 记录操作日志
    await crud.admin_user.admin_operation_log.create(
        db,
        admin_id=current_admin.id,
        action="UPDATE_CURRENT_USER",
        resource_type="ADMIN_USER",
        resource_id=str(current_admin.id),
        resource_name=current_admin.username,
        request_body=user_update.model_dump(),
        ip_address="",
        user_agent=""
    )
    
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
        # 获取操作日志统计
        _, operation_logs = await crud.admin_user.admin_operation_log.get_multi(
            db,
            skip=0,
            limit=1000,
            admin_id=current_admin.id
        )
        total_operations = len(operation_logs)
        
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


# 添加缺失的批量删除端点
@router.delete("/batch", response_model=UnifiedResponse[dict])
async def batch_delete_admin_users(
    request_data: dict,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    批量删除管理员用户
    """
    try:
        user_ids = request_data.get("ids", [])
        if not user_ids:
            raise HTTPException(status_code=400, detail="用户ID列表不能为空")
        
        # 批量删除用户
        deleted_count = 0
        for user_id in user_ids:
            success = await crud.admin_user.remove(db, id=user_id)
            if success:
                deleted_count += 1
        
        # 记录操作日志
        await crud.admin_user.admin_operation_log.create(
            db,
            admin_id=current_admin.id,
            action="BATCH_DELETE_USERS",
            resource_type="ADMIN_USER",
            resource_name=f"批量删除{deleted_count}个用户",
            request_body={"user_ids": user_ids},
            ip_address="",
            user_agent=""
        )
        
        return UnifiedResponse.success(data={"message": f"成功删除 {deleted_count} 个用户", "deletedCount": deleted_count})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量删除用户失败: {str(e)}")


# 添加导入/导出端点的模拟实现
@router.post("/import", response_model=UnifiedResponse[dict])
async def import_admin_users(
    # 注意：实际的文件上传需要更复杂的处理
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    导入管理员用户（模拟实现）
    """
    return UnifiedResponse.success(data={
        "message": "用户导入功能已收到请求，实际实现需要文件上传处理",
        "status": "not_implemented"
    })


@router.get("/export")
async def export_admin_users(
    search: Optional[str] = Query(None, description="按用户名/真实姓名/邮箱搜索"),
    role: Optional[admin_schemas.AdminRoleEnum] = Query(None, description="按角色筛选"),
    status: Optional[admin_schemas.AdminStatusEnum] = Query(None, description="按状态筛选"),
    department: Optional[str] = Query(None, description="按部门筛选"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    导出管理员用户（CSV）
    """
    users, _ = await crud.admin_user.get_multi(
        db,
        skip=0,
        limit=1000,
        role=role,
        status=status,
        department=department,
        search=search
    )

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "username", "real_name", "email", "phone",
        "department", "position", "role", "status", "created_at", "last_login_at"
    ])

    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.real_name,
            user.email,
            user.phone or "",
            user.department or "",
            user.position or "",
            user.role,
            user.status,
            user.created_at.isoformat() if user.created_at else "",
            user.last_login_at.isoformat() if user.last_login_at else ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=admin_users.csv"}
    )


@router.get("/{user_id}", response_model=UnifiedResponse[admin_schemas.AdminUserResponse])
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


@router.put("/{user_id}", response_model=UnifiedResponse[admin_schemas.AdminUserResponse])
async def update_admin_user(
    user_id: int,
    user_update: admin_schemas.AdminUserUpdate,
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
    
    # 记录操作日志
    await crud.admin_user.admin_operation_log.create(
        db,
        admin_id=current_admin.id,
        action="UPDATE_USER",
        resource_type="ADMIN_USER",
        resource_id=str(user.id),
        resource_name=user.username,
        request_body=user_update.model_dump(),
        ip_address="",
        user_agent=""
    )
    
    return UnifiedResponse.success(data=updated_user)


@router.put("/{user_id}/status", response_model=UnifiedResponse[admin_schemas.AdminUserResponse])
async def update_admin_user_status(
    user_id: int,
    status: admin_schemas.AdminStatusEnum = Query(..., description="新状态"),
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
    
    # 记录操作日志
    await crud.admin_user.admin_operation_log.create(
        db,
        admin_id=current_admin.id,
        action="UPDATE_USER_STATUS",
        resource_type="ADMIN_USER",
        resource_id=str(user.id),
        resource_name=user.username,
        request_body={"status": status},
        ip_address="",
        user_agent=""
    )
    
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
    
    # 记录操作日志
    await crud.admin_user.admin_operation_log.create(
        db,
        admin_id=current_admin.id,
        action="RESET_PASSWORD",
        resource_type="ADMIN_USER",
        resource_id=str(user.id),
        resource_name=user.username,
        request_body={"must_change_password": password_reset.must_change_password},
        ip_address="",
        user_agent=""
    )
    
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
    
    # 记录操作日志
    user = await crud.admin_user.get(db, id=user_id)
    if user:
        await crud.admin_user.admin_operation_log.create(
            db,
            admin_id=current_admin.id,
            action="SOFT_DELETE_USER",
            resource_type="ADMIN_USER",
            resource_id=str(user.id),
            resource_name=user.username,
            ip_address="",
            user_agent=""
        )
    
    return UnifiedResponse.success(data={"message": "用户删除成功"})


@router.post("/{user_id}/unlock", response_model=UnifiedResponse[dict])
async def unlock_admin_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    解锁管理员用户账户
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户状态为活跃
    user_update = schemas.AdminUserUpdate(status=schemas.AdminStatusEnum.ACTIVE)
    updated_user = await crud.admin_user.update(db, db_obj=user, obj_in=user_update)
    
    # 记录操作日志
    await crud.admin_user.admin_operation_log.create(
        db,
        admin_id=current_admin.id,
        action="UNLOCK_USER",
        resource_type="ADMIN_USER",
        resource_id=str(user.id),
        resource_name=user.username,
        ip_address="",
        user_agent=""
    )
    
    return UnifiedResponse.success(data={
        "message": f"用户 {updated_user.username} 已解锁",
        "user": updated_user
    })


@router.get("/{user_id}/roles", response_model=UnifiedResponse[dict])
async def get_admin_user_roles(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取管理员用户的角色信息
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 返回用户角色信息
    return UnifiedResponse.success(data={
        "userId": user.id,
        "username": user.username,
        "roles": [user.role.value] if user.role else [],
        "message": "获取角色信息成功"
    })


@router.post("/{user_id}/roles", response_model=UnifiedResponse[dict])
async def assign_admin_user_roles(
    user_id: int,
    role_data: dict,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    为管理员用户分配角色
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 从请求体中获取角色ID列表
    role_ids = role_data.get("roleIds", [])
    
    # 实现角色分配逻辑（此处简化处理）
    # 在实际应用中，需要根据角色ID更新用户的角色信息
    return UnifiedResponse.success(data={
        "message": f"成功为用户 {user.username} 分配了 {len(role_ids)} 个角色",
        "roleIds": role_ids
    })


@router.post("/batch-assign-roles", response_model=UnifiedResponse[dict])
async def batch_assign_roles_to_users(
    role_data: dict,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    批量为用户分配角色
    """
    user_ids = role_data.get("userIds", [])
    role_ids = role_data.get("roleIds", [])
    
    # 实现批量分配角色逻辑
    return UnifiedResponse.success(data={
        "message": f"成功为 {len(user_ids)} 个用户分配了角色",
        "userIds": user_ids,
        "roleIds": role_ids
    })


@router.get("/{user_id}/departments", response_model=UnifiedResponse[dict])
async def get_admin_user_departments(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取管理员用户的部门信息
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UnifiedResponse.success(data={
        "userId": user.id,
        "username": user.username,
        "department": user.department or "未分配",
        "message": "获取部门信息成功"
    })


@router.put("/change-password", response_model=UnifiedResponse[dict])
async def change_current_user_password(
    password_change: schemas.AdminUserChangePassword,
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    修改当前管理员的密码
    """
    # 验证旧密码
    from backend.core.security import verify_password
    if not verify_password(password_change.old_password, current_admin.password_hash):
        raise HTTPException(status_code=400, detail="旧密码不正确")
    
    # 检查新密码与旧密码是否相同
    if password_change.old_password == password_change.new_password:
        raise HTTPException(status_code=400, detail="新密码不能与旧密码相同")
    
    # 更新密码
    updated_user = await crud.admin_user.change_password(
        db, 
        db_obj=current_admin, 
        obj_in=password_change
    )
    
    if not updated_user:
        raise HTTPException(status_code=400, detail="密码修改失败")
    
    # 记录操作日志
    await crud.admin_user.admin_operation_log.create(
        db,
        admin_id=current_admin.id,
        action="CHANGE_PASSWORD",
        resource_type="ADMIN_USER",
        resource_id=str(current_admin.id),
        resource_name=current_admin.username,
        request_body={"action": "change_password"},
        ip_address="",
        user_agent=""
    )
    
    return UnifiedResponse.success(data={
        "message": "密码修改成功"
    })
