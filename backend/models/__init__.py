"""
数据库模型包
"""
from .base import Base, BaseModel, BaseAuditModel, BaseSoftDeleteModel, BaseFullModel, BaseUUIDModel
from .match import Match, Team, League, MatchStatusEnum, MatchTypeEnum, MatchImportanceEnum
from .intelligence import Intelligence, IntelligenceType, IntelligenceSource, IntelligenceTypeEnum, IntelligenceSourceEnum
from .user_models import User, UserRole, UserStatus, SocialProvider, UserPrediction
from .venues import Venue, VenueTypeEnum, VenueSurfaceEnum
from .predictions import Prediction, PredictionMethodEnum, PredictionTypeEnum, PredictionAccuracyEnum
from .odds import Odds, Bookmaker, OddsProviderEnum, OddsTypeEnum, OddsMovementTypeEnum
from .data_review import DataReview, DataTypeEnum, ReviewStatusEnum
from .admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
from .data import AdminData, DataCategoryEnum
from .system_config import SystemConfig
from .crawler_config import CrawlerConfig
from .crawler_alert_rules import CrawlerAlertRule
from .crawler_alert_records import CrawlerAlertRecord
from .crawler_metrics import CrawlerMetric
from .intelligence_record import IntelligenceRecord
from .crawler_tasks import CrawlerTask
from .crawler_logs import CrawlerTaskLog, CrawlerSourceStat
from .department import Department

# SP管理模块新添加的模型
from .data_sources import DataSource
from .matches import FootballMatch
from .odds_companies import OddsCompany
from .sp_records import SPRecord
from .sp_modification_logs import SPModificationLog

# 平局预测管理模块模型
from .draw_feature import DrawFeature
from .draw_training_job import DrawTrainingJob
from .draw_model_version import DrawModelVersion
from .draw_prediction_result import DrawPredictionResult

# 日志模型
from .log_entry import LogEntry

__all__ = [
    # Base models
    "Base", "BaseModel", "BaseAuditModel", "BaseSoftDeleteModel", "BaseFullModel", "BaseUUIDModel",
    
    # Match-related models
    "Match", "Team", "League", 
    "MatchStatusEnum", "MatchTypeEnum", "MatchImportanceEnum",
    
    # Intelligence models
    "Intelligence", "IntelligenceType", "IntelligenceSource", "IntelligenceTypeEnum", "IntelligenceSourceEnum",
    
    # User models
    "User", "UserRole", "UserStatus", "SocialProvider", "UserPrediction",
    
    # Admin user models
    "AdminUser", "AdminRoleEnum", "AdminStatusEnum",
    "Department",
    
    # Venues models
    "Venue", "VenueTypeEnum", "VenueSurfaceEnum",
    
    # Predictions models (excluding UserPrediction since it's now in user_models)
    "Prediction", "PredictionMethodEnum", "PredictionTypeEnum", "PredictionAccuracyEnum",
    
    # Odds models
    "Odds", "Bookmaker", "OddsProviderEnum", "OddsTypeEnum", "OddsMovementTypeEnum",
    
    # Data review models
    "DataReview", "DataTypeEnum", "ReviewStatusEnum",
    
    # Data models
    "AdminData", "DataCategoryEnum",
    
    # System config models
    "SystemConfig",
    
    # Crawler config models
    "CrawlerConfig",
    
    # Crawler alert models
    "CrawlerAlertRule",
    "CrawlerAlertRecord",
    "CrawlerMetric",
    
    # Intelligence record models
    "IntelligenceRecord",
    
    # Crawler task models
    "CrawlerTask",
    
    # Crawler log models
    "CrawlerTaskLog",
    "CrawlerSourceStat",
    
    # SP管理模块新添加的模型
    "DataSource",
    "FootballMatch",
    "OddsCompany", 
    "SPRecord",
    "SPModificationLog",
    
    # 平局预测管理模块模型
    "DrawFeature",
    "DrawTrainingJob",
    "DrawModelVersion",
    "DrawPredictionResult",
    
    # 日志模型
    "LogEntry"
]