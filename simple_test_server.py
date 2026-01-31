#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极简版API测试服务器 - 不依赖外部文件
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class CrawlerAPIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        print(f"[REQUEST] GET {self.path}")
        
        # 设置响应头
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        
        # 根据路径返回不同数据
        if self.path == '/':
            response = {"message": "体育彩票扫盘系统API", "version": "1.0.0"}
        elif self.path == '/health/live':
            response = {"status": "healthy", "service": "sport-lottery-sweeper"}
        elif self.path == '/api/admin/v1/sources':
            response = {
                "code": 200,
                "message": "success",
                "data": [
                    {
                        "id": "0001",
                        "name": "500赛事抓取器",
                        "category": "football_sp_odds",
                        "createTime": "2024-01-15 10:30:00",
                        "status": "active",
                        "url": "https://www.500.com"
                    }
                ]
            }
        elif self.path == '/api/admin/v1/intelligence/data':
            response = {
                "code": 200,
                "message": "success",
                "data": {
                    "items": [
                        {
                            "id": "int_001",
                            "title": "[快讯] 英超豪门爆发激烈冲突",
                            "content": "据最新消息，英超两支豪门球队在训练中爆发激烈冲突...",
                            "category": "football_news",
                            "quality_score": 0.92,
                            "is_valid": True,
                            "source_name": "500赛事抓取器",
                            "created_at": "2024-01-15T10:30:00"
                        }
                    ],
                    "total": 1,
                    "page": 1,
                    "size": 20
                }
            }
        elif self.path == '/api/admin/v1/intelligence/stats':
            response = {
                "code": 200,
                "message": "success",
                "data": {
                    "total_count": 1250,
                    "valid_count": 1180,
                    "invalid_count": 70,
                    "quality_avg": 0.87
                }
            }
        elif self.path == '/api/admin/v1/system/health':
            response = {
                "code": 200,
                "message": "success",
                "data": {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "services": {
                        "database": "connected",
                        "cache": "connected",
                        "crawler": "running"
                    }
                }
            }
        else:
            response = {"code": 404, "message": "Not Found"}
        
        # 发送响应
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

if __name__ == '__main__':
    print("=== 启动极简API测试服务器 ===")
    print("服务地址: http://localhost:8000")
    print("按 Ctrl+C 停止服务")
    print("=" * 40)
    
    server = HTTPServer(('localhost', 8000), CrawlerAPIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.shutdown()
