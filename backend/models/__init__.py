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
# Added missing OddsProvider import
from .odds import OddsProvider
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
from .crawler_task_headers import CrawlerTaskHeader
from .crawler_logs import CrawlerTaskLog, CrawlerSourceStat
from .department import Department

# SP管理模块新添加的模型
from .data_sources import DataSource
from .data_source_headers import DataSourceHeader
from .matches import FootballMatch
from .odds_companies import OddsCompany
from .sp_records import SPRecord
from .sp_modification_logs import SPModificationLog
from .user_activity import UserActivity
from .system_config import SystemConfig

# 请求头和IP池管理模型
from .headers import RequestHeader
from .ip_pool import IPPool

# 平局预测管理模块模型
from .draw_feature import DrawFeature
from .draw_training_job import DrawTrainingJob
from .draw_model_version import DrawModelVersion
from .draw_prediction_result import DrawPredictionResult

# AI服务模型
from .llm_provider import LLMProvider, LLMProviderTypeEnum, LLMProviderStatusEnum

# 日志模型
from .log_entry import LogEntry

from .user import User
from .role import Role
from .department import Department
from .log_entry import LogEntry
from .data_sources import DataSource
from .crawler_config import CrawlerConfig
from .crawler_tasks import CrawlerTask
from .headers import RequestHeader
from .ip_pool import IPPool
from .llm_provider import LLMProvider
from .multi_strategy import MultiStrategyTask  # 新增多策略任务模型

__all__ = [
    "User",
    "Role", 
    "Department",
    "LogEntry",
    "DataSource",
    "CrawlerConfig",
    "CrawlerTask",
    "RequestHeader",
    "IPPool",
    "LLMProvider",
    "MultiStrategyTask"  # 添加到导出列表
]
