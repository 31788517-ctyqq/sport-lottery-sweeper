"""
动态IP代理池更新器
用于定时从89ip.cn获取最新代理IP，实现IP池的动态化
"""
import asyncio
import threading
import time
from datetime import datetime
from typing import Callable

from .ip_proxy import IPProxyPool


class DynamicProxyUpdater:
    """
    动态IP代理池更新器
    定时从89ip.cn获取最新代理IP，保持IP池的动态更新
    """
    
    def __init__(self, refresh_interval_minutes: int = 30):
        """
        初始化动态更新器
        :param refresh_interval_minutes: 刷新间隔（分钟）
        """
        self.refresh_interval = refresh_interval_minutes * 60  # 转换为秒
        # 兼容旧命名，实际使用 IPProxyPool
        self.ip_proxy_manager = IPProxyPool()
        self.stop_event = threading.Event()
        self.thread = None
        self.callback = None
        
    def set_callback(self, callback_func: Callable[[list], None]):
        """
        设置更新完成后的回调函数
        :param callback_func: 回调函数，接收更新后的代理列表作为参数
        """
        self.callback = callback_func
    
    def start(self):
        """
        启动动态更新器
        """
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print(f"[{datetime.now()}] 动态IP代理池更新器已启动，刷新间隔: {self.refresh_interval/60} 分钟")
    
    def stop(self):
        """
        停止动态更新器
        """
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        print(f"[{datetime.now()}] 动态IP代理池更新器已停止")
    
    def _run(self):
        """
        运行更新逻辑
        """
        while not self.stop_event.is_set():
            try:
                print(f"[{datetime.now()}] 开始更新IP代理池...")
                self.ip_proxy_manager.refresh_proxy_pool(count=15)  # 每次获取15个代理
                
                if self.callback:
                    self.callback(self.ip_proxy_manager.proxy_list)
                
                print(f"[{datetime.now()}] IP代理池更新完成，当前共有 {len(self.ip_proxy_manager.proxy_list)} 个有效代理")
                
                # 等待下次刷新
                for _ in range(self.refresh_interval):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"[{datetime.now()}] 更新IP代理池时发生错误: {str(e)}")
                # 等待较短时间后重试
                for _ in range(60):  # 等待1分钟
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
    
    def get_current_proxies(self) -> list:
        """
        获取当前代理列表
        :return: 当前代理列表
        """
        return self.ip_proxy_manager.proxy_list
    
    def get_random_proxy(self):
        """
        获取一个随机代理
        :return: 随机代理或None
        """
        return self.ip_proxy_manager.get_random_proxy()


# 如果直接运行此脚本，启动更新器
if __name__ == "__main__":
    updater = DynamicProxyUpdater(refresh_interval_minutes=30)
    
    def on_update(proxy_list):
        print(f"代理池已更新，当前代理数量: {len(proxy_list)}")
    
    updater.set_callback(on_update)
    updater.start()
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(10)
            # 可以随时获取当前代理池状态
            current_proxies = updater.get_current_proxies()
            print(f"[{datetime.now()}] 当前代理池大小: {len(current_proxies)}")
            
    except KeyboardInterrupt:
        print("正在停止更新器...")
        updater.stop()
