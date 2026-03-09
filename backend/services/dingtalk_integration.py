import requests
import logging

logger = logging.getLogger(__name__)


def send_dingtalk_message(webhook_url, message):
    """
    发送消息到钉钉机器人
    
    :param webhook_url: 钉钉机器人Webhook URL
    :param message: 要发送的消息内容
    :return: 是否发送成功
    """
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    
    try:
        response = requests.post(webhook_url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get('errcode') == 0:
            return True
        else:
            logger.error(f"钉钉消息发送失败: {result.get('errmsg')}")
            return False
    except Exception as e:
        logger.error(f"发送钉钉消息时出错: {str(e)}", exc_info=True)
        return False


def send_markdown_table_to_dingtalk(webhook_url, table_content):
    """
    发送Markdown表格到钉钉
    :param webhook_url: 钉钉机器人Webhook URL
    :param table_content: Markdown格式的表格内容
    :return: 是否发送成功
    """
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "多策略筛选结果",
            "text": table_content
        }
    }
    
    try:
        response = requests.post(webhook_url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get('errcode') == 0:
            return True
        else:
            logger.error(f"钉钉表格消息发送失败: {result.get('errmsg')}")
            return False
    except Exception as e:
        logger.error(f"发送钉钉表格消息时出错: {str(e)}", exc_info=True)
        return False