"""
数据源适配器框架（阶段一改造）

提供多数据源统一接入接口，支持不同数据源的字段映射和数据标准化。
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from enum import Enum


class DataSourceType(Enum):
    """数据源类型枚举"""
    API = "api"
    FILE = "file"
    CRAWLER = "crawler"
    DATABASE = "database"


class DataSourceStatus(Enum):
    """数据源状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class MatchData:
    """标准化比赛数据类"""
    
    def __init__(
        self,
        source_match_id: str,
        data_source: str,
        match_time: datetime,
        home_team: str,
        away_team: str,
        league: Optional[str] = None,
        **kwargs
    ):
        self.source_match_id = source_match_id
        self.data_source = data_source
        self.match_time = match_time
        self.home_team = home_team
        self.away_team = away_team
        self.league = league
        self.standard_fields = kwargs.get('standard_fields', {})
        self.source_attributes = kwargs.get('source_attributes', {})
        self.data_version = kwargs.get('data_version', 1)
        self.quality_score = kwargs.get('quality_score', 100)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于数据库存储"""
        return {
            'source_match_id': self.source_match_id,
            'data_source': self.data_source,
            'match_time': self.match_time,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'league': self.league,
            'standard_fields': self.standard_fields,
            'source_attributes': self.source_attributes,
            'data_version': self.data_version,
            'quality_score': self.quality_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MatchData':
        """从字典创建MatchData实例"""
        return cls(
            source_match_id=data['source_match_id'],
            data_source=data['data_source'],
            match_time=data['match_time'],
            home_team=data['home_team'],
            away_team=data['away_team'],
            league=data.get('league'),
            standard_fields=data.get('standard_fields', {}),
            source_attributes=data.get('source_attributes', {}),
            data_version=data.get('data_version', 1),
            quality_score=data.get('quality_score', 100)
        )


class DataSourceAdapter(ABC):
    """数据源适配器抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_code = config.get('source_code', 'unknown')
        self.source_name = config.get('source_name', 'Unknown Source')
        self.field_mapping = config.get('field_mapping', {})
        self.update_frequency = config.get('update_frequency', 60)  # 分钟
    
    @abstractmethod
    def fetch_matches(self) -> List[MatchData]:
        """
        从数据源获取比赛数据
        
        Returns:
            List[MatchData]: 标准化后的比赛数据列表
        """
        pass
    
    @abstractmethod
    def transform_to_standard(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将原始数据转换为标准化格式
        
        Args:
            raw_data: 原始数据
            
        Returns:
            标准化数据字典，包含标准字段和源特定字段
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        验证数据有效性
        
        Args:
            data: 待验证数据
            
        Returns:
            bool: 数据是否有效
        """
        pass
    
    def map_field(self, field_name: str, raw_value: Any) -> Any:
        """
        根据字段映射配置转换字段值
        
        Args:
            field_name: 原始字段名
            raw_value: 原始值
            
        Returns:
            转换后的字段值
        """
        mapping = self.field_mapping.get(field_name, {})
        
        # 如果映射配置中有转换函数
        if 'transform' in mapping:
            transform_func = mapping['transform']
            return self._apply_transform(transform_func, raw_value)
        
        # 如果映射配置中有目标字段名
        if 'target' in mapping:
            # 这里只是记录映射关系，实际值转换在transform_to_standard中处理
            pass
        
        return raw_value
    
    def _apply_transform(self, transform_func: str, value: Any) -> Any:
        """应用转换函数"""
        # 内置转换函数
        if transform_func == 'datetime_parser':
            # 尝试解析各种日期时间格式
            if isinstance(value, str):
                try:
                    # 尝试ISO格式
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    # 尝试其他格式
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                        try:
                            return datetime.strptime(value, fmt)
                        except:
                            continue
            return value
        elif transform_func == 'team_name_normalizer':
            # 球队名称标准化
            if isinstance(value, str):
                # 去除多余空格，统一大小写
                return value.strip().title()
            return value
        elif transform_func == 'odds_normalizer':
            # 赔率标准化
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                try:
                    return float(value.replace(',', ''))
                except:
                    return 0.0
            return 0.0
        
        # 自定义转换函数（需要在子类中实现）
        if hasattr(self, transform_func):
            return getattr(self, transform_func)(value)
        
        return value
    
    def get_source_info(self) -> Dict[str, Any]:
        """获取数据源信息"""
        return {
            'source_code': self.source_code,
            'source_name': self.source_name,
            'type': self.config.get('type', 'api'),
            'status': self.config.get('status', 'online'),
            'update_frequency': self.update_frequency,
            'field_mapping': self.field_mapping
        }


class Source100QiuAdapter(DataSourceAdapter):
    """100qiu数据源适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 100qiu特定配置
        self.base_url = config.get('base_url', 'https://api.100qiu.com')
        self.api_key = config.get('api_key', '')
        
        # 字段映射配置
        self.field_mapping = {
            'lineId': {'target': 'source_match_id'},
            'matchTimeStr': {'target': 'match_time', 'transform': 'datetime_parser'},
            'homeTeam': {'target': 'home_team', 'transform': 'team_name_normalizer'},
            'guestTeam': {'target': 'away_team', 'transform': 'team_name_normalizer'},
            'gameShortName': {'target': 'league'},
            'rq': {'target': 'handicap'},
            'homePower': {'target': 'home_power'},
            'guestPower': {'target': 'away_power'},
            'homeWinAward': {'target': 'home_win_odds', 'transform': 'odds_normalizer'},
            'guestWinAward': {'target': 'away_win_odds', 'transform': 'odds_normalizer'},
        }
    
    def fetch_matches(self) -> List[MatchData]:
        """从100qiu API获取比赛数据"""
        # 这里实现实际的API调用逻辑
        # 由于是框架，返回空列表
        return []
    
    def transform_to_standard(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """转换100qiu数据为标准格式"""
        standard_fields = {}
        source_attributes = {}
        
        # 应用字段映射
        for raw_field, mapping in self.field_mapping.items():
            if raw_field in raw_data:
                target_field = mapping.get('target')
                raw_value = raw_data[raw_field]
                
                # 应用转换
                transformed_value = self.map_field(raw_field, raw_value)
                
                if target_field:
                    # 标准字段
                    standard_fields[target_field] = transformed_value
                else:
                    # 源特定字段
                    source_attributes[raw_field] = transformed_value
        
        # 确保必填字段存在
        required_fields = ['source_match_id', 'match_time', 'home_team', 'away_team']
        for req in required_fields:
            if req not in standard_fields:
                # 尝试从原始数据中查找
                for raw_field, mapping in self.field_mapping.items():
                    if mapping.get('target') == req and raw_field in raw_data:
                        standard_fields[req] = self.map_field(raw_field, raw_data[raw_field])
                        break
        
        return {
            'standard_fields': standard_fields,
            'source_attributes': source_attributes,
            'data_source': self.source_code,
            'data_version': 1
        }
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证100qiu数据"""
        required = ['lineId', 'matchTimeStr', 'homeTeam', 'guestTeam']
        for field in required:
            if field not in data or not data[field]:
                return False
        
        # 验证时间格式
        match_time = data.get('matchTimeStr')
        if match_time:
            try:
                datetime.fromisoformat(match_time.replace('Z', '+00:00'))
            except:
                # 尝试其他格式
                try:
                    datetime.strptime(match_time, '%Y-%m-%d %H:%M:%S')
                except:
                    return False
        
        return True


class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self):
        self.adapters: Dict[str, DataSourceAdapter] = {}
        self.configs: Dict[str, Dict[str, Any]] = {}
    
    def register_adapter(self, source_code: str, adapter_class, config: Dict[str, Any]):
        """注册数据源适配器"""
        adapter = adapter_class(config)
        self.adapters[source_code] = adapter
        self.configs[source_code] = config
    
    def get_adapter(self, source_code: str) -> Optional[DataSourceAdapter]:
        """获取数据源适配器"""
        return self.adapters.get(source_code)
    
    def fetch_all_matches(self) -> Dict[str, List[MatchData]]:
        """从所有已注册数据源获取比赛数据"""
        results = {}
        
        for source_code, adapter in self.adapters.items():
            try:
                matches = adapter.fetch_matches()
                results[source_code] = matches
            except Exception as e:
                print(f"从数据源 {source_code} 获取数据失败: {e}")
                results[source_code] = []
        
        return results
    
    def transform_all_matches(self, raw_data_dict: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[MatchData]]:
        """转换所有数据源的原始数据"""
        results = {}
        
        for source_code, raw_data_list in raw_data_dict.items():
            adapter = self.get_adapter(source_code)
            if not adapter:
                continue
            
            transformed_matches = []
            for raw_data in raw_data_list:
                if adapter.validate_data(raw_data):
                    transformed = adapter.transform_to_standard(raw_data)
                    match_data = MatchData(
                        source_match_id=transformed['standard_fields'].get('source_match_id', ''),
                        data_source=source_code,
                        match_time=transformed['standard_fields'].get('match_time'),
                        home_team=transformed['standard_fields'].get('home_team', ''),
                        away_team=transformed['standard_fields'].get('away_team', ''),
                        league=transformed['standard_fields'].get('league'),
                        standard_fields=transformed['standard_fields'],
                        source_attributes=transformed['source_attributes'],
                        data_version=transformed.get('data_version', 1)
                    )
                    transformed_matches.append(match_data)
            
            results[source_code] = transformed_matches
        
        return results


# 全局数据源管理器实例
data_source_manager = DataSourceManager()


def init_default_adapters():
    """初始化默认适配器"""
    # 100qiu数据源配置
    config_100qiu = {
        'source_code': 'source_100qiu',
        'source_name': '100球数据源',
        'type': 'api',
        'base_url': 'https://api.100qiu.com',
        'api_key': '',
        'update_frequency': 30,
        'status': 'online'
    }
    
    data_source_manager.register_adapter('source_100qiu', Source100QiuAdapter, config_100qiu)
    
    # 可以在这里添加其他默认适配器
    # config_500 = {...}
    # data_source_manager.register_adapter('source_500', Source500Adapter, config_500)


# 模块导入时初始化默认适配器
init_default_adapters()