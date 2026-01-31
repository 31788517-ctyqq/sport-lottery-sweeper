"""
调试API响应的脚本
"""
import requests
import logging
logger = logging.getLogger(__name__)
import json
from pprint import pprint


def debug_api():
    logger.debug("开始调试API响应...")
    
    try:
        # 请求近三天的比赛数据
        response = requests.get('http://localhost:8000/api/v1/public/matches/')
        
        logger.debug(f"状态码: {response.status_code}")
        logger.debug(f"响应头: {dict(response.headers)}")
        logger.debug(f"响应内容长度: {len(response.content)}")
        
        try:
            data = response.json()
            logger.debug(f"JSON解析成功，数据类型: {type(data)}")
            logger.debug(f"数据长度: {len(data) if isinstance(data, (list, str)) else 'N/A'}")
            
            if isinstance(data, list) and len(data) > 0:
                logger.debug("\n前2条数据详情:")
                for i, item in enumerate(data[:2]):
                    logger.debug(f"\n数据 {i+1}:")
                    plogger.debug(item)
            elif isinstance(data, dict):
                logger.debug("\n返回的是字典类型数据:")
                plogger.debug(data)
            else:
                logger.debug(f"\n返回的数据内容: {data}")
        except ValueError:
            logger.debug(f"JSON解析失败，原始响应内容: {response.text[:1000]}")
            
    except Exception as e:
        logger.debug(f"测试API时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_api()