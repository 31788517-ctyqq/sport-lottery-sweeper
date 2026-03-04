from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.multi_strategy_scheduler import MultiStrategyScheduler

router = APIRouter()

# 全局调度器实例
scheduler = MultiStrategyScheduler()


@router.post("/multi-strategy/config")
def save_multi_strategy_config(config: dict, db: Session = Depends(get_db)):
    """
    保存多策略配置
    """
    try:
        # 验证必需字段
        required_fields = ['task_name', 'strategy_ids', 'cron_expression', 'user_id']
        for field in required_fields:
            if field not in config:
                return {"success": False, "message": f"缺少必需字段: {field}"}
        
        # 添加定时任务
        scheduler.add_scheduled_task(config)
        
        return {
            "success": True,
            "message": "多策略配置已保存并激活",
            "data": {"task_name": config['task_name']}
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"保存配置时出错: {str(e)}",
            "data": None
        }


@router.get("/multi-strategy/config")
def get_multi_strategy_config(user_id: str, db: Session = Depends(get_db)):
    """
    获取多策略配置
    """
    # 这里通常从数据库获取用户的配置，为了简化返回空列表
    return {
        "success": True,
        "message": "获取配置成功",
        "data": {
            "configs": [],
            "user_id": user_id
        }
    }


@router.post("/multi-strategy/execute")
def execute_multi_strategy_now(config: dict, db: Session = Depends(get_db)):
    """
    立即执行多策略筛选
    """
    try:
        # 验证必需字段
        required_fields = ['strategy_ids', 'user_id']
        for field in required_fields:
            if field not in config:
                return {"success": False, "message": f"缺少必需字段: {field}"}
        
        # 获取最新的比赛数据
        latest_matches = scheduler._get_latest_matches_from_db()
        
        if not latest_matches:
            return {
                "success": False,
                "message": "未能获取到最新的比赛数据",
                "data": None
            }
        
        # 执行策略
        from ..services.strategy_manager import StrategyManager
        strategy_manager = StrategyManager()
        
        results_map = {}
        for strategy_id in config['strategy_ids']:
            results = strategy_manager.execute_strategy(strategy_id, latest_matches)
            if results:
                results_map[strategy_id] = results
        
        # 返回结果
        return {
            "success": True,
            "message": "策略执行完成",
            "data": {
                "results_map": results_map,
                "total_strategies": len(config['strategy_ids']),
                "total_matches_found": sum(len(results) for results in results_map.values())
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"执行策略时出错: {str(e)}",
            "data": None
        }


def format_results_as_table(results_map):
    """
    将筛选结果格式化为钉钉表格消息
    :param results_map: 策略ID到结果的映射
    :return: 格式化的表格消息文本
    """
    message = "📊【多策略筛选结果表格】\n\n"
    
    for strategy_id, results in results_map.items():
        strategy_name = strategy_id  # 实际项目中应从数据库获取策略名称
        message += f"*{strategy_name}* ({strategy_id}):\n\n"
        
        # 表格头部 - 基于BeidanFilterPanel筛选结果列表的字段
        message += "| 比赛ID | 主队 | 客队 | 联赛 | 比赛时间 | ΔP | ΔWP | P级 | 主队实力 | 客队实力 | 主队赢盘 | 客队赢盘 | 主队特征 | 客队特征 |\n"
        message += "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        
        # 表格内容
        for match in results[:10]:  # 限制显示前10场比赛
            message += (
                f"| {match.get('match_id', 'N/A')} | {match.get('home_team', 'N/A')} | {match.get('away_team', 'N/A')} | {match.get('league', 'N/A')} | "
                f"{match.get('match_time', 'N/A')} | {match.get('power_diff', 'N/A')} | {match.get('delta_wp', 'N/A')} | P{match.get('p_level', 'N/A')} | "
                f"{match.get('power_home', 'N/A')} | {match.get('power_away', 'N/A')} | {match.get('win_pan_home', 'N/A')} | {match.get('win_pan_away', 'N/A')} | "
                f"{match.get('home_feature', 'N/A')} | {match.get('away_feature', 'N/A')} |\n"
            )
        
        message += "\n"
    
    message += "\n🔗 完整结果请登录系统查看: http://localhost:3000/admin/beidan-filter"
    return message


def init_app(app):
    """初始化应用，注册蓝图"""
    app.include_router(router, prefix="/api")
