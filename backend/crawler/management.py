"""
爬虫管理模块
提供数据源和爬虫配置之间的同步功能
"""
import json
from sqlalchemy.orm import Session
from backend.models.data_sources import DataSource
from backend.models.crawler_config import CrawlerConfig


def create_crawler_config_from_data_source(db: Session, data_source: DataSource):
    """
    根据数据源创建对应的爬虫配置
    实现数据源和爬虫配置的双向同步机制
    """
    # 构建爬虫配置的配置数据
    config_data = {
        "type": data_source.type,
        "url": data_source.url,
        "status": data_source.status,
        "created_by": data_source.created_by
    }
    
    # 如果数据源中有额外的配置信息，合并到爬虫配置中
    if data_source.config:
        try:
            source_config = json.loads(data_source.config)
            config_data.update(source_config)
        except json.JSONDecodeError:
            # 如果配置不是有效的JSON，直接使用原字符串
            config_data["raw_config"] = data_source.config
    
    # 确保爬虫配置名称是唯一的
    crawler_config_name = f"Crawler-{data_source.name}" if len(data_source.name) < 180 else f"Crawler-{data_source.id}"
    
    # 检查名称是否已存在，如果存在则添加后缀
    existing_config = db.query(CrawlerConfig).filter(CrawlerConfig.name == crawler_config_name).first()
    counter = 1
    original_name = crawler_config_name
    while existing_config:
        crawler_config_name = f"{original_name}-{counter}"
        existing_config = db.query(CrawlerConfig).filter(CrawlerConfig.name == crawler_config_name).first()
        counter += 1
    
    # 创建爬虫配置对象
    crawler_config = CrawlerConfig(
        name=crawler_config_name,
        description=f"从数据源同步的爬虫配置: {data_source.name}",
        url=data_source.url,
        frequency=3600,  # 默认1小时执行一次
        is_active=data_source.status,
        config_data=json.dumps(config_data, ensure_ascii=False),
        created_by=data_source.created_by or 1,  # 默认创建者ID为1
        source_id=data_source.id  # 添加源ID关联
    )
    
    # 添加到数据库会话
    db.add(crawler_config)
    
    return crawler_config


def sync_data_source_to_crawler_config(db: Session, source_id: int):
    """
    同步指定数据源到爬虫配置
    """
    # 获取数据源
    data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not data_source:
        raise ValueError(f"数据源不存在，ID: {source_id}")
    
    # 检查是否已存在对应的爬虫配置
    existing_config = db.query(CrawlerConfig).filter(
        CrawlerConfig.source_id == source_id
    ).first()
    
    if existing_config:
        # 更新现有配置
        config_data = {
            "type": data_source.type,
            "url": data_source.url,
            "status": data_source.status,
            "created_by": data_source.created_by
        }
        
        if data_source.config:
            try:
                source_config = json.loads(data_source.config)
                config_data.update(source_config)
            except json.JSONDecodeError:
                config_data["raw_config"] = data_source.config
        
        existing_config.name = f"Crawler-{data_source.name}"[:190]  # 限制长度
        existing_config.description = f"从数据源同步的爬虫配置: {data_source.name}"
        existing_config.url = data_source.url
        existing_config.is_active = data_source.status
        existing_config.config_data = json.dumps(config_data, ensure_ascii=False)
        
        return existing_config
    else:
        # 创建新配置
        return create_crawler_config_from_data_source(db, data_source)


def sync_crawler_config_to_data_source(db: Session, config_id: int):
    """
    同步爬虫配置到数据源
    """
    # 获取爬虫配置
    crawler_config = db.query(CrawlerConfig).filter(CrawlerConfig.id == config_id).first()
    if not crawler_config:
        raise ValueError(f"爬虫配置不存在，ID: {config_id}")
    
    # 检查是否有关联的数据源
    if not crawler_config.source_id:
        raise ValueError(f"爬虫配置未关联数据源，ID: {config_id}")
    
    data_source = db.query(DataSource).filter(DataSource.id == crawler_config.source_id).first()
    if not data_source:
        raise ValueError(f"关联的数据源不存在，ID: {crawler_config.source_id}")
    
    # 从爬虫配置的config_data中提取相关信息
    try:
        config_data = json.loads(crawler_config.config_data)
    except json.JSONDecodeError:
        config_data = {}
    
    # 更新数据源
    data_source.name = crawler_config.name.replace("Crawler-", "")  # 移除前缀
    data_source.url = crawler_config.url
    data_source.status = crawler_config.is_active
    
    # 更新配置信息
    filtered_config = {k: v for k, v in config_data.items() 
                      if k not in ['type', 'url', 'status', 'created_by']}
    if filtered_config:
        data_source.config = json.dumps(filtered_config, ensure_ascii=False)
    
    return data_source