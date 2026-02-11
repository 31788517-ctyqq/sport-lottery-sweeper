"""
100qiu数据源API - 专门处理100qiu数据源的获取和管理
"""
import json
from datetime import datetime as dt, datetime
import os
import requests
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.exceptions import HTTPException
from pydantic import ValidationError, BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.exc import SQLAlchemyError

# 导入数据库依赖
from ...database import get_db

# 导入数据模型
from ...models.data_sources import DataSource

# 添加日志服务导入
from ...services.log_service import LogService
from ...models.log_entry import LogEntry
from ...schemas.log_entry import LogEntryCreate

router = APIRouter()
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
_NO_PROXY_SESSION = requests.Session()
_NO_PROXY_SESSION.trust_env = False


def validation_exception_handler(request: Request, exc: ValidationError):
    """
    自定义验证异常处理器，返回前端期望的格式
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error['loc']),
            "message": error['msg'],
            "type": error['type']
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "data": {
                "errors": errors
            }
        }
    )


class DataSource100qiuCreate(BaseModel):
    name: str
    url: str
    date_time: Optional[str] = "latest"  # 默认获取最新数据
    update_frequency: Optional[int] = 60  # 更新频率，默认60分钟
    field_mapping: Optional[Dict[str, str]] = {}
    status: Optional[str] = "online"  # 添加status字段，默认为online


class DataSource100qiuUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    date_time: Optional[str] = None
    update_frequency: Optional[int] = None
    field_mapping: Optional[Dict[str, str]] = None
    status: Optional[str] = None


class DataSource100qiuResponse(BaseModel):
    id: int
    source_id: str
    name: str
    type: str
    url: str
    status: str
    config: Dict[str, Any]
    last_update: Optional[str] = None
    error_rate: float = 0.0
    created_at: str
    updated_at: str
    created_by: Optional[int] = None
    last_error: Optional[str] = None
    last_error_time: Optional[str] = None


class DataSource100qiuListResponse(BaseModel):
    items: List[DataSource100qiuResponse]
    total: int


class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    sample_data: Optional[List[Dict[str, Any]]] = None


class FetchDataResponse(BaseModel):
    success: bool
    message: str
    total_fetched: int
    sample_data: Optional[List[Dict[str, Any]]] = None


router = APIRouter(prefix="/data-source-100qiu", tags=["data-source-100qiu"])

@router.get("/date-time-options")
async def get_date_time_options(db: Session = Depends(get_db)):
    """Return available date_time options from successful 100qiu sources."""
    try:
        sources = (
            db.query(DataSource)
            .filter(DataSource.last_error.is_(None))
            .filter(DataSource.last_update.isnot(None))
            .all()
        )

        values = set()
        for source in sources:
            config = source.config_dict or {}
            status_val = source.status
            is_online = status_val == 1 or status_val == "online"
            is_100qiu = source.type == "100qiu" or config.get("source_type") == "100qiu"
            if not is_online:
                continue
            if not is_100qiu:
                continue
            date_time = config.get("date_time")
            if date_time and str(date_time).lower() != "latest":
                values.add(str(date_time))

        options = sorted(values, reverse=True)

        return {
            "success": True,
            "data": {"options": options, "total": len(options)},
            "message": "date_time options loaded"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load date_time options: {str(e)}",
            "data": {"options": [], "total": 0}
        }


@router.get("/latest-matches")
async def get_latest_100qiu_matches(
    include_raw: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Return matches from the latest date_time (latest period) stored from 100qiu data source."""
    try:
        sources = db.query(DataSource).all()
        source_count = 0
        for source in sources:
            config = source.config_dict or {}
            if source.type == "100qiu" or config.get("source_type") == "100qiu":
                source_count += 1
        if source_count == 0:
            return {
                "success": False,
                "message": "No 100qiu data source configured",
                "data": {"matches": [], "total": 0}
            }

        from ...models.matches import FootballMatch

        # 获取所有100qiu比赛
        all_matches = db.query(FootballMatch).all()
        
        if not all_matches:
            return {
                "success": True,
                "data": {
                    "matches": [],
                    "total": 0
                },
                "message": "No matches found"
            }
        
        # 提取所有非空的date_time并找到最新的date_time
        date_times = [match.date_time for match in all_matches if match.date_time]
        if not date_times:
            return {
                "success": True,
                "data": {
                    "matches": [],
                    "total": 0
                },
                "message": "No matches with date_time found"
            }
        
        # 按字符串比较找到最新的date_time（格式如：2026-02-13 20:00:00）
        latest_date_time = max(date_times)
        
        # 过滤出最新date_time对应的所有比赛
        latest_matches = [match for match in all_matches if match.date_time == latest_date_time]

        payload = []
        for match in latest_matches:
            item = {
                "match_id": match.match_id,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "league": match.league,
                "match_time": match.match_time.isoformat() if match.match_time else None,
                "date_time": match.date_time,  # 添加date_time字段供前端参考
                "power_home": None,
                "power_away": None,
                "win_pan_home": None,
                "win_pan_away": None,
                "p_level": None,
                "delta_wp": None,
                "rq": None
            }
            if include_raw:
                item["data_source"] = getattr(match, "data_source", None)
                item["source_attributes"] = getattr(match, "source_attributes", None)
            payload.append(item)

        return {
            "success": True,
            "data": {
                "matches": payload,
                "total": len(payload),
                "latest_date_time": latest_date_time  # 返回最新date_time信息
            },
            "message": f"Loaded {len(payload)} matches from latest period ({latest_date_time})"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load latest matches: {str(e)}",
            "data": {"matches": [], "total": 0}
        }


@router.get("/match/{match_id}")
async def get_100qiu_match_raw(
    match_id: str,
    db: Session = Depends(get_db)
):
    """Return stored 100qiu raw payload for a match_id."""
    try:
        from ...models.matches import FootballMatch

        match = db.query(FootballMatch).filter(FootballMatch.match_id == match_id).first()
        if not match:
            return {
                "success": False,
                "message": "Match not found",
                "data": None
            }

        raw = getattr(match, "source_attributes", None)
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                pass

        return {
            "success": True,
            "message": "Match raw loaded",
            "data": {
                "match_id": match.match_id,
                "source_attributes": raw
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load match raw: {str(e)}",
            "data": None
        }


@router.post("/")
async def create_100qiu_data_source(
    data: DataSource100qiuCreate,
    db: Session = Depends(get_db)
):
    """创建100qiu数据源配置"""
    try:
        # 构建配置
        config = {
            "date_time": data.date_time,
            "update_frequency": data.update_frequency
        }
        
        # 创建数据源记录，开发环境中暂时设置created_by为固定值
        db_data_source = DataSource(
            name=data.name,
            type="100qiu",  # 设置为100qiu类型
            url=data.url,
            config=json.dumps(config, ensure_ascii=False),
            field_mapping=data.field_mapping,
            update_frequency=data.update_frequency,
            status=1 if data.status != "offline" else 0,
            created_by=1  # 开发环境临时设置为固定值，后续应通过认证获取
        )
        
        db.add(db_data_source)
        db.commit()
        db.refresh(db_data_source)
        
        # 转换为响应格式
        response_data = DataSource100qiuResponse(
            id=db_data_source.id,
            source_id=db_data_source.source_id or f"DS{db_data_source.id:03d}",
            name=db_data_source.name,
            type=db_data_source.type,
            url=db_data_source.url,
            status="online" if db_data_source.status == 1 else "offline",
            config=db_data_source.config_dict,
            last_update=db_data_source.last_update.isoformat() if db_data_source.last_update else None,
            error_rate=db_data_source.error_rate,
            created_at=db_data_source.created_at.isoformat(),
            updated_at=db_data_source.updated_at.isoformat(),
            created_by=db_data_source.created_by,
            last_error=db_data_source.last_error,
            last_error_time=db_data_source.last_error_time.isoformat() if db_data_source.last_error_time else None
        )
        
        return {"success": True, "data": response_data, "message": "数据源创建成功"}
    except Exception as e:
        return {"success": False, "message": f"创建数据源失败: {str(e)}", "data": None}


@router.get("/{source_id}")
async def get_100qiu_data_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """获取指定ID的100qiu数据源"""
    try:
        db_data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not db_data_source:
            raise HTTPException(status_code=404, detail="数据源不存在")
        
        response_data = DataSource100qiuResponse(
            id=db_data_source.id,
            source_id=db_data_source.source_id or f"DS{db_data_source.id:03d}",
            name=db_data_source.name,
            type=db_data_source.type,
            url=db_data_source.url,
            status="online" if db_data_source.status == 1 else "offline",
            config=db_data_source.config_dict,
            last_update=db_data_source.last_update.isoformat() if db_data_source.last_update else None,
            error_rate=db_data_source.error_rate,
            created_at=db_data_source.created_at.isoformat(),
            updated_at=db_data_source.updated_at.isoformat(),
            created_by=db_data_source.created_by,
            last_error=db_data_source.last_error,
            last_error_time=db_data_source.last_error_time.isoformat() if db_data_source.last_error_time else None
        )
        
        return {"success": True, "data": response_data, "message": "获取数据源成功"}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": f"获取数据源失败: {str(e)}", "data": None}


@router.put("/{source_id}")
async def update_100qiu_data_source(
    source_id: int,
    data: DataSource100qiuUpdate,
    db: Session = Depends(get_db)
):
    """更新100qiu数据源配置"""
    try:
        db_data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not db_data_source:
            raise HTTPException(status_code=404, detail="数据源不存在")
        
        # 更新字段
        if data.name is not None:
            db_data_source.name = data.name
        if data.url is not None:
            db_data_source.url = data.url
        if data.status is not None:
            db_data_source.status = 1 if data.status == "online" else 0
        if data.update_frequency is not None:
            db_data_source.update_frequency = data.update_frequency
        
        # 确保type保持为100qiu
        db_data_source.type = "100qiu"
        
        # 更新配置
        config = db_data_source.config_dict
        if data.date_time is not None:
            config["date_time"] = data.date_time
        if data.field_mapping is not None:
            db_data_source.field_mapping = data.field_mapping
        
        # 重新序列化配置到数据库
        db_data_source.config = json.dumps(config, ensure_ascii=False)
        from datetime import datetime as dt
        db_data_source.updated_at = dt.utcnow()
        
        db.commit()
        db.refresh(db_data_source)
        
        response_data = DataSource100qiuResponse(
            id=db_data_source.id,
            source_id=db_data_source.source_id or f"DS{db_data_source.id:03d}",
            name=db_data_source.name,
            type=db_data_source.type,
            url=db_data_source.url,
            status="online" if db_data_source.status == 1 else "offline",
            config=db_data_source.config_dict,
            last_update=db_data_source.last_update.isoformat() if db_data_source.last_update else None,
            error_rate=db_data_source.error_rate,
            created_at=db_data_source.created_at.isoformat(),
            updated_at=db_data_source.updated_at.isoformat(),
            created_by=db_data_source.created_by,
            last_error=db_data_source.last_error,
            last_error_time=db_data_source.last_error_time.isoformat() if db_data_source.last_error_time else None
        )
        
        return {"success": True, "data": response_data, "message": "更新数据源成功"}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": f"更新数据源失败: {str(e)}", "data": None}


@router.delete("/{source_id}")
async def delete_100qiu_data_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """删除100qiu数据源"""
    try:
        db_data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not db_data_source:
            raise HTTPException(status_code=404, detail="数据源不存在")
        
        db.delete(db_data_source)
        db.commit()
        
        return {"success": True, "message": "数据源删除成功", "data": {"id": source_id}}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": f"删除数据源失败: {str(e)}", "data": None}


@router.get("/")
async def list_100qiu_data_sources(
    name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取100qiu数据源列表"""
    try:
        query = db.query(DataSource).filter(DataSource.type == "100qiu")
        
        # 应用筛选条件
        if name:
            query = query.filter(DataSource.name.contains(name))
        if status:
            query = query.filter(DataSource.status == (1 if status == "online" else 0))
        
        # 计算总数
        total = query.count()
        
        # 应用分页
        data_sources = query.offset(skip).limit(limit).all()
        
        # 转换为响应格式
        items = []
        for ds in data_sources:
            items.append(DataSource100qiuResponse(
                id=ds.id,
                source_id=ds.source_id or f"DS{ds.id:03d}",
                name=ds.name,
                type=ds.type,
                url=ds.url,
                status="online" if ds.status == 1 else "offline",
                config=ds.config_dict,
                last_update=ds.last_update.isoformat() if ds.last_update else None,
                error_rate=ds.error_rate,
                created_at=ds.created_at.isoformat(),
                updated_at=ds.updated_at.isoformat(),
                created_by=ds.created_by,
                last_error=ds.last_error,
                last_error_time=ds.last_error_time.isoformat() if ds.last_error_time else None
            ))
        
        response_data = DataSource100qiuListResponse(items=items, total=total)
        
        return {"success": True, "data": response_data, "message": "获取数据源列表成功"}
    except Exception as e:
        return {"success": False, "message": f"获取数据源列表失败: {str(e)}", "data": None}


@router.post("/{source_id}/test")
async def test_100qiu_data_source_connection(
    source_id: int,
    db: Session = Depends(get_db)
):
    """测试100qiu数据源连接"""
    try:
        db_data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not db_data_source:
            raise HTTPException(status_code=404, detail="数据源不存在")
        
        # 获取配置
        config = db_data_source.config_dict
        date_time = config.get("date_time", "latest")
        
        # 修复：当date_time为'latest'时，使用默认的有效dateTime值
        if date_time == "latest":
            # 使用一个默认的有效dateTime值，可以根据实际需求调整
            date_time = "26011"
        
        # 构造API URL
        if "dateTime" in db_data_source.url:
            import re
            api_url = re.sub(r'dateTime=\w+', f'dateTime={date_time}', db_data_source.url)
        else:
            api_url = f"{db_data_source.url}?dateTime={date_time}"
        
        # 发送请求
        response = _NO_PROXY_SESSION.get(api_url, timeout=30)
        
        if response.status_code != 200:
            return TestConnectionResponse(
                success=False,
                message=f"API请求失败，状态码: {response.status_code}",
                data={"status_code": response.status_code}
            )
        
        try:
            data = response.json()
        except Exception as e:
            return TestConnectionResponse(
                success=False,
                message=f"响应不是有效JSON格式: {str(e)}",
                data=None
            )
        
        # 检查数据结构
        if not isinstance(data, (list, dict)):
            return TestConnectionResponse(
                success=False,
                message="API返回的数据格式不符合预期，应为数组或对象",
                data=None
            )
        
        # 获取样本数据
        sample_data = []
        if isinstance(data, list):
            sample_data = data[:3]  # 前3条数据作为样本
        elif isinstance(data, dict) and "data" in data:
            sample_data = data["data"][:3] if isinstance(data["data"], list) else [data["data"]]
        else:
            sample_data = [data]
        
        response_obj = TestConnectionResponse(
            success=True,
            message="连接测试成功",
            data={
                "status_code": response.status_code,
                "content_length": len(response.content),
                "has_data": len(sample_data) > 0,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            },
            sample_data=sample_data
        )
        
        return {
            "success": True,
            "message": "连接测试成功",
            "data": response_obj
        }
    
    except Exception as e:
        response_obj = TestConnectionResponse(
            success=False,
            message=f"连接测试失败: {str(e)}",
            data=None
        )
        return {
            "success": False,
            "message": f"连接测试失败: {str(e)}",
            "data": response_obj.dict()
        }


@router.post("/{source_id}/fetch")
async def fetch_100qiu_data(
    source_id: int,
    db: Session = Depends(get_db)
):
    """从100qiu API获取数据并存储到数据库"""
    # 初始化日志服务
    log_service = LogService(db)
    
    try:
        db_data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not db_data_source:
            raise HTTPException(status_code=404, detail="数据源不存在")
        
        # 记录开始日志
        start_time = dt.utcnow()
        log_service.create_log_entry(LogEntryCreate(
            timestamp=start_time,
            level="INFO",
            message=f"开始获取100qiu数据源 {source_id} 的数据",
            module="data_source_100qiu",
            user_id=None,
            extra_data=json.dumps({
                "source_id": source_id,
                "source_name": db_data_source.name,
                "url": db_data_source.url,
                "action": "fetch_start"
            }, ensure_ascii=False)
        ))
        
        # 获取配置
        config = db_data_source.config_dict
        date_time = config.get("date_time", "latest")
        
        # 修复：当date_time为'latest'时，使用默认的有效dateTime值
        if date_time == "latest":
            # 使用一个默认的有效dateTime值，可以根据实际需求调整
            date_time = "26011"
        
        # 构造API URL
        if "dateTime" in db_data_source.url:
            import re
            api_url = re.sub(r'dateTime=\w+', f'dateTime={date_time}', db_data_source.url)
        else:
            api_url = f"{db_data_source.url}?dateTime={date_time}"
        
        # 发送请求
        response = _NO_PROXY_SESSION.get(api_url, timeout=30)
        
        if response.status_code != 200:
            error_msg = f"API请求失败，状态码: {response.status_code}"
            print(f"[ERROR] {error_msg}")
            # 更新数据源错误信息
            db_data_source.last_error = error_msg
            db_data_source.last_error_time = datetime.utcnow()
            db.commit()
            
            # 记录错误日志
            log_service.create_log_entry(LogEntryCreate(
                timestamp=dt.utcnow(),
                level="ERROR",
                message=f"100qiu数据源 {source_id} 获取失败: {error_msg}",
                module="data_source_100qiu",
                user_id=None,
                extra_data=json.dumps({
                    "source_id": source_id,
                    "status_code": response.status_code,
                    "url": api_url,
                    "action": "fetch_failed",
                    "error_type": "http_error"
                }, ensure_ascii=False)
            ))
            
            return FetchDataResponse(
                success=False,
                message=error_msg,
                total_fetched=0
            )
        
        try:
            data = response.json()
        except Exception as e:
            error_msg = f"响应不是有效JSON格式: {str(e)}"
            print(f"[ERROR] {error_msg}")
            # 更新数据源错误信息
            db_data_source.last_error = error_msg
            db_data_source.last_error_time = datetime.utcnow()
            db.commit()
            
            # 记录错误日志
            log_service.create_log_entry(LogEntryCreate(
                timestamp=dt.utcnow(),
                level="ERROR",
                message=f"100qiu数据源 {source_id} JSON解析失败: {error_msg}",
                module="data_source_100qiu",
                user_id=None,
                extra_data=json.dumps({
                    "source_id": source_id,
                    "url": api_url,
                    "action": "fetch_failed",
                    "error_type": "json_parse_error",
                    "response_preview": str(response.content)[:500] if response.content else ""
                }, ensure_ascii=False)
            ))
            
            return FetchDataResponse(
                success=False,
                message=error_msg,
                total_fetched=0
            )
        
        # 解析数据并存储到数据库
        from ...models.matches import FootballMatch
        from ...database import engine
        from sqlalchemy.orm import Session as SqlSession
        
        # 添加调试信息
        print(f"[DEBUG] API响应数据类型: {type(data)}")
        print(f"[DEBUG] API响应数据内容预览: {str(data)[:1000]}...")  # 增加预览长度
        
        # 确保数据格式正确
        matches_data = []
        if isinstance(data, list):
            matches_data = data
            print(f"[INFO] 数据是列表格式，包含 {len(matches_data)} 个项目")
        elif isinstance(data, dict):
            if "data" in data:
                matches_data = data["data"] if isinstance(data["data"], list) else []
                print(f"[INFO] 数据是字典格式，包含 'data' 键，解析出 {len(matches_data)} 个项目")
            elif "rows" in data:
                matches_data = data["rows"] if isinstance(data["rows"], list) else []
                print(f"[INFO] 数据是字典格式，包含 'rows' 键，解析出 {len(matches_data)} 个项目")
            elif "results" in data:
                matches_data = data["results"] if isinstance(data["results"], list) else []
                print(f"[INFO] 数据是字典格式，包含 'results' 键，解析出 {len(matches_data)} 个项目")
            elif "items" in data:
                matches_data = data["items"] if isinstance(data["items"], list) else []
                print(f"[INFO] 数据是字典格式，包含 'items' 键，解析出 {len(matches_data)} 个项目")
            elif "matches" in data:
                matches_data = data["matches"] if isinstance(data["matches"], list) else []
                print(f"[INFO] 数据是字典格式，包含 'matches' 键，解析出 {len(matches_data)} 个项目")
            else:
                # 检查字典中是否包含比赛相关字段，如果是，则作为单个项目处理
                match_keys = ['homeTeam', 'awayTeam', 'home_team', 'away_team', 'league', 'matchTime', 'startTime', 'status']
                if any(key in data for key in match_keys):
                    matches_data = [data]
                    print(f"[INFO] 数据是字典格式，包含比赛相关字段，作为单个项目处理")
                else:
                    matches_data = []
                    print(f"[WARNING] 数据是字典格式，但不包含已知数据键或比赛字段，无法解析")
                    # 记录详细错误信息
                    available_keys = list(data.keys()) if hasattr(data, 'keys') else []
                    warning_msg = f"数据格式不符合预期，可用键: {available_keys[:10]}"
                    print(f"[DEBUG] {warning_msg}")
        else:
            matches_data = []
            error_msg = f"数据格式未知，无法解析: {type(data)}"
            print(f"[ERROR] {error_msg}")
            # 更新数据源错误信息
            db_data_source.last_error = error_msg
            db_data_source.last_error_time = datetime.utcnow()
            db.commit()
            
            # 记录错误日志
            log_service.create_log_entry(LogEntryCreate(
                level="ERROR",
                message=f"100qiu数据源 {source_id} 数据格式解析失败: {error_msg}",
                module="data_source_100qiu",
                user_id=None,
                extra_data=json.dumps({
                    "source_id": source_id,
                    "data_type": str(type(data)),
                    "action": "fetch_failed",
                    "error_type": "data_format_error"
                }, ensure_ascii=False)
            ))
            
            return FetchDataResponse(
                success=False,
                message=error_msg,
                total_fetched=0
            )
        
        print(f"[INFO] 最终解析的比赛数据数量: {len(matches_data)}")
        
        # 如果没有解析到任何比赛数据，返回成功但数量为0
        if len(matches_data) == 0:
            success_msg = f"获取成功，获取数量：0；数据库未新增数据条数。API返回了 {len(matches_data)} 条原始数据，但未能解析出有效的比赛数据。"
            print(f"[INFO] {success_msg}")
            # 清除之前的错误信息（因为这不是错误）
            db_data_source.last_error = None
            db_data_source.last_error_time = None
            db.commit()
            
            end_time = dt.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # 记录详细日志
            log_service.create_log_entry(LogEntryCreate(
                timestamp=end_time,
                level="INFO",
                message=f"100qiu数据源 {source_id} 获取完成: {success_msg}",
                module="data_source_100qiu",
                user_id=None,
                extra_data=json.dumps({
                    "source_id": source_id,
                    "total_fetched": 0,
                    "raw_data_count": len(matches_data),
                    "action": "fetch_success_zero",
                    "available_keys": list(data.keys()) if isinstance(data, dict) else [],
                    "duration_seconds": duration
                }, ensure_ascii=False)
            ))
            
            response_obj = FetchDataResponse(
                success=True,
                message=success_msg,
                total_fetched=0,
                sample_data=[]
            )
            return response_obj
        
        # 存储到数据库
        session = SqlSession(bind=engine)
        count = 0
        processed_count = 0
        failed_parsing_count = 0
        duplicate_count = 0
        try:
            for i, item in enumerate(matches_data):
                print(f"[DEBUG] 正在处理第 {i+1}/{len(matches_data)} 个项目: {str(item)[:500]}...")
                processed_count += 1
                
                # 解析比赛数据
                match_data = parse_match_from_100qiu(item, date_time)
                if match_data:
                    print(f"[INFO] 成功解析比赛数据: {match_data.get('match_id', 'N/A')}")
                    
                    # 检查是否已存在
                    existing_match = session.query(FootballMatch).filter(
                        FootballMatch.match_id == match_data["match_id"]
                    ).first()
                    
                    if not existing_match:
                        # 创建新的比赛记录 - 使用FootballMatch模型的字段
                        new_match = FootballMatch(**match_data)
                        session.add(new_match)
                        count += 1
                        print(f"[INFO] 新增比赛记录: {match_data.get('match_id', 'N/A')}")
                    else:
                        duplicate_count += 1
                        print(f"[INFO] 比赛记录已存在，跳过: {match_data.get('match_id', 'N/A')}")
                else:
                    failed_parsing_count += 1
                    print(f"[WARNING] 解析比赛数据失败，跳过第 {i+1} 个项目")
            
            session.commit()
            
            end_time = dt.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            if count == 0:
                success_msg = f"获取成功，获取数量：0；数据库未新增数据条数。共处理 {processed_count} 条原始数据，其中 {duplicate_count} 条已存在，{failed_parsing_count} 条解析失败。"
                print(f"[INFO] {success_msg}")
                # 清除之前的错误信息
                db_data_source.last_error = None
                db_data_source.last_error_time = None
                db.commit()
                
                # 记录详细日志
                log_service.create_log_entry(LogEntryCreate(
                    timestamp=dt.utcnow(),
                    level="INFO",
                    message=f"100qiu数据源 {source_id} 获取完成: {success_msg}",
                    module="data_source_100qiu",
                    user_id=None,
                    extra_data=json.dumps({
                        "source_id": source_id,
                        "total_fetched": 0,
                        "processed_count": processed_count,
                        "duplicate_count": duplicate_count,
                        "failed_parsing_count": failed_parsing_count,
                        "duration_seconds": duration,
                        "action": "fetch_success_zero_detailed"
                    }, ensure_ascii=False)
                ))
                
                response_obj = FetchDataResponse(
                    success=True,
                    message=success_msg,
                    total_fetched=count,
                    sample_data=matches_data[:3] if matches_data else []
                )
            else:
                success_msg = f"成功获取并存储了 {count} 条比赛数据 (共处理 {processed_count} 条原始数据，{duplicate_count} 条已存在，{failed_parsing_count} 条解析失败)"
                print(f"[INFO] {success_msg}")
                # 清除之前的错误信息
                db_data_source.last_error = None
                db_data_source.last_error_time = None
                db.commit()
                
                # 记录成功日志
                log_service.create_log_entry(LogEntryCreate(
                    timestamp=dt.utcnow(),
                    level="INFO",
                    message=f"100qiu数据源 {source_id} 获取成功: {success_msg}",
                    module="data_source_100qiu",
                    user_id=None,
                    extra_data=json.dumps({
                        "source_id": source_id,
                        "total_fetched": count,
                        "processed_count": processed_count,
                        "duplicate_count": duplicate_count,
                        "failed_parsing_count": failed_parsing_count,
                        "duration_seconds": duration,
                        "action": "fetch_success"
                    }, ensure_ascii=False)
                ))
                
                response_obj = FetchDataResponse(
                    success=True,
                    message=success_msg,
                    total_fetched=count,
                    sample_data=matches_data[:3] if matches_data else []
                )
            
            return response_obj
        except Exception as e:
            session.rollback()
            error_msg = f"数据存储失败: {str(e)}"
            print(f"[ERROR] {error_msg}")
            # 更新数据源错误信息
            db_data_source.last_error = error_msg
            db_data_source.last_error_time = datetime.utcnow()
            db.commit()
            
            # 记录错误日志
            log_service.create_log_entry(LogEntryCreate(
                timestamp=dt.utcnow(),
                level="ERROR",
                message=f"100qiu数据源 {source_id} 数据存储失败: {error_msg}",
                module="data_source_100qiu",
                user_id=None,
                extra_data=json.dumps({
                    "source_id": source_id,
                    "action": "fetch_failed",
                    "error_type": "database_error",
                    "processed_count": processed_count
                }, ensure_ascii=False)
            ))
            
            return {
                "success": False,
                "message": error_msg,
                "data": FetchDataResponse(
                    success=False,
                    message=error_msg,
                    total_fetched=0
                ).dict()
            }
        finally:
            session.close()
    
    except Exception as e:
        error_msg = f"获取数据失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        # 更新数据源错误信息
        if 'db_data_source' in locals():
            db_data_source.last_error = error_msg
            db_data_source.last_error_time = datetime.utcnow()
            db.commit()
        
        # 记录错误日志
        log_service.create_log_entry(LogEntryCreate(
            timestamp=dt.utcnow(),
            level="ERROR",
            message=f"100qiu数据源 {source_id} 获取异常: {error_msg}",
            module="data_source_100qiu",
            user_id=None,
            extra_data=json.dumps({
                "source_id": source_id,
                "action": "fetch_exception",
                "error_type": "unexpected_error"
            }, ensure_ascii=False)
        ))
        
        return {
            "success": False,
            "message": error_msg,
            "data": FetchDataResponse(
                success=False,
                message=error_msg,
                total_fetched=0
            ).dict()
        }


def parse_match_from_100qiu(item: Dict[str, Any], date_time: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    从100qiu API响应中解析比赛数据
    这里根据实际API响应结构进行解析
    """
    try:
        # 提取基本字段
        line_id = str(item.get('lineId', ''))
        home_team = item.get('homeTeam', '未知主队')
        away_team = item.get('guestTeam', '未知客队')  # 注意：100qiu使用guestTeam而不是awayTeam
        league = item.get('gameShortName', '未知联赛')
        
        # 处理比赛时间
        match_time_str = item.get('matchTimeStr', None)
        match_time = None
        if match_time_str:
            if isinstance(match_time_str, str):
                try:
                    # 100qiu返回的是"YYYY-MM-DD"格式
                    from datetime import datetime
                    match_time = datetime.strptime(match_time_str, "%Y-%m-%d")
                except ValueError:
                    # 如果解析失败，使用当前时间
                    match_time = datetime.now()
        else:
            match_time = datetime.now()
        
        # 获取比分信息
        home_score = None
        away_score = None
        
        # 状态默认为pending（未开始）
        status = 'pending'
        
        # 提取基本字段
        line_id_str = str(item.get('lineId', '')).strip()
        
        # 转换期号和序号为整数
        try:
            date_time = int(date_time) if date_time else 0
            line_id_int = int(line_id_str) if line_id_str else 0
        except ValueError:
            date_time = 0
            line_id_int = 0
        
        # 生成新的match_id格式：date_time_line_id（如：26024_001）
        if date_time > 0 and line_id_int > 0:
            match_id = f"{date_time}_{line_id_int:03d}"
        elif match_id := line_id_str:
            # 兼容旧格式
            match_id = f"100qiu_{match_id}"
        else:
            # 如果没有有效数据，使用时间戳生成临时ID
            match_id = f"{int(time.time() * 1000)}"
        
        # 将date_time和line_id添加到source_attributes中
        source_attributes = item.copy()
        if date_time:
            source_attributes['date_time'] = date_time
        if line_id_str:
            source_attributes['line_id'] = line_id_int
        
        # 返回符合FootballMatch模型的字段
        match_data = {
            "match_id": match_id,
            "home_team": home_team,
            "away_team": away_team,
            "match_time": match_time,
            "league": league,
            "status": status,
            "home_score": home_score,
            "away_score": away_score,
            "data_source": "100qiu",
            "source_attributes": source_attributes
        }
        
        return match_data
    except Exception as e:
        print(f"解析比赛数据失败: {e}")
        return None
