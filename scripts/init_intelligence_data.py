#!/usr/bin/env python3
"""
情报数据初始化脚本
将系统情报类型和情报来源数据插入数据库
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.base import Base
from backend.models.intelligence import (
    IntelligenceType, IntelligenceSource,
    SYSTEM_INTELLIGENCE_TYPES, SYSTEM_INTELLIGENCE_SOURCES
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntelligenceDataInitializer:
    """情报数据初始化器"""
    
    def __init__(self, database_url=None):
        """
        初始化数据初始化器
        
        Args:
            database_url: 数据库连接URL，如果为None则使用默认配置
        """
        if database_url is None:
            # 从环境变量获取或使用默认SQLite数据库
            database_url = os.getenv(
                'DATABASE_URL',
                'sqlite:///./sport_lottery.db'
            )
        
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info(f"连接到数据库: {database_url}")
    
    def init_intelligence_types(self, session):
        """
        初始化系统情报类型
        
        Args:
            session: SQLAlchemy会话
        """
        logger.info("开始初始化系统情报类型...")
        
        existing_types = session.query(IntelligenceType).all()
        existing_codes = {t.code for t in existing_types}
        
        inserted_count = 0
        updated_count = 0
        
        for type_data in SYSTEM_INTELLIGENCE_TYPES:
            code = type_data['code']
            
            # 检查是否已存在
            existing_type = session.query(IntelligenceType).filter_by(code=code).first()
            
            if existing_type:
                # 更新现有记录
                for key, value in type_data.items():
                    if hasattr(existing_type, key):
                        setattr(existing_type, key, value)
                existing_type.updated_at = datetime.utcnow()
                updated_count += 1
                logger.debug(f"更新情报类型: {code}")
            else:
                # 创建新记录
                new_type = IntelligenceType(
                    **type_data,
                    is_system=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(new_type)
                inserted_count += 1
                logger.debug(f"创建情报类型: {code}")
        
        session.commit()
        logger.info(f"情报类型初始化完成: 新增{inserted_count}个，更新{updated_count}个")
        return inserted_count + updated_count
    
    def init_intelligence_sources(self, session):
        """
        初始化系统信息来源
        
        Args:
            session: SQLAlchemy会话
        """
        logger.info("开始初始化系统信息来源...")
        
        existing_sources = session.query(IntelligenceSource).all()
        existing_codes = {s.code for s in existing_sources}
        
        inserted_count = 0
        updated_count = 0
        
        for source_data in SYSTEM_INTELLIGENCE_SOURCES:
            code = source_data['code']
            
            # 检查是否已存在
            existing_source = session.query(IntelligenceSource).filter_by(code=code).first()
            
            if existing_source:
                # 更新现有记录
                for key, value in source_data.items():
                    if hasattr(existing_source, key):
                        setattr(existing_source, key, value)
                existing_source.updated_at = datetime.utcnow()
                updated_count += 1
                logger.debug(f"更新信息来源: {code}")
            else:
                # 创建新记录
                new_source = IntelligenceSource(
                    **source_data,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(new_source)
                inserted_count += 1
                logger.debug(f"创建信息来源: {code}")
        
        session.commit()
        logger.info(f"信息来源初始化完成: 新增{inserted_count}个，更新{updated_count}个")
        return inserted_count + updated_count
    
    def verify_data_integrity(self, session):
        """
        验证数据完整性
        
        Args:
            session: SQLAlchemy会话
        
        Returns:
            tuple: (是否成功, 错误消息)
        """
        logger.info("开始验证数据完整性...")
        
        try:
            # 检查必要的系统类型是否存在
            required_type_codes = ['injury', 'suspension', 'lineup', 'odds', 'prediction', 'statistics']
            type_count = session.query(IntelligenceType).filter(
                IntelligenceType.code.in_(required_type_codes),
                IntelligenceType.is_active == True
            ).count()
            
            if type_count < len(required_type_codes):
                missing = set(required_type_codes) - {
                    t.code for t in session.query(IntelligenceType.code)
                    .filter(IntelligenceType.code.in_(required_type_codes))
                    .all()
                }
                return False, f"缺少必要的系统情报类型: {missing}"
            
            # 检查必要的来源是否存在
            required_source_codes = ['official_jc', 'william_hill', 'espn', 'system_analysis']
            source_count = session.query(IntelligenceSource).filter(
                IntelligenceSource.code.in_(required_source_codes),
                IntelligenceSource.is_active == True
            ).count()
            
            if source_count < len(required_source_codes):
                missing = set(required_source_codes) - {
                    s.code for s in session.query(IntelligenceSource.code)
                    .filter(IntelligenceSource.code.in_(required_source_codes))
                    .all()
                }
                return False, f"缺少必要的系统信息来源: {missing}"
            
            # 检查数据一致性
            type_codes = [t.code for t in session.query(IntelligenceType.code).all()]
            source_codes = [s.code for s in session.query(IntelligenceSource.code).all()]
            
            logger.info(f"当前系统情报类型数量: {len(type_codes)}")
            logger.info(f"当前系统信息来源数量: {len(source_codes)}")
            
            return True, "数据完整性验证通过"
            
        except Exception as e:
            return False, f"数据完整性验证失败: {str(e)}"
    
    def create_sample_intelligence_data(self, session):
        """
        创建示例情报数据（用于测试）
        
        Args:
            session: SQLAlchemy会话
        
        Returns:
            int: 创建的示例数据数量
        """
        logger.info("开始创建示例情报数据...")
        
        # 这里可以添加示例情报数据的创建逻辑
        # 由于需要依赖matches、teams等表，这里暂时跳过
        # 可以在后续的测试数据初始化脚本中补充
        
        logger.info("示例情报数据创建跳过（需要依赖其他表数据）")
        return 0
    
    def run(self, skip_verification=False, create_samples=False):
        """
        运行数据初始化
        
        Args:
            skip_verification: 是否跳过数据完整性验证
            create_samples: 是否创建示例数据
        
        Returns:
            bool: 是否成功
        """
        logger.info("=" * 50)
        logger.info("开始初始化情报数据")
        logger.info("=" * 50)
        
        session = self.SessionLocal()
        
        try:
            # 1. 初始化情报类型
            type_count = self.init_intelligence_types(session)
            
            # 2. 初始化信息来源
            source_count = self.init_intelligence_sources(session)
            
            # 3. 验证数据完整性
            if not skip_verification:
                success, message = self.verify_data_integrity(session)
                if not success:
                    logger.error(f"数据完整性验证失败: {message}")
                    return False
                logger.info(message)
            
            # 4. 创建示例数据（可选）
            if create_samples:
                sample_count = self.create_sample_intelligence_data(session)
                logger.info(f"创建了 {sample_count} 条示例情报数据")
            
            # 输出汇总信息
            logger.info("=" * 50)
            logger.info("情报数据初始化完成")
            logger.info(f"  情报类型: {type_count} 条记录")
            logger.info(f"  信息来源: {source_count} 条记录")
            logger.info("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"初始化过程中发生错误: {str(e)}", exc_info=True)
            session.rollback()
            return False
            
        finally:
            session.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='情报数据初始化脚本')
    parser.add_argument('--database-url', help='数据库连接URL')
    parser.add_argument('--skip-verification', action='store_true', 
                       help='跳过数据完整性验证')
    parser.add_argument('--create-samples', action='store_true',
                       help='创建示例情报数据')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细日志')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 运行初始化
    initializer = IntelligenceDataInitializer(args.database_url)
    success = initializer.run(
        skip_verification=args.skip_verification,
        create_samples=args.create_samples
    )
    
    if success:
        logger.info("✅ 情报数据初始化成功完成")
        return 0
    else:
        logger.error("❌ 情报数据初始化失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())