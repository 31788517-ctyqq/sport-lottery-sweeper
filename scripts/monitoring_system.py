#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控和告警系统
用于监控系统健康状况并发送告警
"""

import os
import sys
import time
import json
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional
import logging
from urllib.parse import urljoin
import psutil
import subprocess


# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """系统监控类"""
    
    def __init__(self):
        self.base_url = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
        self.admin_username = os.getenv("ADMIN_USERNAME", "admin")
        self.admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        self.email_config = {
            "smtp_server": os.getenv("SMTP_SERVER", "localhost"),
            "smtp_port": int(os.getenv("SMTP_PORT", 587)),
            "sender_email": os.getenv("SENDER_EMAIL", ""),
            "sender_password": os.getenv("SENDER_PASSWORD", ""),
            "recipient_emails": os.getenv("RECIPIENT_EMAILS", "").split(",") if os.getenv("RECIPIENT_EMAILS") else []
        }
        self.thresholds = {
            "cpu_percent": float(os.getenv("CPU_THRESHOLD", 80.0)),
            "memory_percent": float(os.getenv("MEMORY_THRESHOLD", 85.0)),
            "disk_percent": float(os.getenv("DISK_THRESHOLD", 90.0)),
            "response_time_sec": float(os.getenv("RESPONSE_TIME_THRESHOLD", 5.0)),
            "api_status_codes": [200, 401, 403, 404]  # 认为正常的API状态码
        }
    
    def get_system_metrics(self) -> Dict:
        """获取系统指标"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent,
            "load_average": os.getloadavg() if os.name != 'nt' else (0, 0, 0),  # Windows不支持load average
            "process_count": len(psutil.pids()),
            "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
        }
        
        return metrics
    
    def check_api_health(self) -> Dict:
        """检查API健康状况"""
        health_info = {
            "timestamp": datetime.now().isoformat(),
            "api_health": {},
            "response_times": {},
            "errors": []
        }
        
        endpoints_to_check = [
            ("/health", "GET"),
            ("/api/v1/datasources", "GET"),
            ("/api/v1/tasks", "GET"),
            ("/api/auth/login", "POST")
        ]
        
        # 首先尝试获取认证令牌
        token = self._get_auth_token()
        
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        for endpoint, method in endpoints_to_check:
            url = urljoin(self.base_url, endpoint)
            
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                elif method == "POST":
                    if endpoint == "/api/auth/login":
                        # 登录API需要凭据
                        login_data = {
                            "username": self.admin_username,
                            "password": self.admin_password
                        }
                        response = requests.post(url, headers=headers, json=login_data, timeout=10)
                    else:
                        response = requests.post(url, headers=headers, json={}, timeout=10)
                elif method == "PUT":
                    response = requests.put(url, headers=headers, json={}, timeout=10)
                elif method == "DELETE":
                    response = requests.delete(url, headers=headers, timeout=10)
                
                response_time = time.time() - start_time
                
                health_info["api_health"][endpoint] = response.status_code
                health_info["response_times"][endpoint] = round(response_time, 2)
                
                if response.status_code >= 500:
                    health_info["errors"].append({
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "response": response.text[:200]
                    })
                    
            except requests.exceptions.RequestException as e:
                health_info["errors"].append({
                    "endpoint": endpoint,
                    "error": str(e)
                })
                health_info["api_health"][endpoint] = "ERROR"
                health_info["response_times"][endpoint] = -1
        
        return health_info
    
    def _get_auth_token(self) -> Optional[str]:
        """获取认证令牌"""
        auth_url = urljoin(self.base_url, "/api/auth/login")
        
        try:
            response = requests.post(auth_url, json={
                "username": self.admin_username,
                "password": self.admin_password
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "access_token" in data["data"]:
                    return data["data"]["access_token"]
                elif "access_token" in data:
                    return data["access_token"]
        except Exception:
            pass
        
        return None
    
    def evaluate_alerts(self, metrics: Dict, api_health: Dict) -> List[Dict]:
        """评估是否需要发送告警"""
        alerts = []
        
        # 检查系统指标
        if metrics["cpu_percent"] > self.thresholds["cpu_percent"]:
            alerts.append({
                "level": "HIGH",
                "component": "CPU",
                "message": f"CPU使用率过高: {metrics['cpu_percent']}% (阈值: {self.thresholds['cpu_percent']}%)"
            })
        
        if metrics["memory_percent"] > self.thresholds["memory_percent"]:
            alerts.append({
                "level": "HIGH", 
                "component": "Memory",
                "message": f"内存使用率过高: {metrics['memory_percent']}% (阈值: {self.thresholds['memory_percent']}%)"
            })
        
        if metrics["disk_percent"] > self.thresholds["disk_percent"]:
            alerts.append({
                "level": "HIGH",
                "component": "Disk",
                "message": f"磁盘使用率过高: {metrics['disk_percent']}% (阈值: {self.thresholds['disk_percent']}%)"
            })
        
        # 检查API响应时间
        for endpoint, response_time in api_health.get("response_times", {}).items():
            if response_time > self.thresholds["response_time_sec"]:
                alerts.append({
                    "level": "MEDIUM",
                    "component": "API",
                    "message": f"API响应时间过长 {endpoint}: {response_time}s (阈值: {self.thresholds['response_time_sec']}s)"
                })
        
        # 检查API错误
        for error in api_health.get("errors", []):
            level = "HIGH" if error.get("status_code", 0) >= 500 else "MEDIUM"
            alerts.append({
                "level": level,
                "component": "API",
                "message": f"API错误 {error.get('endpoint', 'Unknown')}: {error.get('error', error.get('status_code', 'Unknown'))}"
            })
        
        return alerts
    
    def send_alerts(self, alerts: List[Dict]):
        """发送告警"""
        if not alerts:
            return
        
        logger.warning(f"检测到 {len(alerts)} 个告警")
        
        for alert in alerts:
            logger.warning(f"[{alert['level']}] {alert['component']}: {alert['message']}")
        
        # 如果配置了邮件，发送邮件告警
        if self.email_config["recipient_emails"] and self.email_config["sender_email"]:
            self._send_email_alerts(alerts)
    
    def _send_email_alerts(self, alerts: List[Dict]):
        """发送邮件告警"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config["sender_email"]
            msg['To'] = ', '.join(self.email_config["recipient_emails"])
            msg['Subject'] = f"体育彩票扫盘系统告警 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 构建邮件正文
            body = "检测到以下系统告警：\n\n"
            for alert in alerts:
                body += f"[{alert['level']}] {alert['component']}: {alert['message']}\n"
            
            body += "\n请及时检查系统状态。"
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"])
            server.starttls()
            server.login(self.email_config["sender_email"], self.email_config["sender_password"])
            
            text = msg.as_string()
            server.sendmail(self.email_config["sender_email"], self.email_config["recipient_emails"], text)
            server.quit()
            
            logger.info(f"告警邮件已发送给: {', '.join(self.email_config['recipient_emails'])}")
        
        except Exception as e:
            logger.error(f"发送邮件告警失败: {str(e)}")
    
    def run_monitoring_cycle(self):
        """运行一次监控周期"""
        logger.info("开始监控周期...")
        
        # 获取系统指标
        metrics = self.get_system_metrics()
        logger.info(f"系统指标 - CPU: {metrics['cpu_percent']}%, 内存: {metrics['memory_percent']}%, "
                   f"磁盘: {metrics['disk_percent']}%")
        
        # 检查API健康
        api_health = self.check_api_health()
        error_count = len(api_health['errors'])
        
        if error_count > 0:
            logger.error(f"API健康检查完成，发现 {error_count} 个错误")
        else:
            logger.info(f"API健康检查完成，发现 {error_count} 个错误")
        
        # 评估告警
        alerts = self.evaluate_alerts(metrics, api_health)
        
        # 发送告警
        self.send_alerts(alerts)
        
        # 保存监控数据
        self.save_monitoring_data(metrics, api_health, alerts)
        
        logger.info("监控周期完成")
        return metrics, api_health, alerts
    
    def save_monitoring_data(self, metrics: Dict, api_health: Dict, alerts: List[Dict]):
        """保存监控数据到文件"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "api_health": api_health,
            "alerts": alerts
        }
        
        # 确保监控数据目录存在
        monitor_dir = Path("monitoring_data")
        monitor_dir.mkdir(exist_ok=True)
        
        # 保存到JSON文件
        filename = f"monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = monitor_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def run_continuous_monitoring(self, interval: int = 60):
        """运行连续监控"""
        logger.info(f"开始连续监控，间隔 {interval} 秒")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("监控已停止")
            sys.exit(0)


def run_monitoring_system():
    """运行监控系统"""
    print("=" * 60)
    print("监控和告警系统")
    print("=" * 60)
    
    monitor = SystemMonitor()
    
    print(f"监控目标: {monitor.base_url}")
    print(f"告警阈值 - CPU: {monitor.thresholds['cpu_percent']}%, "
          f"内存: {monitor.thresholds['memory_percent']}%, "
          f"响应时间: {monitor.thresholds['response_time_sec']}s")
    
    print("\n🔧 执行单次监控检查...")
    metrics, api_health, alerts = monitor.run_monitoring_cycle()
    
    print(f"\n📊 监控结果:")
    print(f"  - 系统指标: CPU {metrics['cpu_percent']}%, 内存 {metrics['memory_percent']}%, "
          f"磁盘 {metrics['disk_percent']}%")
    print(f"  - API检查: {len(api_health['api_health'])} 个端点, "
          f"{len(api_health['errors'])} 个错误")
    print(f"  - 告警数量: {len(alerts)} 个")
    
    if alerts:
        print(f"\n🚨 检测到告警:")
        for i, alert in enumerate(alerts, 1):
            print(f"  {i}. [{alert['level']}] {alert['component']}: {alert['message']}")
    else:
        print("\n✅ 系统状态正常，未检测到告警")
    
    print(f"\n💾 监控数据已保存到 monitoring_data/ 目录")
    
    # 询问是否启动连续监控
    response = input("\n是否启动连续监控? (y/N): ")
    if response.lower() == 'y':
        interval_input = input("请输入监控间隔（秒，默认60）: ")
        interval = int(interval_input) if interval_input.strip().isdigit() else 60
        print(f"\n启动连续监控，间隔 {interval} 秒...")
        print("按 Ctrl+C 停止监控")
        monitor.run_continuous_monitoring(interval)
    
    return len(alerts) == 0


if __name__ == "__main__":
    success = run_monitoring_system()
    sys.exit(0 if success else 1)