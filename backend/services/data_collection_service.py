"""
数据采集服务（已移除爬虫功能）
仅保留API和文件数据源的采集功能
"""

import aiohttp
import asyncio
import pandas as pd
import json
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..models.data_sources import DataSource
from ..models.matches import Match
from ..models.sp_records import SPRecord
from ..schemas.data_source import DataSourceCreate

logger = logging.getLogger(__name__)


class DataCollectionService:
    """数据采集服务（已移除爬虫功能）"""
    
    async def test_api_connection(self, url: str, config: str) -> Dict[str, Any]:
        """测试API数据源连接"""
        try:
            config_dict = json.loads(config) if config else {}
            headers = config_dict.get('headers', {})
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.text()
                        return {
                            "success": True,
                            "status_code": response.status,
                            "response_size": len(data),
                            "sample_data": data[:200] if len(data) > 200 else data
                        }
                    else:
                        return {
                            "success": False,
                            "status_code": response.status,
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            logger.error(f"API连接测试失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def fetch_api_data(self, db: Session, source_id: int) -> Dict[str, Any]:
        """从API拉取数据"""
        try:
            source = db.query(DataSource).filter(DataSource.id == source_id).first()
            if not source or source.type != 'api':
                raise ValueError("无效的数据源")
            
            config_dict = source.config_dict
            headers = config_dict.get('headers', {})
            
            async with aiohttp.ClientSession() as session:
                async with session.get(source.url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 根据配置的处理规则处理数据
                        processor = config_dict.get('processor', 'default')
                        processed_data = await self._process_api_data(data, processor)
                        
                        # 更新数据源状态
                        source.last_update = datetime.utcnow()
                        source.error_rate = 0
                        db.commit()
                        
                        return {
                            "success": True,
                            "records_processed": len(processed_data),
                            "data": processed_data[:10]  # 返回前10条作为样本
                        }
                    else:
                        raise Exception(f"API返回状态码: {response.status}")
                        
        except Exception as e:
            logger.error(f"API数据获取失败: {str(e)}")
            
            # 更新错误率
            source.error_rate = min(100, (source.error_rate or 0) + 10)
            db.commit()
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _process_api_data(self, data: Any, processor: str) -> List[Dict[str, Any]]:
        """处理API数据"""
        if processor == 'sporttery':
            return await self._process_sporttery_data(data)
        elif processor == 'custom':
            # 自定义处理逻辑
            return data
        else:
            # 默认处理逻辑
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            else:
                return [data]
    
    async def _process_sporttery_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理体彩数据格式"""
        # 这里根据实际的数据格式进行处理
        # 示例处理逻辑
        processed = []
        
        if 'matches' in data:
            for match in data['matches']:
                processed.append({
                    'match_id': match.get('id'),
                    'home_team': match.get('homeTeam'),
                    'away_team': match.get('awayTeam'),
                    'match_time': match.get('matchTime'),
                    'league': match.get('league'),
                    'status': match.get('status')
                })
        
        return processed
    
    async def import_file_data(self, db: Session, file_path: str, mapping: Dict[str, str]) -> Dict[str, Any]:
        """导入本地文件数据"""
        try:
            # 根据文件扩展名选择读取方式
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                raise ValueError(f"不支持的文件格式: {file_path}")
            
            # 应用字段映射
            df_mapped = pd.DataFrame()
            for target_field, source_field in mapping.items():
                if source_field in df.columns:
                    df_mapped[target_field] = df[source_field]
            
            # 数据验证
            validation_result = await self.validate_data_quality(df_mapped.to_dict('records'))
            
            if not validation_result['valid']:
                return {
                    "success": False,
                    "error": "数据验证失败",
                    "validation_errors": validation_result['errors']
                }
            
            # 导入数据到数据库
            imported_count = await self._import_matches_data(db, df_mapped.to_dict('records'))
            
            return {
                "success": True,
                "records_imported": imported_count,
                "total_records": len(df_mapped)
            }
            
        except Exception as e:
            logger.error(f"文件数据导入失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_data_quality(self, data_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证导入数据的质量和完整性"""
        errors = []
        warnings = []
        valid_count = 0
        
        required_fields = ['match_id', 'home_team', 'away_team', 'match_time']
        
        for idx, record in enumerate(data_batch):
            row_num = idx + 1
            
            # 检查必填字段
            for field in required_fields:
                if field not in record or not record[field]:
                    errors.append(f"第{row_num}行: 缺少必填字段 '{field}'")
            
            # 检查数据类型
            if 'match_time' in record:
                try:
                    datetime.fromisoformat(str(record['match_time']))
                except:
                    errors.append(f"第{row_num}行: 比赛时间格式错误")
            
            # 检查SP值范围
            if 'sp_value' in record:
                try:
                    sp_val = float(record['sp_value'])
                    if sp_val <= 0 or sp_val > 100:
                        warnings.append(f"第{row_num}行: SP值 {sp_val} 超出正常范围")
                except:
                    errors.append(f"第{row_num}行: SP值格式错误")
            
            if len(errors) == 0:
                valid_count += 1
        
        return {
            "valid": len(errors) == 0,
            "valid_count": valid_count,
            "total_count": len(data_batch),
            "errors": errors,
            "warnings": warnings
        }
    
    async def _import_matches_data(self, db: Session, matches_data: List[Dict[str, Any]]) -> int:
        """导入比赛数据到数据库"""
        imported = 0
        
        for match_data in matches_data:
            try:
                # 检查比赛是否已存在
                existing = db.query(Match).filter(
                    Match.match_id == match_data['match_id']
                ).first()
                
                if not existing:
                    match = Match(**match_data)
                    db.add(match)
                    imported += 1
                
            except Exception as e:
                logger.error(f"导入比赛数据失败: {str(e)}")
                continue
        
        db.commit()
        return imported
    
    async def update_match_history(self, db: Session, match_id: int):
        """更新比赛历史数据（异步任务）"""
        try:
            # 这里可以实现更新相关历史数据的逻辑
            # 例如：清理过期数据、更新统计信息等
            logger.info(f"更新比赛 {match_id} 的历史数据")
        except Exception as e:
            logger.error(f"更新比赛历史数据失败: {str(e)}")