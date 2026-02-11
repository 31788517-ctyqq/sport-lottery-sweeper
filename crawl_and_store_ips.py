#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬取300条IP代理并存储到数据库
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.ip_fetcher_multi import MultiSourceProxyFetcher
from backend.database import SessionLocal
from backend.models.ip_pool import IPPool

def crawl_and_store_ips(target_count=300):
    """爬取指定数量的IP并存储到数据库"""
    print(f"开始爬取 {target_count} 条IP代理...")
    
    # 获取IP代理
    fetcher = MultiSourceProxyFetcher()
    proxies = []
    
    # 持续爬取直到达到目标数量或没有更多数据
    while len(proxies) < target_count:
        new_proxies = fetcher.fetch_all()
        if not new_proxies:
            break
        proxies.extend(new_proxies)
        print(f"已获取 {len(proxies)} 个代理IP...")
        
        # 防止无限循环，最多尝试3次
        if len(proxies) >= target_count or len(new_proxies) == 0:
            break
    
    # 去重
    unique_proxies = list(set(proxies))
    print(f"去重后获得 {len(unique_proxies)} 个唯一IP")
    
    # 取前target_count个
    selected_proxies = unique_proxies[:target_count]
    print(f"选择前 {len(selected_proxies)} 个IP进行存储")
    
    # 连接数据库
    db = SessionLocal()
    stored_count = 0
    
    try:
        for ip, port in selected_proxies:
            try:
                # 创建IP池记录
                ip_pool_record = IPPool(
                    ip=ip,
                    port=int(port),
                    protocol="http",
                    status="active",
                    success_count=0,
                    failure_count=0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                db.add(ip_pool_record)
                stored_count += 1
                
                # 每50条提交一次
                if stored_count % 50 == 0:
                    db.commit()
                    print(f"已存储 {stored_count} 条IP记录...")
                    
            except Exception as e:
                print(f"存储IP {ip}:{port} 失败: {e}")
                continue
        
        # 提交剩余记录
        db.commit()
        print(f"IP爬取和存储完成！总共存储了 {stored_count} 条记录")
        
    except Exception as e:
        db.rollback()
        print(f"数据库操作失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    crawl_and_store_ips(300)