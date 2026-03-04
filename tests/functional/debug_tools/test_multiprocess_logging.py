#!/usr/bin/env python3
"""
多进程日志测试脚本
验证在多进程环境下日志系统是否能正常工作
"""
import multiprocessing
import logging
import time
from backend.utils.logging_config import setup_logging, shutdown_logging

def worker_process(worker_id):
    """工作进程函数"""
    # 每个进程都调用setup_logging（这会使用QueueHandler）
    setup_logging()
    
    logger = logging.getLogger(__name__)
    
    # 记录一些日志
    for i in range(5):
        logger.info(f"Worker {worker_id} - Log message {i}")
        time.sleep(0.1)
    
    # 不需要在每个进程中调用shutdown_logging
    # 因为QueueListener只在主进程中运行

def main():
    """主函数"""
    print("开始多进程日志测试...")
    
    # 启动日志系统
    setup_logging()
    
    # 创建多个进程
    processes = []
    for i in range(3):
        p = multiprocessing.Process(target=worker_process, args=(i,))
        processes.append(p)
        p.start()
    
    # 等待所有进程完成
    for p in processes:
        p.join()
    
    # 关闭日志系统
    shutdown_logging()
    
    print("多进程日志测试完成！")

if __name__ == "__main__":
    main()