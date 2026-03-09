class StrategyManager:
    def __init__(self):
        self.strategies = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """注册默认策略"""
        self.register_strategy('high_probability_winning', high_probability_winning_strategy)
        self.register_strategy('balanced_odds', balanced_odds_strategy)
        self.register_strategy('recent_form', recent_form_strategy)
    
    def register_strategy(self, strategy_id, strategy_func):
        """注册筛选策略"""
        self.strategies[strategy_id] = strategy_func
    
    def execute_strategy(self, strategy_id, data):
        """执行特定策略"""
        if strategy_id not in self.strategies:
            raise ValueError(f"策略 {strategy_id} 未找到")
        return self.strategies[strategy_id](data)
    
    def get_all_strategies(self):
        """获取所有策略列表"""
        return list(self.strategies.keys())


def high_probability_winning_strategy(data):
    """高胜率策略"""
    filtered = []
    for match in data:
        # 使用数据库中的胜率字段
        home_win_prob = match.get('home_win_probability', 0)
        away_win_prob = match.get('away_win_probability', 0)
        if home_win_prob > 0.6 or away_win_prob > 0.6:
            filtered.append(match)
    return filtered


def balanced_odds_strategy(data):
    """平衡赔率策略"""
    filtered = []
    for match in data:
        home_odds = match.get('home_odds', 0)
        away_odds = match.get('away_odds', 0)
        # 检查赔率是否在合理范围内
        if home_odds and away_odds and (1.5 <= home_odds <= 3.0 or 1.5 <= away_odds <= 3.0):
            filtered.append(match)
    return filtered


def recent_form_strategy(data):
    """近期状态策略"""
    filtered = []
    for match in data:
        home_recent_form = match.get('home_recent_form', 0)
        away_recent_form = match.get('away_recent_form', 0)
        # 检查近期表现是否良好
        if home_recent_form >= 3 or away_recent_form >= 3:
            filtered.append(match)
    return filtered