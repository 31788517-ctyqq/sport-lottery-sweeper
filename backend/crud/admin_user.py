"""
后台管理用户CRUD操作
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
import json
from passlib.context import CryptContext

from ..models.admin_user import AdminUser, AdminOperationLog, AdminLoginLog, AdminRoleEnum, AdminStatusEnum
from ..schemas.admin_user import (
    AdminUserCreate, AdminUserUpdate, AdminUserChangePassword, AdminUserResetPassword
)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CRUDAdminUser:
    """后台用户CRUD操作类"""
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)
    
    async def get(self, db: AsyncSession, id: int) -> Optional[AdminUser]:
        """根据ID获取后台用户"""
        result = await db.execute(select(AdminUser).filter(AdminUser.id == id))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[AdminUser]:
        """根据用户名获取后台用户"""
        result = await db.execute(select(AdminUser).filter(AdminUser.username == username))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[AdminUser]:
        """根据邮箱获取后台用户"""
        result = await db.execute(select(AdminUser).filter(AdminUser.email == email))
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        role: Optional[AdminRoleEnum] = None,
        status: Optional[AdminStatusEnum] = None,
        department: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[AdminUser], int]:
        """获取后台用户列表（带分页和筛选）"""
        query = select(AdminUser)
        
        # 构建筛选条件
        conditions = []
        if role:
            conditions.append(AdminUser.role == role)
        if status:
            conditions.append(AdminUser.status == status)
        if department:
            conditions.append(AdminUser.department == department)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    AdminUser.username.ilike(search_pattern),
                    AdminUser.real_name.ilike(search_pattern),
                    AdminUser.email.ilike(search_pattern)
                )
            )
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # 获取总数
        count_query = select(func.count()).select_from(AdminUser)
        if conditions:
            count_query = count_query.filter(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 获取分页数据
        query = query.order_by(desc(AdminUser.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    async def create(
        self,
        db: AsyncSession,
        obj_in: AdminUserCreate,
        created_by: Optional[int] = None
    ) -> AdminUser:
        """创建后台用户"""
        db_obj = AdminUser(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=self.get_password_hash(obj_in.password),
            real_name=obj_in.real_name,
            phone=obj_in.phone,
            department=obj_in.department,
            position=obj_in.position,
            role=obj_in.role,
            login_allowed_ips=obj_in.login_allowed_ips,
            two_factor_enabled=obj_in.two_factor_enabled,
            remarks=obj_in.remarks,
            created_by=created_by,
            status=AdminStatusEnum.INACTIVE,  # 默认未激活状态
            must_change_password=True  # 首次登录必须修改密码
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        db_obj: AdminUser,
        obj_in: AdminUserUpdate
    ) -> AdminUser:
        """更新后台用户信息"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "preferences":
                if value is None:
                    continue
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
            setattr(db_obj, field, value)
        
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def change_password(
        self,
        db: AsyncSession,
        db_obj: AdminUser,
        obj_in: AdminUserChangePassword
    ) -> bool:
        """修改密码（用户自己操作）"""
        # 验证旧密码
        if not self.verify_password(obj_in.old_password, db_obj.password_hash):
            return False
        
        # 更新新密码
        db_obj.password_hash = self.get_password_hash(obj_in.new_password)
        db_obj.must_change_password = False
        db_obj.password_expires_at = datetime.utcnow() + timedelta(days=90)  # 90天后过期
        db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        await db.commit()
        return True
    
    async def reset_password(
        self,
        db: AsyncSession,
        db_obj: AdminUser,
        obj_in: AdminUserResetPassword
    ) -> AdminUser:
        """重置密码（管理员操作）"""
        db_obj.password_hash = self.get_password_hash(obj_in.new_password)
        db_obj.must_change_password = obj_in.must_change_password
        db_obj.failed_login_attempts = 0
        db_obj.locked_until = None
        db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_status(
        self,
        db: AsyncSession,
        db_obj: AdminUser,
        status: AdminStatusEnum
    ) -> AdminUser:
        """更新用户状态"""
        db_obj.status = status
        if status == AdminStatusEnum.ACTIVE:
            db_obj.is_verified = True
        elif status == AdminStatusEnum.LOCKED:
            db_obj.locked_until = datetime.utcnow() + timedelta(hours=24)
        db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def record_login_attempt(
        self,
        db: AsyncSession,
        db_obj: AdminUser,
        success: bool,
        ip_address: str
    ) -> None:
        """记录登录尝试"""
        if success:
            db_obj.login_count += 1
            db_obj.last_login_at = datetime.utcnow()
            db_obj.last_login_ip = ip_address
            db_obj.failed_login_attempts = 0
        else:
            db_obj.failed_login_attempts += 1
            db_obj.last_failed_login_at = datetime.utcnow()
            
            # 连续失败5次，锁定账户1小时
            if db_obj.failed_login_attempts >= 5:
                db_obj.status = AdminStatusEnum.LOCKED
                db_obj.locked_until = datetime.utcnow() + timedelta(hours=1)
        
        db.add(db_obj)
        await db.commit()
    
    async def check_ip_whitelist(
        self,
        db_obj: AdminUser,
        ip_address: str
    ) -> bool:
        """检查IP是否在白名单中"""
        if not db_obj.login_allowed_ips or len(db_obj.login_allowed_ips) == 0:
            return True  # 未配置白名单，允许所有IP
        return ip_address in db_obj.login_allowed_ips
    
    async def is_locked(self, db_obj: AdminUser) -> bool:
        """检查账户是否被锁定"""
        if db_obj.status == AdminStatusEnum.LOCKED:
            if db_obj.locked_until and db_obj.locked_until > datetime.utcnow():
                return True
            # 锁定时间已过，自动解锁
            return False
        return False
    
    async def remove(self, db: AsyncSession, id: int) -> bool:
        """删除后台用户（软删除）"""
        db_obj = await self.get(db, id)
        if db_obj:
            db_obj.status = AdminStatusEnum.INACTIVE
            db_obj.updated_at = datetime.utcnow()
            db.add(db_obj)
            await db.commit()
            return True
        return False
    
    async def get_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """获取后台用户统计信息"""
        # 总用户数
        total_result = await db.execute(select(func.count()).select_from(AdminUser))
        total_users = total_result.scalar()
        
        # 按状态统计
        status_counts = {}
        for status in AdminStatusEnum:
            count_result = await db.execute(
                select(func.count()).select_from(AdminUser).filter(AdminUser.status == status)
            )
            status_counts[status.value] = count_result.scalar()
        
        # 按角色统计
        role_counts = {}
        for role in AdminRoleEnum:
            count_result = await db.execute(
                select(func.count()).select_from(AdminUser).filter(AdminUser.role == role)
            )
            role_counts[role.value] = count_result.scalar()
        
        # 最近24小时登录人数
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_login_result = await db.execute(
            select(func.count(func.distinct(AdminUser.id)))
            .select_from(AdminUser)
            .filter(AdminUser.last_login_at >= yesterday)
        )
        recent_logins = recent_login_result.scalar()
        
        # 启用双因素认证的用户数
        two_factor_result = await db.execute(
            select(func.count()).select_from(AdminUser).filter(AdminUser.two_factor_enabled == True)
        )
        two_factor_count = two_factor_result.scalar()
        
        return {
            "total_users": total_users,
            "active_users": status_counts.get("active", 0),
            "inactive_users": status_counts.get("inactive", 0),
            "suspended_users": status_counts.get("suspended", 0),
            "locked_users": status_counts.get("locked", 0),
            "users_by_role": role_counts,
            "recent_logins": recent_logins,
            "two_factor_enabled_count": two_factor_count
        }


class CRUDAdminOperationLog:
    """后台操作日志CRUD操作类"""
    
    async def create(
        self,
        db: AsyncSession,
        admin_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        method: str = "GET",
        path: str = "",
        query_params: Dict[str, Any] = None,
        request_body: Dict[str, Any] = None,
        status_code: int = 200,
        response_data: Dict[str, Any] = None,
        ip_address: str = "",
        user_agent: str = "",
        changes_before: Dict[str, Any] = None,
        changes_after: Dict[str, Any] = None,
        duration_ms: Optional[int] = None
    ) -> AdminOperationLog:
        """创建操作日志"""
        db_obj = AdminOperationLog(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            method=method,
            path=path,
            query_params=query_params or {},
            request_body=request_body,
            status_code=status_code,
            response_data=response_data,
            ip_address=ip_address,
            user_agent=user_agent,
            changes_before=changes_before,
            changes_after=changes_after,
            duration_ms=duration_ms
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        admin_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[AdminOperationLog], int]:
        """获取操作日志列表"""
        query = select(AdminOperationLog)
        
        # 构建筛选条件
        conditions = []
        if admin_id:
            conditions.append(AdminOperationLog.admin_id == admin_id)
        if action:
            conditions.append(AdminOperationLog.action == action)
        if resource_type:
            conditions.append(AdminOperationLog.resource_type == resource_type)
        if start_date:
            conditions.append(AdminOperationLog.created_at >= start_date)
        if end_date:
            conditions.append(AdminOperationLog.created_at <= end_date)
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # 获取总数
        count_query = select(func.count()).select_from(AdminOperationLog)
        if conditions:
            count_query = count_query.filter(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 获取分页数据
        query = query.order_by(desc(AdminOperationLog.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


class CRUDAdminLoginLog:
    """后台登录日志CRUD操作类"""
    
    async def create(
        self,
        db: AsyncSession,
        admin_id: int,
        login_ip: str,
        success: bool = True,
        failure_reason: Optional[str] = None,
        user_agent: Optional[str] = None,
        two_factor_used: bool = False,
        ip_whitelisted: bool = False,
        **kwargs
    ) -> AdminLoginLog:
        """创建登录日志"""
        db_obj = AdminLoginLog(
            admin_id=admin_id,
            login_ip=login_ip,
            success=success,
            failure_reason=failure_reason,
            user_agent=user_agent,
            two_factor_used=two_factor_used,
            ip_whitelisted=ip_whitelisted,
            **kwargs
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        admin_id: Optional[int] = None,
        success: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[AdminLoginLog], int]:
        """获取登录日志列表"""
        query = select(AdminLoginLog)
        
        # 构建筛选条件
        conditions = []
        if admin_id is not None:
            conditions.append(AdminLoginLog.admin_id == admin_id)
        if success is not None:
            conditions.append(AdminLoginLog.success == success)
        if start_date:
            conditions.append(AdminLoginLog.login_at >= start_date)
        if end_date:
            conditions.append(AdminLoginLog.login_at <= end_date)
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # 获取总数
        count_query = select(func.count()).select_from(AdminLoginLog)
        if conditions:
            count_query = count_query.filter(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 获取分页数据
        query = query.order_by(desc(AdminLoginLog.login_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


# 实例化CRUD对象
admin_user = CRUDAdminUser()
admin_operation_log = CRUDAdminOperationLog()
admin_login_log = CRUDAdminLoginLog()

# 将CRUD类中的方法导出到模块级别，以便直接导入
get = admin_user.get
get_by_username = admin_user.get_by_username
get_by_email = admin_user.get_by_email
get_multi = admin_user.get_multi
create = admin_user.create
update = admin_user.update
change_password = admin_user.change_password
reset_password = admin_user.reset_password
update_status = admin_user.update_status
record_login_attempt = admin_user.record_login_attempt
check_ip_whitelist = admin_user.check_ip_whitelist
is_locked = admin_user.is_locked
remove = admin_user.remove
get_stats = admin_user.get_stats
