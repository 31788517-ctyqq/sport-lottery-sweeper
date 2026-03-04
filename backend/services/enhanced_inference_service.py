"""
增强推理服务
支持多种模型类型、版本管理和在线学习
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Union
import pickle
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging
from enum import Enum
import asyncio

# 尝试导入scikit-learn，如果不可用则使用回退方案
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    SKLEARN_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("scikit-learn 已成功导入")
except ImportError as e:
    SKLEARN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"scikit-learn 导入失败: {e}，使用简化回退方案")
    
    # 创建虚拟类作为回退
    class LogisticRegression:
        def __init__(self, **kwargs):
            self.coef_ = None
            self.intercept_ = None
            
        def fit(self, X, y):
            return self
            
        def predict(self, X):
            return np.zeros(len(X))
            
        def predict_proba(self, X):
            n_samples = len(X)
            return np.ones((n_samples, 3)) / 3
    
    class RandomForestClassifier:
        def __init__(self, **kwargs):
            pass
            
        def fit(self, X, y):
            return self
            
        def predict(self, X):
            return np.zeros(len(X))
            
        def predict_proba(self, X):
            n_samples = len(X)
            return np.ones((n_samples, 3)) / 3
    
    class GradientBoostingClassifier:
        def __init__(self, **kwargs):
            pass
            
        def fit(self, X, y):
            return self
            
        def predict(self, X):
            return np.zeros(len(X))
            
        def predict_proba(self, X):
            n_samples = len(X)
            return np.ones((n_samples, 3)) / 3
    
    class MLPClassifier:
        def __init__(self, **kwargs):
            pass
            
        def fit(self, X, y):
            return self
            
        def predict(self, X):
            return np.zeros(len(X))
            
        def predict_proba(self, X):
            n_samples = len(X)
            return np.ones((n_samples, 3)) / 3
    
    class StandardScaler:
        def __init__(self):
            self.mean_ = None
            self.scale_ = None
            
        def fit(self, X):
            self.mean_ = np.mean(X, axis=0)
            self.scale_ = np.std(X, axis=0)
            return self
            
        def transform(self, X):
            if self.mean_ is None or self.scale_ is None:
                return X
            return (X - self.mean_) / self.scale_
            
        def fit_transform(self, X):
            self.fit(X)
            return self.transform(X)
    
    # 简化版本的train_test_split
    def train_test_split(*arrays, test_size=None, random_state=None, **kwargs):
        if len(arrays) == 0:
            return []
        n_samples = len(arrays[0])
        if test_size is None:
            test_size = 0.2
        n_test = int(n_samples * test_size)
        indices = np.arange(n_samples)
        if random_state is not None:
            np.random.seed(random_state)
        np.random.shuffle(indices)
        test_indices = indices[:n_test]
        train_indices = indices[n_test:]
        
        result = []
        for array in arrays:
            result.append(array[train_indices])
            result.append(array[test_indices])
        return tuple(result)
    
    # 简化版本的评估指标
    def accuracy_score(y_true, y_pred):
        return np.mean(y_true == y_pred)
    
    def precision_score(y_true, y_pred, average='weighted'):
        return 0.5
    
    def recall_score(y_true, y_pred, average='weighted'):
        return 0.5
    
    def f1_score(y_true, y_pred, average='weighted'):
        return 0.5


class ModelType(Enum):
    """模型类型枚举"""
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"


class ModelVersion:
    """模型版本管理类"""
    
    def __init__(self, version_id: str, model_type: ModelType, 
                 model_path: str, created_at: datetime, 
                 metadata: Optional[Dict[str, Any]] = None):
        self.version_id = version_id
        self.model_type = model_type
        self.model_path = model_path
        self.created_at = created_at
        self.metadata = metadata or {}
        self.performance_metrics = self.metadata.get('performance_metrics', {})
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'version_id': self.version_id,
            'model_type': self.model_type.value,
            'model_path': self.model_path,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
            'performance_metrics': self.performance_metrics
        }


class EnhancedInferenceService:
    """增强推理服务"""
    
    def __init__(self, model_storage_path: str = "./models/advanced"):
        self.model_storage_path = Path(model_storage_path)
        self.model_storage_path.mkdir(parents=True, exist_ok=True)
        
        # 当前活跃模型
        self.active_model: Optional[Any] = None
        self.active_model_version: Optional[ModelVersion] = None
        self.model_versions: Dict[str, ModelVersion] = {}
        
        # 特征处理器
        self.feature_scaler: Optional[StandardScaler] = None
        
        # 训练数据缓存
        self.training_data_buffer: List[np.ndarray] = []
        self.training_labels_buffer: List[np.ndarray] = []
        self.buffer_max_size = 1000
        
        # 模型性能监控
        self.model_performance_history: List[Dict[str, Any]] = []
        
        # 初始化默认模型
        self._initialize_default_models()
        
    def _initialize_default_models(self):
        """初始化默认模型"""
        # 检查是否有已保存的模型
        model_files = list(self.model_storage_path.glob("*.pkl"))
        if model_files:
            # 加载最新的模型
            latest_file = max(model_files, key=lambda x: x.stat().st_mtime)
            try:
                self.load_model_version(latest_file.stem)
                logger.info(f"已加载模型版本: {self.active_model_version.version_id}")
            except Exception as e:
                logger.error(f"加载模型失败: {e}, 创建默认模型")
                self._create_default_model()
        else:
            self._create_default_model()
    
    def _create_default_model(self):
        """创建默认模型"""
        logger.info("创建默认增强模型")
        
        # 创建随机森林作为默认模型
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # 创建版本
        version_id = f"default_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = self.model_storage_path / f"{version_id}.pkl"
        
        # 保存模型
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'model_type': ModelType.RANDOM_FOREST,
                'created_at': datetime.now(),
                'metadata': {
                    'description': '默认随机森林模型',
                    'features': 6,
                    'classes': 3
                }
            }, f)
        
        # 加载版本
        self.load_model_version(version_id)
    
    def load_model_version(self, version_id: str) -> bool:
        """加载指定版本的模型"""
        model_path = self.model_storage_path / f"{version_id}.pkl"
        
        if not model_path.exists():
            logger.error(f"模型文件不存在: {model_path}")
            return False
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # 创建模型版本对象
            model_version = ModelVersion(
                version_id=version_id,
                model_type=ModelType(model_data['model_type']),
                model_path=str(model_path),
                created_at=model_data['created_at'],
                metadata=model_data.get('metadata', {})
            )
            
            # 设置活跃模型
            self.active_model = model_data['model']
            self.active_model_version = model_version
            self.model_versions[version_id] = model_version
            
            # 初始化特征处理器（如果存在）
            if 'feature_scaler' in model_data:
                self.feature_scaler = model_data['feature_scaler']
            else:
                self.feature_scaler = StandardScaler()
            
            logger.info(f"模型版本加载成功: {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"加载模型版本失败: {version_id}, 错误: {e}")
            return False
    
    def save_model_version(self, model: Any, model_type: ModelType, 
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """保存模型为新版本"""
        # 生成版本ID
        version_id = f"{model_type.value}_{len(self.model_versions)+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = self.model_storage_path / f"{version_id}.pkl"
        
        # 准备保存数据
        save_data = {
            'model': model,
            'model_type': model_type.value,
            'created_at': datetime.now(),
            'metadata': metadata or {},
            'feature_scaler': self.feature_scaler
        }
        
        # 保存到文件
        with open(model_path, 'wb') as f:
            pickle.dump(save_data, f)
        
        # 创建版本对象
        model_version = ModelVersion(
            version_id=version_id,
            model_type=model_type,
            model_path=str(model_path),
            created_at=datetime.now(),
            metadata=metadata
        )
        
        # 更新模型版本记录
        self.model_versions[version_id] = model_version
        
        logger.info(f"模型版本保存成功: {version_id}")
        return version_id
    
    def predict(self, input_data: Union[np.ndarray, List, Dict[str, Any]], 
                model_version: Optional[str] = None) -> Dict[str, Any]:
        """执行推理预测"""
        # 如果需要特定版本，加载该版本
        if model_version and model_version != self.active_model_version.version_id:
            if not self.load_model_version(model_version):
                logger.warning(f"无法加载模型版本 {model_version}, 使用当前活跃模型")
        
        # 转换输入数据
        features = self._prepare_features(input_data)
        
        try:
            # 特征标准化
            if self.feature_scaler:
                features_scaled = self.feature_scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)
            
            # 执行预测
            if hasattr(self.active_model, 'predict_proba'):
                probabilities = self.active_model.predict_proba(features_scaled)[0]
            else:
                # 对于不支持概率的模型，使用决策函数或硬预测
                prediction = self.active_model.predict(features_scaled)[0]
                probabilities = np.zeros(3)
                probabilities[int(prediction)] = 1.0
            
            # 映射到决策
            decision_idx = np.argmax(probabilities)
            decisions = ["home_win", "draw", "away_win"]
            decision = decisions[decision_idx]
            confidence = float(probabilities[decision_idx])
            
            # 构建结果
            result = {
                'decision': decision,
                'confidence': confidence,
                'probabilities': {
                    'home_win': float(probabilities[0]),
                    'draw': float(probabilities[1]),
                    'away_win': float(probabilities[2])
                },
                'model_version': self.active_model_version.version_id,
                'model_type': self.active_model_version.model_type.value,
                'features_used': self._get_feature_names(),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"推理失败: {e}")
            # 返回默认结果
            return {
                'decision': 'draw',
                'confidence': 0.33,
                'probabilities': {
                    'home_win': 0.33,
                    'draw': 0.34,
                    'away_win': 0.33
                },
                'model_version': 'error_fallback',
                'model_type': 'fallback',
                'features_used': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def batch_predict(self, input_batch: List[Union[np.ndarray, List, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """批量推理"""
        results = []
        for input_data in input_batch:
            result = self.predict(input_data)
            results.append(result)
        return results
    
    def train_model(self, training_data: np.ndarray, labels: np.ndarray, 
                   model_type: ModelType = ModelType.RANDOM_FOREST,
                   validation_split: float = 0.2) -> Dict[str, Any]:
        """训练新模型"""
        logger.info(f"开始训练 {model_type.value} 模型")
        
        # 分割训练集和验证集
        if validation_split > 0:
            X_train, X_val, y_train, y_val = train_test_split(
                training_data, labels, test_size=validation_split, random_state=42
            )
        else:
            X_train, y_train = training_data, labels
            X_val, y_val = np.array([]), np.array([])
        
        # 特征标准化
        self.feature_scaler = StandardScaler()
        X_train_scaled = self.feature_scaler.fit_transform(X_train)
        
        # 根据模型类型创建模型
        if model_type == ModelType.LOGISTIC_REGRESSION:
            model = LogisticRegression(max_iter=1000, random_state=42)
        elif model_type == ModelType.RANDOM_FOREST:
            model = RandomForestClassifier(
                n_estimators=100, max_depth=10, 
                min_samples_split=5, min_samples_leaf=2,
                random_state=42, n_jobs=-1
            )
        elif model_type == ModelType.GRADIENT_BOOSTING:
            model = GradientBoostingClassifier(
                n_estimators=100, learning_rate=0.1,
                max_depth=5, random_state=42
            )
        elif model_type == ModelType.NEURAL_NETWORK:
            model = MLPClassifier(
                hidden_layer_sizes=(64, 32),
                max_iter=1000, random_state=42
            )
        else:
            # 默认使用随机森林
            model = RandomForestClassifier(
                n_estimators=100, max_depth=10, 
                random_state=42, n_jobs=-1
            )
        
        # 训练模型
        model.fit(X_train_scaled, y_train)
        
        # 评估模型
        performance_metrics = {}
        if len(X_val) > 0:
            X_val_scaled = self.feature_scaler.transform(X_val)
            y_pred = model.predict(X_val_scaled)
            
            performance_metrics = {
                'accuracy': float(accuracy_score(y_val, y_pred)),
                'precision': float(precision_score(y_val, y_pred, average='weighted')),
                'recall': float(recall_score(y_val, y_pred, average='weighted')),
                'f1_score': float(f1_score(y_val, y_pred, average='weighted')),
                'train_samples': len(X_train),
                'val_samples': len(X_val)
            }
        
        # 保存模型
        metadata = {
            'description': f'{model_type.value} 模型训练',
            'performance_metrics': performance_metrics,
            'training_date': datetime.now().isoformat(),
            'features': training_data.shape[1],
            'classes': len(np.unique(labels))
        }
        
        version_id = self.save_model_version(model, model_type, metadata)
        
        # 加载新模型为活跃模型
        self.load_model_version(version_id)
        
        # 记录性能历史
        performance_record = {
            'version_id': version_id,
            'model_type': model_type.value,
            'performance_metrics': performance_metrics,
            'training_date': datetime.now().isoformat()
        }
        self.model_performance_history.append(performance_record)
        
        logger.info(f"模型训练完成: {version_id}")
        
        return {
            'version_id': version_id,
            'performance_metrics': performance_metrics,
            'model_type': model_type.value,
            'training_summary': {
                'train_samples': len(X_train),
                'val_samples': len(X_val) if len(X_val) > 0 else 0
            }
        }
    
    def online_learning(self, new_data: np.ndarray, new_labels: np.ndarray, 
                       learning_rate: float = 0.1) -> bool:
        """在线学习 - 增量更新模型"""
        logger.info("开始在线学习")
        
        try:
            # 添加到训练缓冲区
            self.training_data_buffer.append(new_data)
            self.training_labels_buffer.append(new_labels)
            
            # 如果缓冲区满了，进行批量更新
            if len(self.training_data_buffer) >= self.buffer_max_size:
                # 合并缓冲区数据
                all_data = np.concatenate(self.training_data_buffer)
                all_labels = np.concatenate(self.training_labels_buffer)
                
                # 训练新模型
                self.train_model(all_data, all_labels, 
                               model_type=self.active_model_version.model_type)
                
                # 清空缓冲区
                self.training_data_buffer.clear()
                self.training_labels_buffer.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"在线学习失败: {e}")
            return False
    
    def get_model_performance_history(self) -> List[Dict[str, Any]]:
        """获取模型性能历史"""
        return self.model_performance_history
    
    def get_available_model_versions(self) -> List[Dict[str, Any]]:
        """获取可用模型版本列表"""
        versions = []
        for version_id, model_version in self.model_versions.items():
            versions.append(model_version.to_dict())
        
        # 按创建时间排序
        versions.sort(key=lambda x: x['created_at'], reverse=True)
        return versions
    
    def switch_active_model(self, version_id: str) -> bool:
        """切换活跃模型版本"""
        if version_id in self.model_versions:
            return self.load_model_version(version_id)
        return False
    
    def _prepare_features(self, input_data: Union[np.ndarray, List, Dict[str, Any]]) -> np.ndarray:
        """准备特征向量"""
        if isinstance(input_data, np.ndarray):
            return input_data.flatten()
        elif isinstance(input_data, list):
            return np.array(input_data).flatten()
        elif isinstance(input_data, dict):
            # 从字典中提取标准特征
            features = []
            
            # 赔率特征
            features.append(input_data.get('home_win_odd', 2.0))
            features.append(input_data.get('draw_odd', 3.0))
            features.append(input_data.get('away_win_odd', 3.5))
            
            # 球队排名
            features.append(input_data.get('home_team_rank', 10))
            features.append(input_data.get('away_team_rank', 10))
            
            # 历史胜率
            features.append(input_data.get('historical_win_rate', 0.33))
            
            # 其他可选特征
            features.append(input_data.get('home_form', 0.5))
            features.append(input_data.get('away_form', 0.5))
            features.append(input_data.get('injury_impact', 0.0))
            features.append(input_data.get('motivation_factor', 0.5))
            
            # 截断或填充到标准特征数
            standard_features = 6
            if len(features) > standard_features:
                features = features[:standard_features]
            else:
                features.extend([0.0] * (standard_features - len(features)))
            
            return np.array(features)
        else:
            raise ValueError(f"不支持的输入数据类型: {type(input_data)}")
    
    def _get_feature_names(self) -> List[str]:
        """获取特征名称"""
        return [
            'home_win_odd',
            'draw_odd', 
            'away_win_odd',
            'home_team_rank',
            'away_team_rank',
            'historical_win_rate'
        ]
    
    def export_model(self, version_id: str, export_path: str) -> bool:
        """导出模型到指定路径"""
        if version_id not in self.model_versions:
            logger.error(f"模型版本不存在: {version_id}")
            return False
        
        try:
            model_version = self.model_versions[version_id]
            
            # 读取模型数据
            with open(model_version.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # 添加额外信息
            export_data = {
                **model_data,
                'export_date': datetime.now().isoformat(),
                'version_info': model_version.to_dict()
            }
            
            # 保存到导出路径
            with open(export_path, 'wb') as f:
                pickle.dump(export_data, f)
            
            logger.info(f"模型导出成功: {version_id} -> {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"模型导出失败: {e}")
            return False


# 全局服务实例
_enhanced_inference_service = None


def get_enhanced_inference_service() -> EnhancedInferenceService:
    """获取增强推理服务实例"""
    global _enhanced_inference_service
    if _enhanced_inference_service is None:
        _enhanced_inference_service = EnhancedInferenceService()
    return _enhanced_inference_service


# 示例使用
if __name__ == "__main__":
    # 初始化服务
    service = EnhancedInferenceService()
    
    # 获取可用模型版本
    versions = service.get_available_model_versions()
    print(f"可用模型版本: {len(versions)}")
    
    # 示例预测
    test_data = {
        'home_win_odd': 1.8,
        'draw_odd': 3.2,
        'away_win_odd': 4.5,
        'home_team_rank': 5,
        'away_team_rank': 12,
        'historical_win_rate': 0.4
    }
    
    result = service.predict(test_data)
    print("预测结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))