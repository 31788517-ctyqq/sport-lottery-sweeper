# 平局预测模块开发文档

## 概述

平局预测模块是整个体育彩票扫盘系统的核心AI功能模块，旨在通过机器学习技术预测足球比赛的平局概率。本模块采用模块化设计，覆盖从数据准备到模型部署的完整ML生命周期。

### 模块目标
- 提供准确的足球比赛平局概率预测
- 支持特征工程的灵活配置和管理
- 实现模型训练、评估和调优的全流程管理
- 提供生产级的模型部署和监控能力

## 模块架构设计

### 整体架构
```
平局预测模块（总模块）
├── 1. 数据与特征管理 (Data & Feature Management)
├── 2. 模型训练与评估 (Model Training & Evaluation)
├── 3. 模型管理与部署 (Model Management & Deployment)
└── 4. 预测服务与监控 (Prediction Service & Monitoring)
```

## 1. 数据与特征管理 (Data & Feature Management)

### 1.1 功能概述
将"特征工程管理"的核心功能及其前置步骤整合，提供数据源配置、数据导入/清洗、特征生成、特征预览和管理的功能。

### 1.2 核心功能详述

#### 1.2.1 数据源配置 (Data Source Configuration)
**目标**：管理SP数据来源和相关配置

**功能清单**：
- 管理SP数据来源（爬虫、API、本地文件）
- 配置数据采集频率、规则、API密钥等
- 与数据源管理模块联动

**技术实现**：
```python
class DataSourceConfig:
    def __init__(self):
        self.sources = {
            'sp_crawler': {
                'type': 'crawler',
                'frequency': 'hourly',
                'rules': {...},
                'enabled': True
            },
            'sp_api': {
                'type': 'api',
                'endpoint': 'https://api.example.com/sp',
                'api_key': 'xxx',
                'frequency': '30min'
            },
            'local_file': {
                'type': 'file',
                'path': './data/sp_data.csv',
                'format': 'csv'
            }
        }
```

#### 1.2.2 数据导入与清洗 (Data Import & Cleaning)
**目标**：提供数据导入和清洗规则的配置管理

**功能清单**：
- 手动触发数据导入（SP数据、比赛信息、历史数据）
- 配置数据清洗规则（值范围、格式等）
- 查看清洗日志

**技术实现**：
```python
class DataCleaningManager:
    def __init__(self):
        self.cleaning_rules = {
            'sp_value_range': {'min': 1.0, 'max': 10.0},
            'match_date_format': '%Y-%m-%d %H:%M:%S',
            'team_name_normalization': True
        }
    
    async def import_data(self, source_type: str, config: dict):
        """导入指定数据源的数据"""
        pass
    
    def validate_data_quality(self, data: pd.DataFrame) -> dict:
        """验证数据质量并返回清洗报告"""
        pass
```

#### 1.2.3 特征生成 (Feature Generation)
**目标**：提供SP特征和非SP特征的生成配置

**功能清单**：
- **SP特征生成器**：
  - 选择SP数据集，配置生成SP特征的逻辑
  - 选择时间点、计算基于公司间SP差值、SP变动率等
  - 预设常用的SP特征生成模板
- **非SP特征生成器**（可选）：
  - 配置生成球队状态、历史交锋等相关特征
- **特征预览**：生成后的特征可以在此模块预览，查看特征值分布

**技术实现**：
```python
class FeatureGenerator:
    def __init__(self):
        self.sp_feature_templates = {
            'sp_difference': {
                'description': '不同博彩公司SP差值',
                'calculation': 'max(sp_values) - min(sp_values)',
                'companies': ['company_a', 'company_b', 'company_c']
            },
            'sp_change_rate': {
                'description': 'SP变动率',
                'calculation': '(current_sp - previous_sp) / previous_sp',
                'time_window': '24h'
            },
            'sp_convergence': {
                'description': 'SP收敛度',
                'calculation': 'std(sp_values)',
                'interpretation': '值越小越可能平局'
            }
        }
    
    def generate_sp_features(self, sp_data: pd.DataFrame, template: str) -> pd.DataFrame:
        """根据模板生成SP特征"""
        pass
    
    def preview_features(self, features: pd.DataFrame) -> dict:
        """预览特征分布和基本统计信息"""
        pass
```

#### 1.2.4 特征管理 (Feature Management)
**目标**：管理已生成特征的启用状态和依赖关系

**功能清单**：
- 查看已生成的特征列表（特征名称、类型、生成逻辑、状态）
- 特征的启用/禁用
- 设置特征之间的依赖关系
- （可选项）特征评分（基于简单统计分析）

**技术实现**：
```python
class FeatureManager:
    def __init__(self):
        self.features = {}
        self.feature_dependencies = {}
    
    def register_feature(self, name: str, config: dict):
        """注册新特征"""
        pass
    
    def enable_feature(self, name: str):
        """启用特征"""
        pass
    
    def get_feature_importance_score(self, feature_name: str) -> float:
        """计算特征重要性评分"""
        pass
```

### 1.3 API接口设计
```python
# RESTful API endpoints
@app.route('/api/draw-prediction/data-sources', methods=['GET', 'POST'])
def manage_data_sources():
    pass

@app.route('/api/draw-prediction/import-data', methods=['POST'])
def trigger_data_import():
    pass

@app.route('/api/draw-prediction/generate-features', methods=['POST'])
def generate_features():
    pass

@app.route('/api/draw-prediction/features', methods=['GET'])
def list_features():
    pass
```

## 2. 模型训练与评估 (Model Training & Evaluation)

### 2.1 功能概述
将"模型训练"、"模型评估与调教"的核心部分整合，管理模型的训练流程、超参数调优、以及模型性能的评估。

### 2.2 核心功能详述

#### 2.2.1 任务集管理 (Training Job Management)
**目标**：管理模型训练任务的创建和执行

**功能清单**：
- 创建新的训练任务：选择数据集、要使用的特征集、目标变量（平局）、目标模型类型（如XGBoost）
- 配置训练参数：时间序列划分设置、评估指标选择
- 启动/停止训练任务
- 查看训练任务日志

**技术实现**：
```python
class TrainingJobManager:
    def __init__(self):
        self.jobs = {}
        self.model_types = ['xgboost', 'lightgbm', 'logistic_regression', 'random_forest']
    
    def create_training_job(self, config: dict) -> str:
        """创建训练任务"""
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            'status': 'created',
            'config': config,
            'created_at': datetime.now()
        }
        return job_id
    
    async def start_training(self, job_id: str):
        """启动训练任务"""
        pass
    
    def get_training_logs(self, job_id: str) -> List[str]:
        """获取训练日志"""
        pass
```

#### 2.2.2 超参数调优 (Hyperparameter Tuning)
**目标**：自动化超参数搜索和优化

**功能清单**：
- 配置超参数搜索空间（如逻辑回归的C值范围、XGBoost的`max_depth`, `learning_rate`等）
- 选择调优算法（Grid Search, Random Search）
- 自动化执行超参数搜索，并在验证集上评估性能
- 查看调优过程和结果，找到最佳超参数组合

**技术实现**：
```python
class HyperparameterTuner:
    def __init__(self):
        self.search_methods = ['grid_search', 'random_search', 'bayesian_optimization']
    
    def configure_search_space(self, model_type: str, params: dict):
        """配置超参数搜索空间"""
        pass
    
    async def run_tuning(self, job_id: str, method: str) -> dict:
        """执行超参数调优"""
        pass
    
    def get_best_params(self, job_id: str) -> dict:
        """获取最佳参数组合"""
        pass
```

#### 2.2.3 模型评估 (Model Evaluation)
**目标**：在独立测试集上评估模型性能

**功能清单**：
- 在独立的测试集上运行已训练好的模型
- 展示评估结果：Accuracy, Precision, Recall, F1-Score, AUC, 混淆矩阵
- 可视化评估结果（如ROC曲线）

**技术实现**：
```python
class ModelEvaluator:
    def evaluate_model(self, model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
        """评估模型性能"""
        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)[:, 1]
        
        return {
            'accuracy': accuracy_score(y_test, predictions),
            'precision': precision_score(y_test, predictions),
            'recall': recall_score(y_test, predictions),
            'f1_score': f1_score(y_test, predictions),
            'auc': roc_auc_score(y_test, probabilities),
            'confusion_matrix': confusion_matrix(y_test, predictions).tolist()
        }
    
    def plot_roc_curve(self, y_test: pd.Series, y_prob: np.array):
        """绘制ROC曲线"""
        pass
```

#### 2.2.4 特征重要性分析 (Feature Importance Analysis)
**目标**：分析模型特征的重要性并提供解释

**功能清单**：
- 展示训练出的模型的特征重要性排序
- （可选项）集成SHAP值工具，提供个体预测解释

**技术实现**：
```python
class FeatureImportanceAnalyzer:
    def get_xgboost_importance(self, model) -> pd.DataFrame:
        """获取XGBoost特征重要性"""
        pass
    
    def calculate_shap_values(self, model, X_sample: pd.DataFrame):
        """计算SHAP值"""
        pass
    
    def plot_feature_importance(self, importance_df: pd.DataFrame):
        """绘制特征重要性图"""
        pass
```

### 2.3 数据库设计
```sql
-- 训练任务表
CREATE TABLE training_jobs (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    dataset_id UUID,
    feature_set_id UUID,
    config JSONB,
    status VARCHAR(20) DEFAULT 'created',
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metrics JSONB
);

-- 模型评估表
CREATE TABLE model_evaluations (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES training_jobs(id),
    accuracy DECIMAL(5,4),
    precision DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    auc DECIMAL(5,4),
    confusion_matrix JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 3. 模型管理与部署 (Model Management & Deployment)

### 3.1 功能概述
专注于已训练好的模型，对其进行版本管理、部署和发布。

### 3.2 核心功能详述

#### 3.2.1 模型库 (Model Repository)
**目标**：管理所有已完成训练的模型

**功能清单**：
- 列出所有已完成训练的模型（包括训练任务ID、使用的特征集、模型类型、训练时间、最佳超参数）
- 模型版本管理：可以保存同一模型训练的不同版本
- 模型详情查看：下载模型文件、查看详细的训练配置和评估报告

**技术实现**：
```python
class ModelRepository:
    def __init__(self):
        self.models = {}
    
    def register_model(self, model_path: str, metadata: dict):
        """注册模型到仓库"""
        pass
    
    def list_models(self, filters: dict = None) -> List[dict]:
        """列出模型"""
        pass
    
    def get_model_details(self, model_id: str) -> dict:
        """获取模型详情"""
        pass
    
    def download_model(self, model_id: str) -> bytes:
        """下载模型文件"""
        pass
```

#### 3.2.2 模型部署 (Model Deployment)
**目标**：管理模型的部署状态和A/B测试

**功能清单**：
- 选择一个或多个模型版本，将其"部署"到生产环境
- 管理部署状态：部署中、已部署、已下线
- 模型A/B测试：可以同时部署两个模型版本，并将流量分配给它们

**技术实现**：
```python
class ModelDeploymentManager:
    def __init__(self):
        self.deployments = {}
        self.ab_tests = {}
    
    def deploy_model(self, model_id: str, version: str, environment: str = 'production'):
        """部署模型"""
        pass
    
    def setup_ab_test(self, model_a_id: str, model_b_id: str, traffic_split: float):
        """设置A/B测试"""
        pass
    
    def get_deployment_status(self, deployment_id: str) -> str:
        """获取部署状态"""
        pass
```

#### 3.2.3 预测API管理 (Prediction API Management)
**目标**：管理预测API的生命周期

**功能清单**：
- 查看已部署模型的预测API端点（URL）
- （可选项）API密钥管理，用于权限控制
- （可选项）查看API的调用日志、请求量、响应时间

**技术实现**：
```python
class PredictionAPIManager:
    def __init__(self):
        self.api_keys = {}
        self.api_logs = []
    
    def generate_api_key(self, model_id: str, permissions: List[str]) -> str:
        """生成API密钥"""
        pass
    
    def log_api_request(self, endpoint: str, request_data: dict, response_time: float):
        """记录API请求日志"""
        pass
    
    def get_api_metrics(self, api_key: str) -> dict:
        """获取API使用指标"""
        pass
```

### 3.3 API接口设计
```python
# 模型管理API
@app.route('/api/models', methods=['GET'])
def list_models():
    pass

@app.route('/api/models/<model_id>/deploy', methods=['POST'])
def deploy_model(model_id):
    pass

@app.route('/api/models/<model_id>/download', methods=['GET'])
def download_model(model_id):
    pass

# 预测API
@app.route('/api/predict/draw', methods=['POST'])
def predict_draw():
    pass

@app.route('/api/predict/batch', methods=['POST'])
def batch_predict():
    pass
```

## 4. 预测服务与监控 (Prediction Service & Monitoring)

### 4.1 功能概述
专注于模型的线上运行效果和预测服务的稳定，提供在线预测功能和实时监控。

### 4.2 核心功能详述

#### 4.2.1 在线预测接口 (Online Prediction Interface)
**目标**：提供简化的在线预测界面

**功能清单**：
- 简化界面，直接输入单场比赛信息或SP值等关键特征
- 调用已部署模型进行实时预测
- 显示预测结果（平局概率）、预测标签（平局/非平局），以及预测的置信度

**技术实现**：
```python
class OnlinePredictionService:
    def __init__(self):
        self.active_model = None
    
    def predict_single_match(self, match_data: dict) -> dict:
        """单场比赛预测"""
        features = self.prepare_features(match_data)
        probability = self.active_model.predict_proba([features])[0][1]
        
        return {
            'draw_probability': float(probability),
            'prediction': 'draw' if probability > 0.5 else 'no_draw',
            'confidence': abs(probability - 0.5) * 2,
            'feature_contributions': self.explain_prediction(features)
        }
    
    def prepare_features(self, match_data: dict) -> List[float]:
        """准备预测特征"""
        pass
```

#### 4.2.2 预测结果监控 (Prediction Monitoring)
**目标**：持续监控模型预测性能

**功能清单**：
- 对比模型的预测结果与实际比赛结果，持续计算模型的评估指标
- 设置KPI阈值，当模型性能下降到一定程度时发出预警

**技术实现**：
```python
class PredictionMonitor:
    def __init__(self):
        self.kpi_thresholds = {
            'accuracy': 0.75,
            'precision': 0.70,
            'recall': 0.70,
            'f1_score': 0.70
        }
    
    def monitor_predictions(self, predictions: List[dict], actual_results: List[str]):
        """监控预测结果"""
        metrics = self.calculate_metrics(predictions, actual_results)
        
        # 检查是否触发告警
        alerts = self.check_kpi_thresholds(metrics)
        if alerts:
            self.send_alerts(alerts)
        
        return metrics
    
    def check_kpi_thresholds(self, metrics: dict) -> List[str]:
        """检查KPI阈值"""
        pass
```

#### 4.2.3 数据漂移检测 (Data Drift Detection)
**目标**：监控输入特征分布的变化

**功能清单**：
- 监控输入到在线预测服务的比赛特征分布
- 与模型训练时的数据分布进行比较
- 如果特征分布发生显著变化，发出预警

**技术实现**：
```python
class DataDriftDetector:
    def __init__(self):
        self.training_distributions = {}
    
    def detect_drift(self, current_features: pd.DataFrame) -> dict:
        """检测数据漂移"""
        drift_report = {}
        
        for column in current_features.columns:
            if column in self.training_distributions:
                drift_score = self.calculate_drift_score(
                    self.training_distributions[column],
                    current_features[column]
                )
                drift_report[column] = {
                    'drift_score': drift_score,
                    'is_drift': drift_score > 0.1  # 阈值可配置
                }
        
        return drift_report
    
    def calculate_drift_score(self, train_dist: np.array, current_dist: np.array) -> float:
        """计算漂移分数（使用KL散度或PSI）"""
        pass
```

#### 4.2.4 性能监控 (Performance Monitoring)
**目标**：监控预测API的性能指标

**功能清单**：
- 监控预测API的可用性、响应时间和错误率

**技术实现**：
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'error_count': 0,
            'total_requests': 0
        }
    
    def record_request(self, response_time: float, success: bool):
        """记录请求指标"""
        self.metrics['response_times'].append(response_time)
        self.metrics['total_requests'] += 1
        if not success:
            self.metrics['error_count'] += 1
    
    def get_performance_metrics(self) -> dict:
        """获取性能指标"""
        avg_response_time = np.mean(self.metrics['response_times'][-1000:])  # 最近1000次
        error_rate = self.metrics['error_count'] / max(self.metrics['total_requests'], 1)
        
        return {
            'avg_response_time': avg_response_time,
            'error_rate': error_rate,
            'requests_per_minute': len(self.metrics['response_times']) / max(len(self.metrics['response_times']) / 60, 1)
        }
```

## 5. 数据库设计总览

### 5.1 核心数据表
```sql
-- 特征表
CREATE TABLE features (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    generation_logic JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 特征依赖表
CREATE TABLE feature_dependencies (
    id UUID PRIMARY KEY,
    feature_id UUID REFERENCES features(id),
    depends_on_id UUID REFERENCES features(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 模型部署表
CREATE TABLE model_deployments (
    id UUID PRIMARY KEY,
    model_id UUID NOT NULL,
    version VARCHAR(50) NOT NULL,
    environment VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    deployed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 预测日志表
CREATE TABLE prediction_logs (
    id UUID PRIMARY KEY,
    model_id UUID NOT NULL,
    input_features JSONB,
    prediction_result JSONB,
    actual_result VARCHAR(20),
    prediction_time TIMESTAMP DEFAULT NOW()
);

-- 监控告警表
CREATE TABLE monitoring_alerts (
    id UUID PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 6. 开发计划与里程碑

### 6.1 Phase 1: 基础架构搭建 (Week 1-2)
- [ ] 数据库设计和建表
- [ ] 基础API框架搭建
- [ ] 数据源配置模块开发
- [ ] 数据导入清洗功能实现

### 6.2 Phase 2: 特征工程模块 (Week 3-4)
- [ ] 特征生成器开发
- [ ] 特征管理界面实现
- [ ] 特征预览和统计功能
- [ ] 特征依赖关系管理

### 6.3 Phase 3: 模型训练模块 (Week 5-6)
- [ ] 训练任务管理系统
- [ ] 超参数调优功能
- [ ] 模型评估可视化
- [ ] 特征重要性分析

### 6.4 Phase 4: 模型部署模块 (Week 7-8)
- [ ] 模型仓库管理
- [ ] 部署和A/B测试功能
- [ ] API密钥和权限管理
- [ ] 预测API开发

### 6.5 Phase 5: 监控和运维 (Week 9-10)
- [ ] 预测结果监控
- [ ] 数据漂移检测
- [ ] 性能监控系统
- [ ] 告警系统集成

## 7. 技术栈建议

### 7.1 后端技术栈
- **框架**: FastAPI (Python) - 高性能异步API框架
- **数据库**: PostgreSQL + Redis (缓存)
- **机器学习**: scikit-learn, XGBoost, LightGBM
- **数据处理**: pandas, numpy
- **模型序列化**: joblib, pickle
- **任务队列**: Celery + Redis
- **监控**: Prometheus + Grafana

### 7.2 前端技术栈
- **框架**: Vue 3 + TypeScript
- **UI组件**: Element Plus
- **图表**: ECharts
- **状态管理**: Pinia
- **HTTP客户端**: Axios

### 7.3 部署和运维
- **容器化**: Docker + Docker Compose
- **编排**: Kubernetes (可选)
- **CI/CD**: GitHub Actions
- **日志**: ELK Stack
- **监控**: Prometheus + Grafana + AlertManager

## 8. 安全和合规考虑

### 8.1 数据安全
- API访问控制和认证
- 数据传输加密 (HTTPS)
- 敏感数据脱敏处理
- 访问日志记录和审计

### 8.2 模型安全
- 模型文件完整性验证
- 预测结果合理性检查
- 异常输入检测和过滤
- 模型版本回滚机制

### 8.3 合规性
- 遵循数据保护法规 (如GDPR)
- 模型决策的公平性和可解释性
- 用户隐私保护
- 业务合规性审查

## 9. 测试和验证

### 9.1 单元测试
- 各模块核心功能测试
- 边界条件和异常处理测试
- 数据库操作测试

### 9.2 集成测试
- API接口集成测试
- 数据流端到端测试
- 模型训练和部署流程测试

### 9.3 性能测试
- API响应时间测试
- 并发处理能力测试
- 大数据量处理测试

### 9.4 模型验证
- 交叉验证和留出验证
- 业务指标验证
- 模型稳定性测试

## 10. 维护和演进

### 10.1 日常维护
- 模型性能定期评估
- 数据质量监控
- 系统健康状态检查
- 告警处理和问题解决

### 10.2 持续优化
- 特征工程持续优化
- 模型算法升级
- 系统性能调优
- 用户体验改进

### 10.3 技术演进
- 引入深度学习模型
- 实时特征计算优化
- 自动化ML流水线
- 联邦学习应用探索

---

**文档版本**: v1.0  
**创建日期**: 2026-01-21  
**作者**: AI Assistant  
**审核状态**: 待审核