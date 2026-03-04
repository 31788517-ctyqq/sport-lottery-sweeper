"""
任务调度服务
处理爬虫任务的创建、调度和执行管理
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import uuid

from ..config import settings
from ..models.crawler_config import CrawlerConfig
from ..models.crawler_tasks import CrawlerTask
from ..models.crawler_logs import CrawlerTaskLog
from ..models.headers import RequestHeader
from ..models.data_source_headers import DataSourceHeader
from ..models.crawler_task_headers import CrawlerTaskHeader
from ..models.admin_user import AdminUser
from ..models.ip_pool import IPPool
from ..schemas.crawler import (
    CrawlerTaskCreate, CrawlerTaskUpdate, CrawlerTaskResponse
)
from .crawler_service import BaseCrawlerService


class TaskSchedulerService(BaseCrawlerService):
    """任务调度服务类"""
    
    # 用于存储运行中任务的线程信息
    _running_tasks = {}
    _domain_fail_state: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _resolve_domain(url: str) -> str:
        try:
            return (urlparse(url).hostname or "").strip().lower()
        except Exception:
            return ""

    def _is_domain_circuit_open(self, domain: str) -> bool:
        if not domain:
            return False
        state = self._domain_fail_state.get(domain) or {}
        open_until = state.get("open_until")
        if not open_until:
            return False
        if datetime.utcnow() >= open_until:
            state["open_until"] = None
            state["fail_count"] = 0
            self._domain_fail_state[domain] = state
            return False
        return True

    def _record_domain_result(self, domain: str, *, success: bool, status_code: Optional[int] = None) -> None:
        if not domain:
            return
        now = datetime.utcnow()
        state = self._domain_fail_state.setdefault(domain, {"fail_count": 0, "open_until": None, "last_status": None})
        state["last_status"] = status_code
        if success:
            state["fail_count"] = 0
            state["open_until"] = None
            return

        state["fail_count"] = int(state.get("fail_count", 0)) + 1
        threshold = max(1, int(settings.REQUEST_DOMAIN_FAILURE_THRESHOLD))
        if state["fail_count"] >= threshold:
            cooldown = max(30, int(settings.REQUEST_DOMAIN_COOLDOWN_SECONDS))
            state["open_until"] = now + timedelta(seconds=cooldown)

    def get_tasks(self, status: Optional[str] = None, source_id: Optional[int] = None,
                  page: int = 1, page_size: int = 20) -> List[CrawlerTaskResponse]:
        """
        获取任务列表
        
        Args:
            status: 状态筛选
            source_id: 数据源ID筛选
            page: 页码
            page_size: 每页数量
            
        Returns:
            List[CrawlerTaskResponse]: 任务列表
        """
        query = self.db.query(CrawlerTask)
        
        # 状态筛选
        if status:
            query = query.filter(CrawlerTask.status == status)
        
        # 数据源筛选
        if source_id:
            query = query.filter(CrawlerTask.source_id == source_id)
        
        # 分页
        offset = (page - 1) * page_size
        tasks = query.order_by(desc(CrawlerTask.updated_at)).offset(offset).limit(page_size).all()
        
        # 转换为响应模型（已经是真实数据，无需模拟）
        result = []
        for task in tasks:
            # 获取关联的数据源信息
            source = self.db.query(CrawlerConfig).filter(
                CrawlerConfig.id == task.source_id
            ).first()
            
            # 如果有最后运行时间，计算下次运行时间
            next_run_time = None
            if task.last_run_time and task.cron_expression and task.is_active:
                # 这里简化处理：基于cron表达式和最后运行时间计算
                # 实际应用中应使用cron解析库如croniter
                next_run_time = task.last_run_time + timedelta(hours=1)
            
            response = CrawlerTaskResponse(
                id=task.id,
                name=task.name,
                source_id=task.source_id,
                task_type=task.task_type,
                cron_expression=task.cron_expression,
                is_active=task.is_active,
                status=task.status,
                last_run_time=task.last_run_time,
                next_run_time=next_run_time,
                run_count=task.run_count,
                success_count=task.success_count,
                error_count=task.error_count,
                config=task.config or {"timeout": 30, "retry": 3},
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            
            # 状态二次筛选（确保状态筛选生效）
            if status and response.status != status:
                continue
                
            result.append(response)
        
        return result
    
    def create_task(self, task_data: CrawlerTaskCreate, created_by: int) -> CrawlerTaskResponse:
        """
        创建爬虫任务
        
        Args:
            task_data: 任务创建数据
            created_by: 创建者ID
            
        Returns:
            CrawlerTaskResponse: 创建的任务
        """
        # 检查数据源是否存在
        source = self.db.query(CrawlerConfig).filter(
            CrawlerConfig.id == task_data.source_id
        ).first()
        
        if not source:
            raise ValueError("数据源不存在")
        
        # 验证Cron表达式（简单验证）
        if not self._validate_cron_expression(task_data.cron_expression):
            raise ValueError("无效的Cron表达式")
        
        # 模拟创建任务
        import hashlib
        task_id = int(hashlib.md5(
            f"{task_data.source_id}{task_data.task_type}{self._get_current_timestamp()}".encode()
        ).hexdigest()[:8], 16) % 100000
        
        now = datetime.utcnow()
        
        return CrawlerTaskResponse(
            id=task_id,
            name=task_data.name,
            source_id=task_data.source_id,
            task_type=task_data.task_type,
            cron_expression=task_data.cron_expression,
            is_active=task_data.is_active,
            status="stopped" if not task_data.is_active else "running",
            last_run_time=None,
            next_run_time=now + timedelta(minutes=1) if task_data.is_active else None,
            run_count=0,
            success_count=0,
            error_count=0,
            config=task_data.config or {},
            created_at=now,
            updated_at=now
        )
    
    def update_task_status(self, task_id: int, new_status: str, updated_by: int) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            new_status: 新状态
            updated_by: 更新者ID
            
        Returns:
            bool: 是否更新成功
        """
        # 模拟更新任务状态
        # 在实际应用中，这里应该更新Task表
        valid_statuses = ["running", "stopped", "error", "completed"]
        if new_status not in valid_statuses:
            return False
        
        # 这里应该更新数据库中的任务状态
        # 现在只是模拟返回成功
        return True
    
    def trigger_task(self, task_id: int, triggered_by: int) -> Dict[str, Any]:
        """
        手动触发任务执行
        
        Args:
            task_id: 任务ID
            triggered_by: 触发者ID
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        from sqlalchemy import and_
        from ..models.crawler_tasks import CrawlerTask
        from ..models.crawler_logs import CrawlerTaskLog
        from datetime import datetime
        import threading
        
        # 查找任务
        task = self.db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
        if not task:
            return {
                "success": False,
                "message": "任务不存在",
                "task_id": task_id
            }
                # 查找关联的爬虫配置
        from ..models.crawler_config import CrawlerConfig
        source = self.db.query(CrawlerConfig).filter(CrawlerConfig.id == task.source_id).first()
        if not source:
            return {
                "success": False,
                "message": "任务关联的爬虫配置不存在",
                "task_id": task_id
            }
        
        # 更新任务状态为运行中
        task.status = "RUNNING"
        task.last_run_time = datetime.utcnow()
        task.run_count = task.run_count + 1
        self.db.commit()  # 确保提交事务
        
        # 记录任务开始执行的日志
        log_entry = CrawlerTaskLog(
            task_id=task.id,
            source_id=task.source_id,  # 修复：使用任务的source_id
            status="RUNNING",
            started_at=datetime.utcnow(),
            records_processed=0,
            records_success=0,
            records_failed=0,
            error_message=None
        )
        self.db.add(log_entry)
        self.db.commit()
        
        # 为了不阻塞API响应，启动一个新线程来执行实际的爬虫任务
        def execute_task():
            # 在新线程中创建新的数据库会话
            from backend.database import get_db
            db = next(get_db())
            try:
                # 查询任务和数据源，使用新的数据库会话
                task_in_thread = db.query(CrawlerTask).filter(CrawlerTask.id == task.id).first()
                source = db.query(CrawlerConfig).filter(CrawlerConfig.id == task.source_id).first()
                
                if not task_in_thread:
                    print(f"任务 {task.id} 不存在")
                    return
                if not source:
                    print(f"任务关联的爬虫配置不存在，source_id: {task.source_id}")
                    return
                
                # 执行爬虫任务，使用实际的爬虫逻辑而不是模拟的
                result = self._execute_real_task_logic(task_in_thread, source)
                
                # 更新任务状态和日志
                task_in_thread = db.query(CrawlerTask).filter(CrawlerTask.id == task.id).first()
                if task_in_thread:
                    task_in_thread.status = result.get("status", "SUCCESS")
                    task_in_thread.success_count = task_in_thread.success_count + result.get("items_success", 0)
                    task_in_thread.error_count = task_in_thread.error_count + result.get("items_failed", 0)
                    
                    # 更新日志记录
                    log_in_thread = db.query(CrawlerTaskLog).filter(CrawlerTaskLog.id == log_entry.id).first()
                    if log_in_thread:
                        log_in_thread.status = result.get("status", "SUCCESS")
                        log_in_thread.records_processed = result.get("items_processed", 0)
                        log_in_thread.records_success = result.get("items_success", 0)
                        log_in_thread.records_failed = result.get("items_failed", 0)
                        log_in_thread.completed_at = datetime.utcnow()
                    
                    db.commit()
                
            except Exception as e:
                print(f"执行任务时发生错误: {e}")
                import traceback
                traceback.print_exc()
                # 记录错误
                task_in_thread = db.query(CrawlerTask).filter(CrawlerTask.id == task.id).first()
                if task_in_thread:
                    task_in_thread.status = "FAILED"
                    task_in_thread.error_count = task_in_thread.error_count + 1
                    
                    log_in_thread = db.query(CrawlerTaskLog).filter(CrawlerTaskLog.id == log_entry.id).first()
                    if log_in_thread:
                        log_in_thread.status = "FAILED"
                        log_in_thread.error_message = str(e)
                        log_in_thread.completed_at = datetime.utcnow()
                    
                    db.commit()
            finally:
                db.close()

        # 启动线程执行任务
        thread = threading.Thread(target=execute_task)
        thread.daemon = True  # 设置为守护线程，这样主线程退出时会自动清理
        thread.start()
        
        # 记录线程信息以便后续停止任务
        self._running_tasks[task_id] = thread

        return {
            "success": True,
            "message": "任务已触发执行",
            "task_id": task_id
        }
    
    def _execute_real_task_logic(self, task: CrawlerTask, source: 'CrawlerConfig') -> Dict[str, Any]:
        """
        执行任务的真实逻辑，实际调用数据源进行数据抓取
        
        Args:
            task: 任务对象
            source: 数据源对象
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        import requests
        import time
        import json
        from datetime import datetime
        from backend.models.matches import FootballMatch
        used_header_ids: List[int] = []
        proxy: Optional[IPPool] = None
        request_meta: Dict[str, Any] = {
            "proxy_used": None,
            "proxy_id": None,
            "header_ids": [],
            "fallback_reason": None,
            "used_direct": True,
        }

        try:
            # 使用数据源配置进行请求
            url = source.url
            domain = self._resolve_domain(url)
            # 从config_data解析配置
            import ast
            try:
                # 尝试解析JSON格式的配置
                config_dict = json.loads(source.config_data) if source.config_data else {}
            except json.JSONDecodeError:
                try:
                    # 如果不是JSON格式，尝试用ast.literal_eval解析
                    config_dict = ast.literal_eval(source.config_data) if source.config_data else {}
                except:
                    # 如果都不是，使用默认配置
                    config_dict = {"headers": {}, "timeout": 30}
            
            headers = config_dict.get("headers", {})
            bound_headers, used_header_ids = self._get_bound_headers(
                task_id=task.id,
                data_source_id=task.source_id,
            )
            if bound_headers:
                headers.update(bound_headers)
            timeout = config_dict.get("timeout", 30)
            
            print(f"正在请求数据源: {url}")
            print(f"数据源配置: {config_dict}")
            
            # 添加默认请求头
            if not headers.get("User-Agent"):
                headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

            if self._is_domain_circuit_open(domain):
                return {
                    "status": "FAILED",
                    "items_processed": 0,
                    "items_success": 0,
                    "items_failed": 0,
                    "success": False,
                    "message": f"域名熔断中: {domain}",
                    "request_meta": {
                        **request_meta,
                        "domain": domain,
                        "fallback_reason": "domain_circuit_open",
                    },
                }

            proxy = self._choose_proxy_for_request()
            request_meta = {
                "proxy_used": f"{proxy.protocol}://{proxy.ip}:{proxy.port}" if proxy else None,
                "proxy_id": int(proxy.id) if proxy else None,
                "header_ids": list(used_header_ids),
                "fallback_reason": None,
                "used_direct": proxy is None,
                "domain": domain,
            }

            request_kwargs: Dict[str, Any] = {"headers": headers, "timeout": timeout}
            if proxy and settings.REQUEST_USE_PROXY_BY_DEFAULT:
                proxy_url = f"{proxy.protocol}://{proxy.ip}:{proxy.port}"
                request_kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
            elif not settings.REQUEST_ALLOW_DIRECT_FALLBACK and settings.REQUEST_USE_PROXY_BY_DEFAULT:
                return {
                    "status": "FAILED",
                    "items_processed": 0,
                    "items_success": 0,
                    "items_failed": 0,
                    "success": False,
                    "message": "无可用代理且不允许直连回退",
                    "request_meta": {
                        **request_meta,
                        "fallback_reason": "proxy_pool_unavailable",
                    },
                }

            try:
                response = requests.get(url, **request_kwargs)
            except requests.exceptions.RequestException as req_exc:
                # Proxy-first fallback to direct request once.
                if request_kwargs.get("proxies") and settings.REQUEST_ALLOW_DIRECT_FALLBACK:
                    request_meta["fallback_reason"] = "proxy_request_failed_direct_fallback"
                    request_meta["used_direct"] = True
                    request_meta["proxy_used"] = None
                    request_kwargs.pop("proxies", None)
                    response = requests.get(url, **request_kwargs)
                else:
                    raise req_exc

            print(f"请求完成，状态码: {response.status_code}")
            self._record_domain_result(domain, success=response.status_code == 200, status_code=response.status_code)
            self._record_header_usage(used_header_ids, response.status_code == 200)
            self._record_proxy_usage(proxy, response.status_code == 200)
            
            if response.status_code == 200:
                # 解析响应数据
                try:
                    data = response.json()
                    print(f"响应数据长度: {len(str(data))}")
                    
                    # 统计数据量
                    items_data = []
                    if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                        items_data = data['data']
                        items_count = len(items_data)
                        print(f"找到 {items_count} 条数据记录")
                    elif isinstance(data, list):
                        items_data = data
                        items_count = len(items_data)
                        print(f"找到 {items_count} 条数据记录")
                    else:
                        # 尝试其他可能的字段名
                        items_data = []
                        for key in ['matches', 'results', 'items', 'list']:
                            if key in data and isinstance(data[key], list):
                                items_data = data[key]
                                items_count = len(items_data)
                                print(f"找到 {items_count} 条数据记录 (通过 '{key}' 字段)")
                                break
                        if not items_data:
                            print(f"未找到可统计的数据列表，响应结构: {list(data.keys()) if isinstance(data, dict) else '非字典类型'}")
                    
                    # 如果数据源是100qiu，手动处理数据
                    if '100qiu' in source.url:
                        # 逐条处理数据并保存到数据库
                        success_count = 0
                        current_timestamp = int(time.time() * 1000000)  # 微秒级时间戳，确保唯一性
                        for idx, item in enumerate(items_data):
                            # 手动处理100qiu数据格式
                            processed_item = self._process_hundred_qiu_data(item)
                            if processed_item:
                                # 使用微秒级时间戳和索引确保唯一性
                                unique_match_id = f"100qiu_{processed_item['match_id']}_{current_timestamp}_{idx}"
                                
                                # 检查是否已存在该比赛
                                existing_match = self.db.query(FootballMatch).filter(
                                    FootballMatch.match_id == unique_match_id
                                ).first()
                                
                                if existing_match:
                                    # 如果存在，则更新
                                    existing_match.league = processed_item['league'] or ''
                                    existing_match.home_team = processed_item['home_team'] or ''
                                    existing_match.away_team = processed_item['away_team'] or ''
                                    # 确保 match_time 不为 None
                                    existing_match.match_time = processed_item['match_time'] or datetime.now()
                                    existing_match.status = processed_item['status'] or 'pending'
                                    existing_match.updated_at = datetime.now()
                                else:
                                    # 如果不存在，则创建
                                    new_match = FootballMatch(
                                        match_id=unique_match_id,
                                        league=processed_item['league'] or '',
                                        home_team=processed_item['home_team'] or '',
                                        away_team=processed_item['away_team'] or '',
                                        # 确保 match_time 不为 None
                                        match_time=processed_item['match_time'] or datetime.now(),
                                        status=processed_item['status'] or 'pending',
                                        created_at=datetime.now(),
                                        updated_at=datetime.now()
                                    )
                                    self.db.add(new_match)
                                
                                success_count += 1
                        
                        self.db.commit()
                        print(f"成功保存 {success_count} 条比赛数据到数据库")
                        
                        # 返回成功结果
                        return {
                            "status": "SUCCESS",
                            "items_processed": items_count,
                            "items_success": success_count,
                            "items_failed": items_count - success_count,
                            "success": True,
                            "message": f"成功处理了 {items_count} 条数据记录，其中 {success_count} 条成功保存到数据库",
                            "request_meta": request_meta,
                        }
                    else:
                        # 对于其他数据源，暂时只统计而不保存
                        print(f"数据源 {source.name} 不支持自动保存到数据库")
                        # 返回成功结果
                        return {
                            "status": "SUCCESS",
                            "items_processed": items_count,
                            "items_success": items_count,
                            "items_failed": 0,
                            "success": True,
                            "message": f"成功处理了 {items_count} 条数据记录",
                            "request_meta": request_meta,
                        }
                except ValueError as ve:
                    print(f"响应不是JSON格式: {ve}")
                    # 如果不是JSON格式，则返回固定值
                    content_length = len(response.text)
                    print(f"响应内容长度: {content_length}")
                    return {
                        "status": "SUCCESS",
                        "items_processed": min(content_length, 1),  # 避免过大的数值
                        "items_success": min(content_length, 1),
                        "items_failed": 0,
                        "success": True,
                        "message": "成功处理了数据，但格式不是JSON",
                        "request_meta": request_meta,
                    }
            else:
                # 请求失败
                print(f"HTTP请求失败，状态码: {response.status_code}")
                return {
                    "status": "FAILED",
                    "items_processed": 0,
                    "items_success": 0,
                    "items_failed": 0,
                    "success": False,
                    "message": f"HTTP请求失败，状态码: {response.status_code}",
                    "request_meta": request_meta,
                }
                
        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            try:
                self._record_domain_result(self._resolve_domain(source.url), success=False, status_code=None)
                self._record_header_usage(used_header_ids, False)
                self._record_proxy_usage(proxy, False)
            except Exception:
                pass
            return {
                "status": "FAILED",
                "items_processed": 0,
                "items_success": 0,
                "items_failed": 0,
                "success": False,
                "message": "请求超时",
                "request_meta": {**request_meta, "fallback_reason": request_meta.get("fallback_reason") or "request_timeout"},
            }
        except requests.exceptions.RequestException as re:
            print(f"请求异常: {re}")
            try:
                self._record_domain_result(self._resolve_domain(source.url), success=False, status_code=None)
                self._record_header_usage(used_header_ids, False)
                self._record_proxy_usage(proxy, False)
            except Exception:
                pass
            return {
                "status": "FAILED",
                "items_processed": 0,
                "items_success": 0,
                "items_failed": 0,
                "success": False,
                "message": f"请求异常: {str(re)}",
                "request_meta": {**request_meta, "fallback_reason": request_meta.get("fallback_reason") or "request_exception"},
            }
        except Exception as e:
            print(f"执行异常: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "FAILED",
                "items_processed": 0,
                "items_success": 0,
                "items_failed": 0,
                "success": False,
                "message": f"执行异常: {str(e)}",
                "request_meta": {**request_meta, "fallback_reason": request_meta.get("fallback_reason") or "unexpected_exception"},
            }

    def _process_hundred_qiu_data(self, item):
        """
        处理100qiu数据格式
        """
        try:
            from datetime import datetime
            
            # 提取基本字段
            match_id = str(item.get('id', item.get('matchId', item.get('_id', 'unknown'))))
            league = item.get('league', item.get('competition', ''))
            home_team = item.get('homeTeam', item.get('home', ''))
            away_team = item.get('awayTeam', item.get('away', ''))
            match_time_str = item.get('matchTime', item.get('time', ''))
            status = item.get('status', item.get('matchStatus', ''))
            
            # 关键修复：提取date_time字段（期号）
            # 从match_id中解析期号，格式如 "26022_001" -> 26022
            date_time = None
            if match_id and '_' in match_id:
                try:
                    date_time = int(match_id.split('_')[0])  # 提取期号部分
                except (ValueError, IndexError):
                    pass
            
            # 如果无法从match_id解析，尝试从其他字段获取
            if date_time is None:
                # 尝试从source_attributes中提取date_time
                source_attrs = item.get('source_attributes', {})
                if isinstance(source_attrs, dict):
                    date_time_str = source_attrs.get('date_time') or source_attrs.get('dateTime')
                    if date_time_str:
                        try:
                            date_time = int(date_time_str)
                        except (ValueError, TypeError):
                            pass
            
            # 如果仍然无法获取，使用默认值（当前年份的后两位+当前天数）
            if date_time is None:
                now = datetime.now()
                date_time = int(now.strftime('%y%j'))  # 年(后两位)+年内天数
                print(f"⚠️  无法解析date_time，使用默认值: {date_time}")
            
            # 解析比赛时间
            match_time = None
            if match_time_str:
                # 尝试多种日期格式
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M']:
                    try:
                        match_time = datetime.strptime(match_time_str, fmt)
                        break
                    except ValueError:
                        continue
                # 如果以上格式都不匹配，尝试作为时间戳
                if match_time is None:
                    try:
                        match_time = datetime.fromtimestamp(int(match_time_str))
                    except:
                        match_time = None
            
            # 构建处理后的数据 - 包含FootballMatch模型中的所有必需字段
            processed_data = {
                'match_id': match_id,
                'date_time': date_time,  # 关键修复：添加date_time字段
                'league': league,
                'home_team': home_team,
                'away_team': away_team,
                'match_time': match_time or datetime.now(),  # 确保不为None
                'status': status or 'pending'
            }
            
            return processed_data
        except Exception as e:
            print(f"处理100qiu数据时出错: {e}")
            import traceback
            traceback.print_exc()
            # 返回最小化的数据结构
            return {
                'match_id': 'unknown_' + str(int(datetime.now().timestamp())),
                'league': '',
                'home_team': '',
                'away_team': '',
                'match_time': datetime.now(),
                'status': 'pending'
            }
    
    def _get_bound_headers(self, task_id: int, data_source_id: int) -> (Dict[str, str], List[int]):
        header_map: Dict[str, Dict[str, Any]] = {}
        used_ids = set()
        reuse_seconds = max(0, int(settings.REQUEST_PROXY_REUSE_MIN_SECONDS))
        recent_before = datetime.utcnow() - timedelta(seconds=reuse_seconds) if reuse_seconds > 0 else None

        data_source_bindings = (
            self.db.query(DataSourceHeader, RequestHeader)
            .join(RequestHeader, DataSourceHeader.header_id == RequestHeader.id)
            .filter(DataSourceHeader.data_source_id == data_source_id)
            .filter(DataSourceHeader.enabled.is_(True))
            .all()
        )

        for binding, header in data_source_bindings:
            if header.status != "enabled":
                continue
            priority = binding.priority_override if binding.priority_override is not None else header.priority
            if recent_before and header.last_used and header.last_used >= recent_before:
                priority = int(priority or 0) - 10
            existing = header_map.get(header.name)
            if not existing or priority >= existing["priority"]:
                header_map[header.name] = {"value": header.value, "priority": priority, "id": header.id}

        task_bindings = (
            self.db.query(CrawlerTaskHeader, RequestHeader)
            .join(RequestHeader, CrawlerTaskHeader.header_id == RequestHeader.id)
            .filter(CrawlerTaskHeader.task_id == task_id)
            .filter(CrawlerTaskHeader.enabled.is_(True))
            .all()
        )

        for binding, header in task_bindings:
            if header.status != "enabled":
                continue
            priority = binding.priority_override if binding.priority_override is not None else header.priority
            if recent_before and header.last_used and header.last_used >= recent_before:
                priority = int(priority or 0) - 10
            # 任务绑定优先
            header_map[header.name] = {"value": header.value, "priority": priority, "id": header.id}

        for entry in header_map.values():
            if entry.get("id"):
                used_ids.add(entry["id"])

        return {name: entry["value"] for name, entry in header_map.items()}, list(used_ids)

    def _record_header_usage(self, header_ids: List[int], success: bool) -> None:
        if not header_ids:
            return
        now = datetime.utcnow()
        headers = self.db.query(RequestHeader).filter(RequestHeader.id.in_(header_ids)).all()
        for header in headers:
            header.usage_count = (header.usage_count or 0) + 1
            if success:
                header.success_count = (header.success_count or 0) + 1
            header.last_used = now
        self.db.commit()

    def _choose_proxy_for_request(self) -> Optional[IPPool]:
        reuse_seconds = max(0, int(settings.REQUEST_PROXY_REUSE_MIN_SECONDS))
        base_query = self.db.query(IPPool).filter(IPPool.status.in_(["active", "testing"]))

        if reuse_seconds > 0:
            recent_before = datetime.utcnow() - timedelta(seconds=reuse_seconds)
            preferred = (
                base_query.filter(and_(IPPool.last_used.isnot(None), IPPool.last_used < recent_before))
                .order_by(IPPool.last_used.asc(), IPPool.updated_at.asc(), IPPool.id.asc())
                .first()
            )
            if preferred:
                return preferred

            never_used = (
                base_query.filter(IPPool.last_used.is_(None))
                .order_by(IPPool.updated_at.asc(), IPPool.id.asc())
                .first()
            )
            if never_used:
                return never_used

        return base_query.order_by(IPPool.last_used.asc(), IPPool.updated_at.asc(), IPPool.id.asc()).first()

    def _record_proxy_usage(self, proxy: Optional[IPPool], success: bool) -> None:
        if not proxy:
            return

        proxy.last_used = datetime.utcnow()
        if success:
            proxy.success_count = int(proxy.success_count or 0) + 1
            proxy.fail_reason = None
            proxy.status = "active"
        else:
            proxy.failure_count = int(proxy.failure_count or 0) + 1
            proxy.fail_reason = "request_failed"
            fail_count = int(proxy.failure_count or 0)
            threshold = max(1, int(settings.IP_POOL_FAILURES_BEFORE_COOLING))
            proxy.status = "cooling" if fail_count >= threshold else "testing"
        self.db.commit()

    def _execute_task_logic(self, task: CrawlerTask) -> Dict[str, Any]:
        """
        执行任务的具体逻辑
        
        Args:
            task: 任务对象
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        # 这里应该根据任务类型执行不同的爬虫逻辑
        import random
        import time
        
        # 模拟爬虫执行过程
        time.sleep(2)  # 模拟网络请求时间
        
        # 模拟数据抓取结果
        items_processed = random.randint(10, 100)
        items_success = int(items_processed * 0.9)  # 90%的成功率
        items_failed = items_processed - items_success
        
        return {
            "status": "SUCCESS",
            "items_processed": items_processed,
            "items_success": items_success,
            "items_failed": items_failed,
            "success": True,
            "message": f"成功处理了 {items_processed} 个项目，其中 {items_success} 个成功，{items_failed} 个失败"
        }
    
    async def _execute_five_hundred_task(self, task):
        """执行500彩票网爬虫任务"""
        from ..scrapers.sources.five_hundred_scraper import FiveHundredScraper
        from ..models.matches import FootballMatch
        from sqlalchemy.orm import sessionmaker
        from ..core.database import engine
        from datetime import datetime
        
        # 获取爬取天数，默认为3天
        days = task.config.get("days", 3) if task.config else 3
        
        # 创建爬虫实例
        scraper = FiveHundredScraper()
        
        try:
            # 执行爬取
            matches_data = await scraper.get_matches(days=days)
            
            # 创建数据库会话
            Session = sessionmaker(bind=engine)
            db = Session()
            
            try:
                # 将爬取的数据保存到数据库
                created_count = 0
                for match_data in matches_data:
                    # 检查是否已存在该比赛
                    existing_match = db.query(FootballMatch).filter(
                        FootballMatch.match_id == match_data['match_id']
                    ).first()
                    
                    if not existing_match:
                        # 创建新的比赛记录
                        match = FootballMatch(
                            match_id=match_data['match_id'],
                            home_team=match_data['home_team'],
                            away_team=match_data['away_team'],
                            match_time=datetime.strptime(match_data['match_date'], "%Y-%m-%d %H:%M:%S") if match_data['match_date'] else datetime.now(),
                            league=match_data['league'],
                            status=match_data['status']
                        )
                        
                        db.add(match)
                        created_count += 1
                
                db.commit()
                
                return {
                    "success": True,
                    "status": "SUCCESS",
                    "message": f"成功爬取并保存了 {created_count} 条比赛数据到数据库",
                    "items_processed": len(matches_data),
                    "items_success": created_count,
                    "items_failed": len(matches_data) - created_count,
                    "duration": 0
                }
            finally:
                db.close()
        finally:
            await scraper.close()
    
    def stop_task(self, task_id: int) -> Dict[str, Any]:
        """
        停止正在运行的任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict[str, Any]: 停止结果
        """
        # 检查任务是否存在
        task = self.db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
        if not task:
            return {
                "success": False,
                "message": "任务不存在",
                "task_id": task_id
            }
        
        # 检查任务是否正在运行
        if task.status != "RUNNING":
            return {
                "success": False,
                "message": "任务未在运行中，无法停止",
                "task_id": task_id
            }
        
        # 尝试停止任务线程
        thread = self._running_tasks.get(task_id)
        if thread:
            # 注意：Python的threading模块没有直接停止线程的方法
            # 这里只是从运行任务列表中移除，实际的爬虫任务可能需要实现中断机制
            del self._running_tasks[task_id]
        
        # 更新任务状态为已停止
        task.status = "STOPPED"
        task.updated_at = datetime.utcnow()
        self.db.commit()
        
        # 记录停止任务的日志
        log_entry = CrawlerTaskLog(
            task_id=task.id,
            source_id=task.source_id,
            status="STOPPED",
            started_at=datetime.utcnow(),
            records_processed=0,
            records_success=0,
            records_failed=0,
            error_message="任务被用户手动停止"
        )
        self.db.add(log_entry)
        self.db.commit()
        
        return {
            "success": True,
            "message": "任务已停止",
            "task_id": task_id
        }

    def get_task_logs(self, task_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取任务执行日志
        
        Args:
            task_id: 任务ID
            limit: 日志条数限制
            
        Returns:
            List[Dict[str, Any]]: 日志列表
        """
        # 查询数据库中的日志
        logs = self.db.query(CrawlerTaskLog).filter(
            CrawlerTaskLog.task_id == task_id
        ).order_by(CrawlerTaskLog.created_at.desc()).limit(limit).all()

        # 转换为字典格式
        logs_data = []
        for log in logs:
            log_dict = {
                'id': log.id,
                'task_id': log.task_id,
                'source_id': log.source_id,
                'status': log.status,
                'message': log.error_message or f"Task {log.status}",
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'started_at': log.started_at.isoformat() if log.started_at else None,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'records_processed': log.records_processed or 0,
                'records_success': log.records_success or 0,
                'records_failed': log.records_failed or 0
            }
            logs_data.append(log_dict)

        # 反转列表以显示最新的日志在前面
        logs_data.reverse()

        return logs_data
    
    def _validate_cron_expression(self, cron_expr: str) -> bool:
        """
        验证Cron表达式（简单验证）
        
        Args:
            cron_expr: Cron表达式
            
        Returns:
            bool: 是否有效
        """
        if not cron_expr:
            return False
        
        parts = cron_expr.split()
        # 简单的5位或6位Cron表达式验证
        if len(parts) < 5 or len(parts) > 6:
            return False
        
        # 检查基本格式（更严格的验证需要使用专门的库如croniter）
        return all(part.strip() for part in parts)
    
    def _generate_log_message(self, status: str, task_id: int) -> str:
        """
        生成日志消息
        
        Args:
            status: 状态
            task_id: 任务ID
            
        Returns:
            str: 日志消息
        """
        messages = {
            "success": [
                f"任务 {task_id} 执行成功，数据抓取完成",
                f"任务 {task_id} 正常运行，未发现异常",
                f"任务 {task_id} 数据采集成功，质量良好"
            ],
            "error": [
                f"任务 {task_id} 执行失败，网络连接超时",
                f"任务 {task_id} 数据源返回错误状态码",
                f"任务 {task_id} 解析数据时发生异常"
            ],
            "warning": [
                f"任务 {task_id} 部分数据格式异常，已跳过",
                f"任务 {task_id} 响应时间过长，建议优化",
                f"任务 {task_id} 数据源返回数据不完整"
            ]
        }
        
        import random
        return random.choice(messages.get(status, ["未知状态"]))
    
    def calculate_next_run_time(self, cron_expression: str, last_run: datetime) -> datetime:
        """
        计算下次运行时间
        
        Args:
            cron_expression: Cron表达式
            last_run: 上次运行时间
            
        Returns:
            datetime: 下次运行时间
        """
        # 简化实现：基于Cron表达式的简单计算
        # 实际应用中应使用croniter等专业库
        
        if "* * * *" in cron_expression:  # 每分钟
            return last_run + timedelta(minutes=1)
        elif "0 * * * *" in cron_expression:  # 每小时
            return last_run + timedelta(hours=1)
        elif "0 0 * * *" in cron_expression:  # 每天
            return last_run + timedelta(days=1)
        elif "0 0 * * 0" in cron_expression:  # 每周
            return last_run + timedelta(weeks=1)
        else:
            # 默认1小时后
            return last_run + timedelta(hours=1)
