import numpy as np
from typing import Dict, Any, List
from sklearn.linear_model import LogisticRegression
import pickle
import os
from pathlib import Path


class LightweightInferenceService:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or "./models/quick_decision.pkl"
        self.model = self.load_model()
        
    def load_model(self):
        """加载预训练的轻量级模型"""
        model_path = Path(self.model_path)
        
        if model_path.exists():
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
        else:
            # 如果模型文件不存在，创建一个默认模型
            model = self.create_default_model()
            self.save_model(model)
        
        return model
    
    def create_default_model(self):
        """创建默认的轻量级模型"""
        # 这里创建一个简单的逻辑回归模型作为示例
        # 实际应用中应根据具体需求训练合适的模型
        model = LogisticRegression(max_iter=1000)
        return model
    
    def save_model(self, model):
        """保存模型到文件"""
        model_path = Path(self.model_path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
    
    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """执行轻量级推理"""
        # 确保输入数据形状正确
        if len(input_data.shape) == 1:
            input_data = input_data.reshape(1, -1)
        
        try:
            result = self.model.predict_proba(input_data)
            return result
        except Exception as e:
            # 如果预测失败，返回默认结果
            print(f"Prediction failed: {e}")
            # 返回均匀分布的预测概率作为默认值
            return np.array([[1/3, 1/3, 1/3]])  # 假设是三分类问题
    
    def batch_predict(self, input_batch: List[np.ndarray]) -> List[np.ndarray]:
        """批量推理"""
        results = []
        for input_data in input_batch:
            result = self.predict(input_data)
            results.append(result)
        return results
    
    def train_model(self, training_data: np.ndarray, labels: np.ndarray):
        """使用新数据重新训练模型"""
        self.model.fit(training_data, labels)
        self.save_model(self.model)