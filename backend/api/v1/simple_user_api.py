"""
简化的用户管理API - 避免复杂的导入问题
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

# 使用同步数据库
def get_db():
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(tags=["后台用户管理"])

@router.get("/", response_model=dict)
async def list_admin_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取后台用户列表"""
    try:
        # 使用原始SQL查询避免ORM模型导入冲突
        sql_base = "SELECT * FROM admin_users WHERE 1=1"
        params = {}
        
        # 构建查询条件和参数
        if search:
            sql_base += " AND (username LIKE :search OR full_name LIKE :search OR email LIKE :search)"
            params['search'] = f'%{search}%'
        if role:
            sql_base += " AND role = :role"
            params['role'] = role
        
        # 注意：现有表没有 status、department 字段，忽略这两个过滤条件
        
        # 获取总数
        count_sql = "SELECT COUNT(*) as total FROM admin_users WHERE 1=1"
        if search:
            count_sql += " AND (username LIKE :search OR full_name LIKE :search OR email LIKE :search)"
        if role:
            count_sql += " AND role = :role"
        count_result = db.execute(text(count_sql), params).fetchone()
        total = count_result[0] if count_result else 0
        
        # 分页参数
        limit = size
        offset = (page - 1) * size
        params['limit'] = limit
        params['offset'] = offset
        
        # 分页查询
        sql = "SELECT * FROM admin_users WHERE 1=1"
        if search:
            sql += " AND (username LIKE :search OR full_name LIKE :search OR email LIKE :search)"
        if role:
            sql += " AND role = :role"
        sql += " ORDER BY id LIMIT :limit OFFSET :offset"
        
        result = db.execute(text(sql), params).fetchall()
        
        # 转换为字典格式 (匹配现有表字段)
        items = []
        for row in result:
            items.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "full_name": row[3],
                "role": row[4],
                "is_active": bool(row[5]),
                "created_at": row[6].isoformat() if hasattr(row[6], 'isoformat') else str(row[6]),
                "updated_at": row[7].isoformat() if hasattr(row[7], 'isoformat') else str(row[7])
            })
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")

@router.get("/{user_id}", response_model=dict)
async def get_admin_user(user_id: int, db: Session = Depends(get_db)):
    """获取后台用户详情"""
    try:
        # 使用原始SQL查询避免ORM模型导入冲突
        sql = "SELECT * FROM admin_users WHERE id = :user_id"
        result = db.execute(text(sql), {"user_id": user_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {
            "id": result[0],  # id
            "username": result[1],  # username
            "email": result[2],  # email
            "real_name": result[3],  # real_name
            "phone": result[4],  # phone
            "department": result[5],  # department
            "position": result[6],  # position
            "role": result[7],  # role
            "status": result[8],  # status
            "two_factor_enabled": bool(result[9]),  # two_factor_enabled
            "is_verified": bool(result[10]),  # is_verified
            "login_count": result[11],  # login_count
            "last_login_at": result[12].isoformat() if result[12] else None,  # last_login_at
            "last_login_ip": result[13],  # last_login_ip
            "failed_login_attempts": result[14],  # failed_login_attempts
            "locked_until": result[15].isoformat() if result[15] else None,  # locked_until
            "must_change_password": bool(result[16]),  # must_change_password
            "created_by": result[17],  # created_by
            "remarks": result[18],  # remarks
            "created_at": result[19].isoformat() if result[19] else None,  # created_at
            "updated_at": result[20].isoformat() if result[20] else None  # updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户详情失败: {str(e)}")

@router.get("/stats", response_model=dict)
async def get_admin_user_stats(db: Session = Depends(get_db)):
    """获取后台用户统计信息"""
    try:
        # 使用原始SQL查询避免ORM模型导入冲突
        
        # 总数
        total_result = db.execute(text("SELECT COUNT(*) as total FROM admin_users")).fetchone()
        total = total_result[0] if total_result else 0
        
        # 按角色统计
        role_stats = {}
        roles = ['super_admin', 'admin', 'operator', 'auditor', 'finance_admin']
        for role in roles:
            count_result = db.execute(text("SELECT COUNT(*) as count FROM admin_users WHERE role = :role"), {"role": role}).fetchone()
            role_stats[role] = count_result[0] if count_result else 0
        
        # 按状态统计
        status_stats = {}
        statuses = ['active', 'inactive', 'locked', 'pending']
        for status in statuses:
            count_result = db.execute(text("SELECT COUNT(*) as count FROM admin_users WHERE status = :status"), {"status": status}).fetchone()
            status_stats[status] = count_result[0] if count_result else 0
        
        # 激活用户数
        active_result = db.execute(text("SELECT COUNT(*) as count FROM admin_users WHERE status = 'active'")).fetchone()
        active_users = active_result[0] if active_result else 0
        
        # 锁定用户数
        locked_result = db.execute(text("SELECT COUNT(*) as count FROM admin_users WHERE status = 'locked'")).fetchone()
        locked_users = locked_result[0] if locked_result else 0
        
        # 双因素认证用户数
        two_factor_result = db.execute(text("SELECT COUNT(*) as count FROM admin_users WHERE two_factor_enabled = 1")).fetchone()
        two_factor_enabled_count = two_factor_result[0] if two_factor_result else 0
        
        return {
            "total_users": total,
            "active_users": active_users,
            "locked_users": locked_users,
            "two_factor_enabled_count": two_factor_enabled_count,
            "role_distribution": role_stats,
            "status_distribution": status_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
