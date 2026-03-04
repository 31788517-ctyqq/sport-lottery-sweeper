#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多策略筛选与钉钉通知服务
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from threading import Lock

logger = logging.getLogger(__name__)

class StrategyManager:
    def __init__(self):
        self.strategies = {}
        self._lock = Lock()
    
    def register_strategy(self, strategy_id: str, strategy_func):
        """注册筛选策略"""
        with self._lock:
            self.strategies[strategy_id] = strategy_func
            logger.info(f"策略 {strategy_id} 已注册")
    
    def execute_strategy(self, strategy_id: str, data: Dict[str, Any]):
        """执行特定策略"""
        if strategy_id not in self.strategies:
            raise ValueError(f"策略 {strategy_id} 未找到")
        logger.info(f"执行策略: {strategy_id}")
        return self.strategies[strategy_id](data)
    
    def get_all_strategies(self):
        """获取所有策略列表"""
        return list(self.strategies.keys())


def high_probability_winning_strategy(data):
    """高胜率策略 - 示例"""
    logger.info("执行高胜率策略")
    # 这里需要根据实际数据结构实现
    # 示例：筛选实力差和赢盘差在特定范围内的比赛
    filtered = []
    if 'matches' in data:
        for match in data['matches']:
            # 示例条件：实力差绝对值小于等于2，赢盘差绝对值小于等于2
            if abs(match.get('power_diff', 0)) <= 2 and abs(match.get('delta_wp', 0)) <= 2:
                filtered.append(match)
    return filtered


def balanced_odds_strategy(data):
    """平衡赔率策略 - 示例"""
    logger.info("执行平衡赔率策略")
    filtered = []
    if 'matches' in data:
        for match in data['matches']:
            # 示例条件：P级为P3或P4
            if match.get('p_level', 0) in [3, 4]:
                filtered.append(match)
    return filtered


def recent_form_strategy(data):
    """近期状态策略 - 示例"""
    logger.info("执行近期状态策略")
    filtered = []
    if 'matches' in data:
        for match in data['matches']:
            # 示例条件：稳定度大于0.6
            if match.get('stability', 0) > 0.6:
                filtered.append(match)
    return filtered


def send_dingtalk_message(webhook_url: str, message: str):
    """
    发送钉钉消息
    :param webhook_url: 钉钉机器人Webhook URL
    :param message: 消息内容
    :return: 是否发送成功
    """
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "多策略筛选结果",
            "text": message
        }
    }
    
    try:
        response = requests.post(webhook_url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('errcode') == 0:
            logger.info("钉钉消息发送成功")
            return True
        else:
            logger.error(f"钉钉消息发送失败: {result.get('errmsg')}")
            return False
    except Exception as e:
        logger.error(f"发送钉钉消息时出错: {str(e)}", exc_info=True)
        return False


def format_results_as_table(results_map: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    将筛选结果格式化为钉钉表格消息
    :param results_map: 策略ID到结果的映射
    :return: 格式化的表格消息文本
    """
    message = "📊【策略筛选场次表】\n\n"
    
    for strategy_id, results in results_map.items():
        strategy_name = strategy_id  # 可以通过映射获取更友好的名称
        message += f"**{strategy_name}** ({strategy_id}):\n\n"
        
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


class MultiStrategyScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.strategy_manager = StrategyManager()
        self._setup_default_strategies()

    def _setup_default_strategies(self):
        """设置默认策略"""
        self.strategy_manager.register_strategy('high_probability_winning', high_probability_winning_strategy)
        self.strategy_manager.register_strategy('balanced_odds', balanced_odds_strategy)
        self.strategy_manager.register_strategy('recent_form', recent_form_strategy)

    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("多策略调度器已启动")

    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("多策略调度器已关闭")

    def add_scheduled_task(self, task_config: Dict[str, Any]):
        """
        添加定时筛选任务
        :param task_config: 任务配置，包含strategy_ids列表
        """
        def task_wrapper():
            try:
                results_map = {}
                for strategy_id in task_config['strategy_ids']:
                    # 这里需要获取实际的比赛数据，暂时用空数据测试
                    data = {}  # 应该从API或数据库获取最新的比赛数据
                    results = self.strategy_manager.execute_strategy(strategy_id, data)
                    if results:
                        results_map[strategy_id] = results
                
                if results_map:
                    if task_config.get('message_format') == 'table':
                        message = format_results_as_table(results_map)
                    else:
                        message = self._format_text_results(task_config['user_id'], results_map)
                    
                    if task_config.get('dingtalk_enabled') and task_config.get('dingtalk_webhook'):
                        send_dingtalk_message(task_config['dingtalk_webhook'], message)
            except Exception as e:
                logger.error(f"执行多策略任务时出错: {str(e)}", exc_info=True)
        
        trigger = CronTrigger.from_crontab(task_config['cron_expression'])
        job_id = f"multi_filter_task_{task_config['user_id']}"
        
        # 检查是否已存在相同ID的任务，如果存在则先移除
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        self.scheduler.add_job(
            task_wrapper, 
            trigger,
            id=job_id,
            replace_existing=True
        )
        logger.info(f"定时任务已添加: {job_id}")

    def remove_scheduled_task(self, user_id: str):
        """移除定时任务"""
        job_id = f"multi_filter_task_{user_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"定时任务已移除: {job_id}")

    def _format_text_results(self, user_id: str, results_map: Dict[str, List[Dict[str, Any]]]):
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

    def execute_multiple_strategies_now(self, strategy_ids: List[str], message_format: str = 'text') -> Dict[str, Any]:
        """
        立即执行多个策略筛选
        :param strategy_ids: 策略ID列表
        :param message_format: 消息格式 ('text' 或 'table')
        :return: 各策略的筛选结果字典
        """
        results = {}
        for strategy_id in strategy_ids:
            try:
                # 获取最新的比赛数据
                data = {}  # 应该从API或数据库获取最新的比赛数据
                result = self.strategy_manager.execute_strategy(strategy_id, data)
                results[strategy_id] = result
            except Exception as e:
                logger.error(f"执行策略 {strategy_id} 时出错: {str(e)}")
                results[strategy_id] = []
        
        # 格式化结果
        if message_format == 'table':
            formatted_message = format_results_as_table(results)
        else:
            formatted_message = self._format_text_results('manual_execute', results)
        
        return {
            'results': results,
            'formatted_message': formatted_message
        }


# 创建全局实例
multi_strategy_scheduler = MultiStrategyScheduler()
# 注意：调度器启动移至main.py中，避免在模块导入时阻塞
# multi_strategy_scheduler.start()