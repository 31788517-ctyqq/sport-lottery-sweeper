import time
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class LLMUsageMonitor:
    """LLM使用监控器"""
    
    def __init__(self):
        self.requests_log = []
        self.provider_costs = {}  # 各提供商的成本模型
        self.daily_limits = {}    # 每日使用限额
        self.current_daily_usage = {}  # 当前每日使用量
    
    def log_request(self, provider: str, input_tokens: int, output_tokens: int, cost: float):
        """记录请求"""
        request_info = {
            'timestamp': datetime.now(),
            'provider': provider,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost
        }
        self.requests_log.append(request_info)
        
        # 更新当日使用量
        today = datetime.now().date()
        key = f"{provider}:{today}"
        if key not in self.current_daily_usage:
            self.current_daily_usage[key] = {'tokens': 0, 'cost': 0}
        
        self.current_daily_usage[key]['tokens'] += (input_tokens + output_tokens)
        self.current_daily_usage[key]['cost'] += cost
    
    def is_within_daily_limit(self, provider: str) -> bool:
        """检查是否超出每日限额"""
        today = datetime.now().date()
        key = f"{provider}:{today}"
        
        current_usage = self.current_daily_usage.get(key, {'cost': 0})
        daily_limit = self.daily_limits.get(provider, float('inf'))
        
        return current_usage['cost'] <= daily_limit
    
    def get_daily_usage(self, provider: str, date: datetime.date = None) -> Dict[str, any]:
        """获取某日使用情况"""
        if date is None:
            date = datetime.now().date()
        
        key = f"{provider}:{date}"
        return self.current_daily_usage.get(key, {'tokens': 0, 'cost': 0})
    
    def get_cost_estimate(self, provider: str, input_tokens: int, output_tokens: int) -> float:
        """估算请求成本"""
        cost_model = self.provider_costs.get(provider)
        if not cost_model:
            # 默认成本模型（示例）
            return (input_tokens * 0.00001) + (output_tokens * 0.00001)
        
        input_cost = (input_tokens / 1000) * cost_model['input_price_per_1k']
        output_cost = (output_tokens / 1000) * cost_model['output_price_per_1k']
        return input_cost + output_cost