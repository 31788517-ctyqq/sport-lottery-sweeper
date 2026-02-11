from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from .strategy_manager import StrategyManager
from .dingtalk_integration import send_markdown_table_to_dingtalk
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.matches import FootballMatch

logger = logging.getLogger(__name__)


class MultiStrategyScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.strategy_manager = StrategyManager()
        self._register_default_strategies()
        self.scheduler.start()
        logger.info("多策略调度器已启动")

    def _register_default_strategies(self):
        """注册默认策略"""
        from .strategy_manager import (
            high_probability_winning_strategy,
            balanced_odds_strategy,
            recent_form_strategy
        )
        
        self.strategy_manager.register_strategy('high_probability_winning', high_probability_winning_strategy)
        self.strategy_manager.register_strategy('balanced_odds', balanced_odds_strategy)
        self.strategy_manager.register_strategy('recent_form', recent_form_strategy)

    def _get_latest_matches_from_db(self):
        """从100球数据库获取最新比赛数据"""
        try:
            db: Session = next(get_db())
            # 查询最近的200场比赛数据
            latest_matches = db.query(FootballMatch).order_by(FootballMatch.match_time.desc()).limit(200).all()
            
            # 将数据库模型转换为字典格式，适配策略函数
            matches_data = []
            for match in latest_matches:
                # 尝试从source_attributes中提取额外数据，如果没有则使用默认值
                source_attrs = match.source_attributes or {}
                
                match_dict = {
                    'match_id': match.match_id,
                    'league': match.league,
                    'home_team': match.home_team,
                    'away_team': match.away_team,
                    'match_time': match.match_time.isoformat() if match.match_time else None,
                    'power_diff': source_attrs.get('power_diff', 0),
                    'delta_wp': source_attrs.get('delta_wp', 0),
                    'p_level': source_attrs.get('p_level', None),
                    'power_home': source_attrs.get('power_home', 0),
                    'power_away': source_attrs.get('power_away', 0),
                    'win_pan_home': source_attrs.get('win_pan_home', 0),
                    'win_pan_away': source_attrs.get('win_pan_away', 0),
                    'home_feature': source_attrs.get('home_feature', ''),
                    'away_feature': source_attrs.get('away_feature', ''),
                    'home_win_probability': source_attrs.get('home_win_probability', 0),
                    'away_win_probability': source_attrs.get('away_win_probability', 0),
                    'home_odds': source_attrs.get('home_odds', 0),
                    'away_odds': source_attrs.get('away_odds', 0),
                    'home_recent_form': source_attrs.get('home_recent_form', 0),
                    'away_recent_form': source_attrs.get('away_recent_form', 0),
                }
                matches_data.append(match_dict)
                
            logger.info(f"从100球数据库获取到 {len(matches_data)} 条比赛数据")
            return matches_data
        except Exception as e:
            logger.error(f"从数据库获取比赛数据时出错: {str(e)}", exc_info=True)
            return []

    def add_scheduled_task(self, task_config):
        """
        添加定时筛选任务
        :param task_config: 任务配置，包含strategy_ids列表
        """
        def task_wrapper():
            try:
                # 首先获取最新的比赛数据
                latest_matches = self._get_latest_matches_from_db()
                
                if not latest_matches:
                    logger.warning("未能获取到最新的比赛数据，跳过本次策略执行")
                    return
                
                results_map = {}
                for strategy_id in task_config['strategy_ids']:
                    # 使用最新的比赛数据执行策略
                    results = self.strategy_manager.execute_strategy(strategy_id, latest_matches)
                    if results:
                        results_map[strategy_id] = results
                
                if results_map:
                    if task_config.get('message_format') == 'table':
                        table_content = self._format_results_as_table(results_map)
                        send_markdown_table_to_dingtalk(task_config['dingtalk_webhook'], table_content)
                    else:
                        message = self._format_multi_strategy_results(task_config['user_id'], results_map)
                        from .dingtalk_integration import send_dingtalk_message
                        send_dingtalk_message(task_config['dingtalk_webhook'], message)
                    logger.info(f"筛选结果已发送至钉钉: user_id={task_config['user_id']}")
                else:
                    logger.info(f"策略筛选无结果: user_id={task_config['user_id']}")
            except Exception as e:
                logger.error(f"执行筛选任务时出错: {str(e)}", exc_info=True)
        
        trigger = CronTrigger.from_crontab(task_config['cron_expression'])
        self.scheduler.add_job(
            task_wrapper, 
            trigger,
            id=f"multi_filter_task_{task_config['user_id']}",
            replace_existing=True
        )
        logger.info(f"已添加多策略定时任务: user_id={task_config['user_id']}, cron={task_config['cron_expression']}")

    def _format_multi_strategy_results(self, user_id, results_map):
        """格式化多策略筛选结果消息"""
        header = f"【多策略筛选结果】\n\n"
        content = ""
        
        for strategy_id, results in results_map.items():
            content += f"📊 {strategy_id} 策略:\n"
            content += f"共筛选出 {len(results)} 场比赛:\n"
            
            for i, match in enumerate(results[:3], 1):  # 每个策略只显示前3场
                content += (
                    f"  {i}. {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')} "
                    f"({match.get('match_time', 'N/A')})\n"
                )
            
            if len(results) > 3:
                content += f"  ... 还有{len(results)-3}场比赛\n\n"
            else:
                content += "\n"
        
        content += "完整结果请登录系统查看: http://localhost:3000/admin/beidan-filter"
        return header + content

    def _format_results_as_table(self, results_map):
        """
        将筛选结果格式化为钉钉表格消息
        :param results_map: 策略ID到结果的映射
        :return: 格式化的表格消息文本
        """
        message = "📊【多策略筛选结果表格】\n\n"
        
        for strategy_id, results in results_map.items():
            # 获取策略名称
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

    def remove_task(self, user_id):
        """移除定时任务"""
        job_id = f"multi_filter_task_{user_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"已移除多策略定时任务: {job_id}")
        except:
            logger.warning(f"尝试移除不存在的多策略定时任务: {job_id}")

    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
        logger.info("多策略调度器已关闭")