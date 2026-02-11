"""
数据源类型定义和枚举
扩展支持多种数据源类型
"""
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DataSourceType(str, Enum):
    """数据源类型枚举"""
    # 基础类型
    API = "api"                    # REST API数据源
    FILE = "file"                  # 文件数据源
    DATABASE = "database"          # 数据库连接
    
    # 体育数据特定类型
    SPORTS_API = "sports_api"      # 体育数据API
    ODDS_API = "odds_api"          # 赔率数据API
    LIVE_SCORE = "live_score"      # 实时比分数据
    
    # 爬虫类型
    WEB_CRAWLER = "web_crawler"    # 网页爬虫
    RSS_FEED = "rss_feed"          # RSS订阅源
    
    # 流式数据
    WEBSOCKET = "websocket"        # WebSocket实时流
    MESSAGE_QUEUE = "message_queue" # 消息队列
    
    # 第三方服务
    THIRD_PARTY = "third_party"    # 第三方服务集成
    CUSTOM = "custom"              # 自定义数据源


class DataSourceConfig(BaseModel):
    """数据源配置基类"""
    name: str = Field(..., description="数据源名称")
    type: DataSourceType = Field(..., description="数据源类型")
    description: Optional[str] = Field(None, description="数据源描述")
    
    class Config:
        use_enum_values = True


class APIDataSourceConfig(DataSourceConfig):
    """API数据源配置"""
    base_url: str = Field(..., description="API基础URL")
    auth_type: str = Field("none", description="认证类型: none/basic/token/oauth2")
    auth_config: Optional[Dict[str, Any]] = Field(None, description="认证配置")
    rate_limit: Optional[int] = Field(None, description="请求频率限制(次/分钟)")
    timeout: int = Field(30, description="请求超时时间(秒)")
    retry_times: int = Field(3, description="重试次数")
    
    type: DataSourceType = Field(DataSourceType.API, description="数据源类型")


class FileDataSourceConfig(DataSourceConfig):
    """文件数据源配置"""
    file_path: str = Field(..., description="文件路径")
    file_format: str = Field("json", description="文件格式: json/csv/xml")
    encoding: str = Field("utf-8", description="文件编码")
    delimiter: Optional[str] = Field(None, description="分隔符(CSV文件)")
    has_header: bool = Field(True, description="是否有表头(CSV文件)")
    
    type: DataSourceType = Field(DataSourceType.FILE, description="数据源类型")


class DatabaseDataSourceConfig(DataSourceConfig):
    """数据库数据源配置"""
    connection_string: str = Field(..., description="数据库连接字符串")
    driver: str = Field(..., description="数据库驱动")
    schema_name: Optional[str] = Field(None, description="数据库模式")
    table_name: Optional[str] = Field(None, description="表名")
    query: Optional[str] = Field(None, description="查询SQL")
    
    type: DataSourceType = Field(DataSourceType.DATABASE, description="数据源类型")


class WebSocketDataSourceConfig(DataSourceConfig):
    """WebSocket数据源配置"""
    ws_url: str = Field(..., description="WebSocket连接URL")
    protocol: str = Field("ws", description="协议: ws/wss")
    reconnect_interval: int = Field(5, description="重连间隔(秒)")
    heartbeat_interval: int = Field(30, description="心跳间隔(秒)")
    message_format: str = Field("json", description="消息格式: json/protobuf/text")
    
    type: DataSourceType = Field(DataSourceType.WEBSOCKET, description="数据源类型")


class MessageQueueDataSourceConfig(DataSourceConfig):
    """消息队列数据源配置"""
    queue_type: str = Field(..., description="队列类型: rabbitmq/kafka/redis")
    connection_config: Dict[str, Any] = Field(..., description="连接配置")
    topic: Optional[str] = Field(None, description="主题/队列名称")
    consumer_group: Optional[str] = Field(None, description="消费者组")
    
    type: DataSourceType = Field(DataSourceType.MESSAGE_QUEUE, description="数据源类型")


class SportsAPIDataSourceConfig(APIDataSourceConfig):
    """体育数据API配置"""
    sport_type: str = Field("soccer", description="体育类型: soccer/basketball/tennis")
    data_category: str = Field("matches", description="数据类别: matches/odds/standings")
    league_filter: Optional[str] = Field(None, description="联赛过滤")
    
    type: DataSourceType = Field(DataSourceType.SPORTS_API, description="数据源类型")


class OddsAPIDataSourceConfig(APIDataSourceConfig):
    """赔率数据API配置"""
    bookmaker: str = Field(..., description="博彩公司")
    market_type: str = Field("1x2", description="市场类型: 1x2/asian/over_under")
    odds_format: str = Field("decimal", description="赔率格式: decimal/fraction/american")
    
    type: DataSourceType = Field(DataSourceType.ODDS_API, description="数据源类型")


# 数据源类型映射
DATA_SOURCE_TYPE_MAPPING = {
    DataSourceType.API: APIDataSourceConfig,
    DataSourceType.FILE: FileDataSourceConfig,
    DataSourceType.DATABASE: DatabaseDataSourceConfig,
    DataSourceType.WEBSOCKET: WebSocketDataSourceConfig,
    DataSourceType.MESSAGE_QUEUE: MessageQueueDataSourceConfig,
    DataSourceType.SPORTS_API: SportsAPIDataSourceConfig,
    DataSourceType.ODDS_API: OddsAPIDataSourceConfig,
    DataSourceType.LIVE_SCORE: APIDataSourceConfig,
    DataSourceType.WEB_CRAWLER: APIDataSourceConfig,
    DataSourceType.RSS_FEED: APIDataSourceConfig,
    DataSourceType.THIRD_PARTY: APIDataSourceConfig,
    DataSourceType.CUSTOM: DataSourceConfig
}


def create_data_source_config(
    source_type: DataSourceType, 
    config_data: Dict[str, Any]
) -> DataSourceConfig:
    """根据类型创建数据源配置对象"""
    config_class = DATA_SOURCE_TYPE_MAPPING.get(source_type, DataSourceConfig)
    
    # 确保类型字段正确设置
    config_data['type'] = source_type
    
    try:
        return config_class(**config_data)
    except Exception as e:
        # 如果创建失败，返回基础配置
        return DataSourceConfig(
            name=config_data.get('name', 'unknown'),
            type=source_type,
            description=config_data.get('description')
        )


def get_data_source_type_description(source_type: DataSourceType) -> str:
    """获取数据源类型描述"""
    descriptions = {
        DataSourceType.API: "REST API接口数据源",
        DataSourceType.FILE: "文件数据源（JSON/CSV/XML）",
        DataSourceType.DATABASE: "数据库连接数据源",
        DataSourceType.WEBSOCKET: "WebSocket实时数据流",
        DataSourceType.MESSAGE_QUEUE: "消息队列数据源",
        DataSourceType.SPORTS_API: "体育数据专用API",
        DataSourceType.ODDS_API: "赔率数据API",
        DataSourceType.LIVE_SCORE: "实时比分数据源",
        DataSourceType.WEB_CRAWLER: "网页爬虫数据源",
        DataSourceType.RSS_FEED: "RSS订阅数据源",
        DataSourceType.THIRD_PARTY: "第三方服务集成",
        DataSourceType.CUSTOM: "自定义数据源"
    }
    
    return descriptions.get(source_type, "未知数据源类型")


def get_supported_data_source_types() -> Dict[str, Any]:
    """获取支持的数据源类型列表"""
    types_info = []
    
    for source_type in DataSourceType:
        type_info = {
            'value': source_type.value,
            'description': get_data_source_type_description(source_type),
            'config_schema': DATA_SOURCE_TYPE_MAPPING.get(source_type).schema() 
                if source_type in DATA_SOURCE_TYPE_MAPPING else None
        }
        types_info.append(type_info)
    
    return {
        'total_types': len(DataSourceType),
        'types': types_info
    }