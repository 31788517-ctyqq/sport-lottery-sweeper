"""
竞彩赛程API - 管理员接口
实现竞彩赛程的增删改查功能
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path

# 从本地deps模块导入，避免跨包引用问题
from ..deps import get_current_admin_user

# 移除路由器的prefix，因为已经在main.py中指定了完整路径
router = APIRouter(tags=["admin-lottery-schedules"])

# 模拟竞彩赛程数据
mock_lottery_schedules = [
    {
        "id": 1,
        "match_date": "2024-06-15",
        "round_number": "第1轮",
        "match_count": 10,
        "status": "completed",
        "created_at": "2024-06-10T10:00:00Z",
        "updated_at": "2024-06-15T22:00:00Z"
    },
    {
        "id": 2,
        "match_date": "2024-06-16",
        "round_number": "第2轮",
        "match_count": 12,
        "status": "upcoming",
        "created_at": "2024-06-11T10:00:00Z",
        "updated_at": "2024-06-11T10:00:00Z"
    },
    {
        "id": 3,
        "match_date": "2024-06-17",
        "round_number": "第3轮",
        "match_count": 8,
        "status": "scheduled",
        "created_at": "2024-06-12T10:00:00Z",
        "updated_at": "2024-06-12T10:00:00Z"
    }
]

@router.get("/", response_model=dict)
async def list_lottery_schedules(
    current_user: dict = Depends(get_current_admin_user),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, description="过滤状态: upcoming, ongoing, completed, scheduled")
):
    """
    获取竞彩赛程列表
    """
    try:
        # 过滤数据
        filtered_schedules = mock_lottery_schedules
        if status:
            filtered_schedules = [s for s in filtered_schedules if s["status"] == status]
        
        # 分页
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_data = filtered_schedules[start_idx:end_idx]
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": paginated_data,
                "total": len(filtered_schedules),
                "page": page,
                "size": size,
                "pages": (len(filtered_schedules) + size - 1) // size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取竞彩赛程列表失败: {str(e)}")



@router.get("/{schedule_id}", response_model=dict)
async def get_lottery_schedule(
    schedule_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    获取单个竞彩赛程详情
    """
    try:
        schedule = next((s for s in mock_lottery_schedules if s["id"] == schedule_id), None)
        if not schedule:
            raise HTTPException(status_code=404, detail="竞彩赛程不存在")
        
        return {
            "code": 200,
            "message": "success",
            "data": schedule
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取竞彩赛程详情失败: {str(e)}")


@router.post("/", response_model=dict)
async def create_lottery_schedule(
    current_user: dict = Depends(get_current_admin_user)
):
    """
    创建竞彩赛程
    """
    try:
        # 模拟创建一个新的赛程
        new_schedule = {
            "id": len(mock_lottery_schedules) + 1,
            "match_date": "2024-06-20",
            "round_number": f"第{len(mock_lottery_schedules) + 1}轮",
            "match_count": 10,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        mock_lottery_schedules.append(new_schedule)
        
        return {
            "code": 200,
            "message": "竞彩赛程创建成功",
            "data": new_schedule
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建竞彩赛程失败: {str(e)}")


@router.put("/{schedule_id}", response_model=dict)
async def update_lottery_schedule(
    schedule_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    更新竞彩赛程
    """
    try:
        schedule = next((s for s in mock_lottery_schedules if s["id"] == schedule_id), None)
        if not schedule:
            raise HTTPException(status_code=404, detail="竞彩赛程不存在")
        
        # 模拟更新
        schedule["status"] = "updated"
        schedule["updated_at"] = datetime.now().isoformat()
        
        return {
            "code": 200,
            "message": "竞彩赛程更新成功",
            "data": schedule
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新竞彩赛程失败: {str(e)}")


@router.delete("/{schedule_id}", response_model=dict)
async def delete_lottery_schedule(
    schedule_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    删除竞彩赛程
    """
    try:
        schedule = next((s for s in mock_lottery_schedules if s["id"] == schedule_id), None)
        if not schedule:
            raise HTTPException(status_code=404, detail="竞彩赛程不存在")
        
        mock_lottery_schedules.remove(schedule)
        
        return {
            "code": 200,
            "message": "竞彩赛程删除成功",
            "data": {"deleted_id": schedule_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除竞彩赛程失败: {str(e)}")