"""
独立的对冲功能测试文件
不依赖backend目录结构，完全独立运行
"""

from datetime import datetime, timedelta
from typing import List
import json


class StandaloneHedgingConfig:
    """独立的对冲配置类"""
    def __init__(self):
        self.min_profit_rate = 0.02  # 最低利润率要求 (2%)
        self.commission_rate = 0.8   # 佣金率
        self.cost_factor = 0.2       # 成本因子


class StandaloneHedgingService:
    def __init__(self):
        self.config = StandaloneHedgingConfig()

    def calculate_hedging(self, C: float, Sc: float, Se: float) -> dict:
        """
        计算对冲方案关键指标
        :param C: 竞彩卖出金额（通常为1单位便于百分比计算）
        :param Sc: 竞彩组合赔率
        :param Se: 欧指组合赔率
        :return: 包含E(欧指投入)、R(利润)、profit_rate(利润率)的字典
        """
        E = C * (Sc - self.config.cost_factor) / Se
        R = self.config.commission_rate * C - E
        profit_rate = R / C
        
        return {
            "investment": E,
            "revenue": self.config.commission_rate * C,
            "profit": R,
            "profit_rate": profit_rate,
            "is_profitable": profit_rate >= self.config.min_profit_rate
        }

    def find_parlay_combinations(self, target_date: str) -> dict:
        """
        查找指定日期的二串一组合（使用模拟数据）
        :param target_date: 目标日期，格式为 "YYYY-MM-DD"
        :return: 包含所有符合条件的二串一组合的字典
        """
        return self._generate_mock_data(target_date)

    def _generate_mock_data(self, target_date: str) -> dict:
        """
        生成模拟对冲数据
        """
        # 解析目标日期
        base_date = datetime.strptime(target_date, "%Y-%m-%d")
        
        # 创建模拟比赛数据
        mock_matches = [
            {
                'id': 1,
                'home_team': '巴塞罗那',
                'away_team': '皇家马德里',
                'start_time': base_date.replace(hour=15, minute=0),
                'sp_value': 3.2,
                'european_odd': 3.8
            },
            {
                'id': 2,
                'home_team': '拜仁慕尼黑',
                'away_team': '多特蒙德',
                'start_time': base_date.replace(hour=17, minute=30),
                'sp_value': 2.8,
                'european_odd': 3.1
            },
            {
                'id': 3,
                'home_team': '曼城',
                'away_team': '切尔西',
                'start_time': base_date.replace(hour=20, minute=0),
                'sp_value': 2.5,
                'european_odd': 2.9
            },
            {
                'id': 4,
                'home_team': '尤文图斯',
                'away_team': 'AC米兰',
                'start_time': base_date.replace(hour=22, minute=45),
                'sp_value': 3.0,
                'european_odd': 3.5
            }
        ]
        
        # 生成模拟的二串一组合
        parlay_combinations = []
        
        for i in range(len(mock_matches)):
            for j in range(i + 1, len(mock_matches)):
                match1 = type('MockMatch1', (), mock_matches[i])()
                match2 = type('MockMatch2', (), mock_matches[j])()
                
                # 检查时间间隔是否超过1小时
                time_diff = abs((match2.start_time - match1.start_time).total_seconds())
                if time_diff < 3600:  # 小于1小时，跳过
                    continue
                
                # 计算组合赔率
                total_sp_odd = match1.sp_value * match2.sp_value
                total_european_odd = match1.european_odd * match2.european_odd
                
                # 计算对冲数据
                hedging_data = self.calculate_hedging(1000, total_sp_odd, total_european_odd)
                
                # 如果不符合利润要求，跳过
                if not hedging_data["is_profitable"]:
                    continue
                
                combination = {
                    "match1_id": match1.id,
                    "match1_home_team": match1.home_team,
                    "match1_away_team": match1.away_team,
                    "match1_start_time": match1.start_time.isoformat(),
                    "match1_sp_value": match1.sp_value,
                    "match1_european_odd": match1.european_odd,
                    "match2_id": match2.id,
                    "match2_home_team": match2.home_team,
                    "match2_away_team": match2.away_team,
                    "match2_start_time": match2.start_time.isoformat(),
                    "match2_sp_value": match2.sp_value,
                    "match2_european_odd": match2.european_odd,
                    "total_sp_odd": total_sp_odd,
                    "total_european_odd": total_european_odd,
                    "investment_amount": hedging_data["investment"],
                    "revenue_amount": hedging_data["revenue"],
                    "profit_amount": hedging_data["profit"],
                    "profit_rate": hedging_data["profit_rate"],
                    "is_profitable": hedging_data["is_profitable"]
                }
                
                parlay_combinations.append(combination)
        
        return {
            "date": target_date,
            "opportunities": parlay_combinations,
            "total_count": len(parlay_combinations)
        }


def test_standalone_hedging():
    """
    测试独立的对冲功能
    """
    try:
        # 创建对冲服务实例
        hedging_service = StandaloneHedgingService()
        
        # 测试获取默认配置
        config = hedging_service.config
        print(f"对冲配置: 最低利润率={config.min_profit_rate}, 佣金率={config.commission_rate}, 成本因子={config.cost_factor}")
        
        # 测试计算函数
        result = hedging_service.calculate_hedging(1000, 3.6, 5.0)
        print(f"对冲计算示例: 投入={result['investment']:.2f}, 收益={result['revenue']:.2f}, 利润={result['profit']:.2f}, 利润率={result['profit_rate']*100:.2f}%, 是否盈利={result['is_profitable']}")
        
        # 测试获取模拟数据
        today = datetime.now().strftime("%Y-%m-%d")
        mock_result = hedging_service.find_parlay_combinations(today)
        print(f"模拟数据测试: 日期={mock_result['date']}, 发现机会={mock_result['total_count']}个")
        
        if mock_result['opportunities']:
            first_opportunity = mock_result['opportunities'][0]
            print(f"首个机会: {first_opportunity['match1_home_team']} VS {first_opportunity['match1_away_team']} "
                  f"和 {first_opportunity['match2_home_team']} VS {first_opportunity['match2_away_team']}, "
                  f"利润={first_opportunity['profit_amount']:.2f}, 利润率={first_opportunity['profit_rate']*100:.2f}%")
        
        print("✅ 独立版对冲功能测试成功!")
        return True
        
    except Exception as e:
        print(f"❌ 独立版对冲功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_sample_response():
    """
    创建示例API响应数据，用于前端测试
    """
    service = StandaloneHedgingService()
    today = datetime.now().strftime("%Y-%m-%d")
    data = service.find_parlay_combinations(today)
    
    print("\n📋 示例API响应数据 (可用于前端测试):")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    return data


if __name__ == "__main__":
    print("🧪 开始测试独立版对冲管理功能...")
    
    success = test_standalone_hedging()
    
    if success:
        print("\n🎉 独立版对冲管理模块已成功配置并可以使用模拟数据运行!")
        
        # 创建示例数据
        create_sample_response()
        
        print("\n📋 接下来可以:")
        print("- 将此功能集成到前端页面中")
        print("- 使用示例数据结构来构建前端组件")
        print("- 在前端中模拟API响应")
        print("- 所有功能都基于模拟数据运行，不依赖复杂的后端结构")
    else:
        print("\n❌ 测试失败")