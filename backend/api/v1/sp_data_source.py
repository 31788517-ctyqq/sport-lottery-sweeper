"""
SP数据源管理API - 实现数据源的增删改查和测试连接功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import Optional, Dict, Any
from pydantic import BaseModel
import json
from datetime import datetime
import os
from pathlib import Path

from backend.api.deps import get_current_admin_user
from backend.models.admin_user import AdminUser

# 模拟数据源存储
data_sources = []
next_id = 1

# 文件上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Pydantic模型
class DataSourceCreate(BaseModel):
    name: str
    type: str
    url: str
    config: Optional[str] = '{}'
    status: bool = True


class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    config: Optional[str] = None
    status: Optional[bool] = None


class DataSourceResponse(BaseModel):
    id: int
    name: str
    type: str
    url: str
    config: str
    status: bool
    last_update: Optional[str] = None
    error_rate: float = 0.0


class DataSourceListResponse(BaseModel):
    items: list[DataSourceResponse]
    total: int


class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class FileUploadResponse(BaseModel):
    filename: str
    filepath: str
    size: int
    message: str


# 创建路由
router = APIRouter(prefix="/sp", tags=["sp-data-source"])


@router.get("/data-sources", response_model=DataSourceListResponse)
async def list_data_sources(
    name: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """获取数据源列表"""
    filtered_sources = [
        ds for ds in data_sources
        if (not name or name.lower() in ds['name'].lower()) and
           (not type or ds['type'] == type) and
           (status is None or ds['status'] == status)
    ]
    
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_sources = filtered_sources[start_idx:end_idx]
    
    return DataSourceListResponse(
        items=paginated_sources,
        total=len(filtered_sources)
    )


@router.post("/data-sources", response_model=DataSourceResponse)
async def create_data_source(
    data: DataSourceCreate,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """创建数据源"""
    global next_id
    
    # 验证输入
    if data.config:
        try:
            json.loads(data.config)
        except ValueError:
            raise HTTPException(status_code=400, detail="配置信息必须是有效的JSON格式")
    
    new_source = DataSourceResponse(
        id=next_id,
        name=data.name,
        type=data.type,
        url=data.url,
        config=data.config or '{}',
        status=data.status,
        last_update=datetime.now().isoformat()
    ).dict()
    
    data_sources.append(new_source)
    next_id += 1
    
    return new_source


@router.put("/data-sources/{source_id}", response_model=DataSourceResponse)
async def update_data_source(
    source_id: int,
    data: DataSourceUpdate,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """更新数据源"""
    for i, ds in enumerate(data_sources):
        if ds['id'] == source_id:
            update_data = data.dict(exclude_unset=True)
            for key, value in update_data.items():
                if key == 'config' and value:
                    try:
                        json.loads(value)
                    except ValueError:
                        raise HTTPException(status_code=400, detail="配置信息必须是有效的JSON格式")
                
                if value is not None:
                    data_sources[i][key] = value
            
            data_sources[i]['last_update'] = datetime.now().isoformat()
            return data_sources[i]
    
    raise HTTPException(status_code=404, detail="数据源不存在")


@router.delete("/data-sources/{source_id}")
async def delete_data_source(
    source_id: int,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """删除数据源"""
    for i, ds in enumerate(data_sources):
        if ds['id'] == source_id:
            # 如果是文件类型，尝试删除实际文件
            if ds['type'] == 'file' and ds['url'].startswith('/uploads/'):
                filepath = UPLOAD_DIR / ds['url'][len('/uploads/'):]
                if filepath.exists():
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass  # 删除失败不影响删除数据记录
            
            del data_sources[i]
            return {"message": "数据源删除成功"}
    
    raise HTTPException(status_code=404, detail="数据源不存在")


@router.post("/data-sources/{source_id}/test", response_model=TestConnectionResponse)
async def test_data_source_connection(
    source_id: int,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """测试数据源连接"""
    for ds in data_sources:
        if ds['id'] == source_id:
            # 这里应该实现真正的连接测试逻辑
            # 为了演示，我们简单返回成功
            try:
                # 模拟连接测试逻辑
                # 这里可以添加具体的连接测试代码
                if ds['type'] == 'api':
                    # 模拟API连接测试
                    import requests
                    response = requests.get(ds['url'], timeout=5)
                    success = response.status_code == 200
                    message = f"API连接测试{'成功' if success else '失败'}"
                    data = {"status_code": response.status_code} if success else None
                elif ds['type'] == 'file':
                    # 模拟文件连接测试
                    import os
                    # 处理上传文件路径
                    if ds['url'].startswith('/uploads/'):
                        filepath = UPLOAD_DIR / ds['url'][len('/uploads/'):]
                    else:
                        filepath = Path(ds['url'])
                    
                    exists = filepath.exists()
                    success = exists
                    message = f"文件连接测试{'成功' if success else '失败'}"
                    data = {"exists": exists} if success else None
                else:
                    success = False
                    message = f"未知的数据源类型: {ds['type']}"
                    data = None
                
                return TestConnectionResponse(
                    success=success,
                    message=message,
                    data=data
                )
            except Exception as e:
                return TestConnectionResponse(
                    success=False,
                    message=f"连接测试失败: {str(e)}",
                    data=None
                )
    
    raise HTTPException(status_code=404, detail="数据源不存在")


@router.post("/upload-file", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """上传文件接口"""
    # 检查文件类型
    allowed_extensions = {".csv", ".xlsx", ".xls", ".json", ".txt"}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_extension}. 支持的类型: {allowed_extensions}"
        )
    
    # 检查文件大小 (最大20MB)
    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:  # 20MB
        raise HTTPException(
            status_code=400,
            detail="文件大小不能超过20MB"
        )
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{file.filename}"
    filepath = UPLOAD_DIR / unique_filename
    
    # 保存文件
    with open(filepath, "wb") as f:
        f.write(contents)
    
    # 返回文件信息
    return FileUploadResponse(
        filename=unique_filename,
        filepath=f"/uploads/{unique_filename}",
        size=len(contents),
        message="文件上传成功"
    )