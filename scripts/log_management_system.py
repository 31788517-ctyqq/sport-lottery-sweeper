#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理系统
用于实现结构化日志记录、日志分析和日志告警功能
"""

import os
import sys
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import sqlite3

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class LogManagementSystem:
    """日志管理系统"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "data/sport_lottery.db"
        self.log_dir = project_root / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建日志分析结果目录
        self.analysis_dir = self.log_dir / "analysis"
        self.analysis_dir.mkdir(exist_ok=True)
        
        # 初始化数据库表
        self.init_log_tables()
    
    def init_log_tables(self):
        """初始化日志相关的数据库表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建日志分析结果表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    log_type TEXT,
                    severity TEXT,
                    count INTEGER,
                    description TEXT
                )
            """)
            
            # 创建错误日志追踪表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_log_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    error_type TEXT,
                    error_message TEXT,
                    severity TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolution_notes TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("日志相关数据库表初始化完成")
        except Exception as e:
            logger.error(f"初始化日志表失败: {str(e)}")
    
    def collect_application_logs(self) -> List[Dict]:
        """收集应用程序日志"""
        logs = []
        
        # 搜索项目中的日志文件
        for log_file in self.log_dir.rglob("*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if line.strip():
                            # 尝试解析日志行
                            log_entry = self.parse_log_line(line.strip(), str(log_file), line_num)
                            if log_entry:
                                logs.append(log_entry)
            except Exception as e:
                logger.error(f"读取日志文件失败 {log_file}: {str(e)}")
        
        # 也检查后端main.py的日志输出
        backend_log_path = project_root / "backend" / "main.py"
        if backend_log_path.exists():
            # 检查是否有日志记录
            with open(backend_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找日志相关的代码
                log_matches = re.findall(r'logger\.(info|warning|error|debug)\(([^)]+)\)', content)
                for level, msg in log_matches:
                    logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'level': level.upper(),
                        'message': msg.strip("'\""),
                        'source': 'backend/main.py',
                        'line_number': 0
                    })
        
        logger.info(f"收集到 {len(logs)} 条日志记录")
        return logs
    
    def parse_log_line(self, line: str, source_file: str, line_number: int) -> Optional[Dict]:
        """解析日志行"""
        # 尝试匹配标准日志格式: YYYY-MM-DD HH:MM:SS,mmm - LEVEL - message
        log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.+)'
        match = re.match(log_pattern, line)
        
        if match:
            timestamp_str, level, message = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f').isoformat()
            return {
                'timestamp': timestamp,
                'level': level.upper(),
                'message': message,
                'source': source_file,
                'line_number': line_number
            }
        
        # 尝试匹配其他常见格式
        alt_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*?)[\-:\s]+(\w+)[\-:\s]+(.+)'
        match = re.match(alt_pattern, line)
        
        if match:
            timestamp_str, level, message = match.groups()
            # 标准化时间戳
            try:
                # 尝试几种不同的时间格式
                for fmt in ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        parsed_time = datetime.strptime(timestamp_str.split('.')[0], fmt)
                        timestamp = parsed_time.isoformat()
                        break
                    except ValueError:
                        continue
            except:
                timestamp = datetime.now().isoformat()
            
            return {
                'timestamp': timestamp,
                'level': level.upper(),
                'message': message,
                'source': source_file,
                'line_number': line_number
            }
        
        # 如果无法解析时间戳，则使用当前时间
        return {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': line,
            'source': source_file,
            'line_number': line_number
        }
    
    def analyze_logs(self, logs: List[Dict]) -> Dict:
        """分析日志数据"""
        logger.info("开始分析日志数据...")
        
        analysis_result = {
            'total_logs': len(logs),
            'by_level': defaultdict(int),
            'by_source': defaultdict(int),
            'errors': [],
            'warnings': [],
            'critical_issues': [],
            'time_range': {'start': None, 'end': None},
            'patterns': defaultdict(int)
        }
        
        for log in logs:
            level = log['level']
            analysis_result['by_level'][level] += 1
            analysis_result['by_source'][log['source']] += 1
            
            # 提取时间范围
            if analysis_result['time_range']['start'] is None or log['timestamp'] < analysis_result['time_range']['start']:
                analysis_result['time_range']['start'] = log['timestamp']
            if analysis_result['time_range']['end'] is None or log['timestamp'] > analysis_result['time_range']['end']:
                analysis_result['time_range']['end'] = log['timestamp']
            
            # 按级别分类
            if level == 'ERROR':
                analysis_result['errors'].append(log)
                # 检查是否是严重错误
                if any(keyword in log['message'].lower() for keyword in ['exception', 'critical', 'fatal', 'unhandled']):
                    analysis_result['critical_issues'].append(log)
            elif level == 'WARNING':
                analysis_result['warnings'].append(log)
            
            # 提取常见模式
            # 这里简化为提取错误消息的关键词
            if level in ['ERROR', 'WARNING']:
                words = log['message'].lower().split()
                for word in words[:5]:  # 只取前5个词
                    if len(word) > 3:  # 只考虑长度大于3的词
                        analysis_result['patterns'][word] += 1
        
        error_count = len(analysis_result['errors'])
        warning_count = len(analysis_result['warnings'])
        
        if error_count > 0:
            logger.error(f"日志分析完成，发现 {error_count} 个错误和 {warning_count} 个警告")
        elif warning_count > 0:
            logger.warning(f"日志分析完成，发现 {error_count} 个错误和 {warning_count} 个警告")
        else:
            logger.info(f"日志分析完成，发现 {error_count} 个错误和 {warning_count} 个警告")
        
        return analysis_result
    
    def generate_log_report(self, analysis_result: Dict) -> str:
        """生成日志分析报告"""
        report_path = self.analysis_dir / f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 日志分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**分析期间**: {analysis_result['time_range']['start']} 至 {analysis_result['time_range']['end']}\n\n")
            
            f.write(f"## 统计概览\n")
            f.write(f"- 总日志数: {analysis_result['total_logs']}\n")
            f.write(f"- 错误数: {len(analysis_result['errors'])}\n")
            f.write(f"- 警告数: {len(analysis_result['warnings'])}\n")
            f.write(f"- 严重问题: {len(analysis_result['critical_issues'])}\n\n")
            
            f.write(f"## 按级别分布\n")
            for level, count in analysis_result['by_level'].items():
                f.write(f"- {level}: {count}\n")
            f.write("\n")
            
            f.write(f"## 按来源分布\n")
            for source, count in sorted(analysis_result['by_source'].items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"- {source}: {count}\n")
            f.write("\n")
            
            if analysis_result['critical_issues']:
                f.write(f"## 严重问题详情\n")
                for i, issue in enumerate(analysis_result['critical_issues'][:10], 1):
                    f.write(f"### 问题 {i}\n")
                    f.write(f"- 时间: {issue['timestamp']}\n")
                    f.write(f"- 来源: {issue['source']}\n")
                    f.write(f"- 消息: {issue['message']}\n\n")
            
            if analysis_result['errors']:
                f.write(f"## 错误详情 (前10条)\n")
                for i, error in enumerate(analysis_result['errors'][:10], 1):
                    f.write(f"### 错误 {i}\n")
                    f.write(f"- 时间: {error['timestamp']}\n")
                    f.write(f"- 来源: {error['source']}\n")
                    f.write(f"- 消息: {error['message']}\n\n")
            
            if analysis_result['patterns']:
                f.write(f"## 常见模式\n")
                sorted_patterns = sorted(analysis_result['patterns'].items(), key=lambda x: x[1], reverse=True)
                for pattern, count in sorted_patterns[:10]:
                    f.write(f"- {pattern}: {count} 次\n")
                f.write("\n")
        
        logger.info(f"日志分析报告已生成: {report_path}")
        return str(report_path)
    
    def store_analysis_results(self, analysis_result: Dict):
        """将分析结果存储到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 插入总体统计
            cursor.execute("""
                INSERT INTO log_analysis_results (log_type, severity, count, description)
                VALUES (?, ?, ?, ?)
            """, ("TOTAL_LOGS", "INFO", analysis_result['total_logs'], "Total logs collected"))
            
            # 插入各级别的日志数量
            for level, count in analysis_result['by_level'].items():
                cursor.execute("""
                    INSERT INTO log_analysis_results (log_type, severity, count, description)
                    VALUES (?, ?, ?, ?)
                """, ("LOG_LEVEL", level, count, f"Logs with level {level}"))
            
            # 插入错误和警告
            cursor.execute("""
                INSERT INTO log_analysis_results (log_type, severity, count, description)
                VALUES (?, ?, ?, ?)
            """, ("ERRORS", "ERROR", len(analysis_result['errors']), "Total errors found"))
            
            cursor.execute("""
                INSERT INTO log_analysis_results (log_type, severity, count, description)
                VALUES (?, ?, ?, ?)
            """, ("WARNINGS", "WARNING", len(analysis_result['warnings']), "Total warnings found"))
            
            # 插入严重问题
            cursor.execute("""
                INSERT INTO log_analysis_results (log_type, severity, count, description)
                VALUES (?, ?, ?, ?)
            """, ("CRITICAL_ISSUES", "CRITICAL", len(analysis_result['critical_issues']), "Critical issues found"))
            
            conn.commit()
            conn.close()
            logger.info("日志分析结果已存储到数据库")
        except Exception as e:
            logger.error(f"存储日志分析结果失败: {str(e)}")
    
    def setup_log_alerting(self):
        """设置日志告警机制"""
        logger.info("设置日志告警机制...")
        
        # 创建告警规则配置文件
        alert_config_path = self.log_dir / "alert_config.json"
        
        default_config = {
            "rules": [
                {
                    "name": "High Error Rate",
                    "condition": "error_count > 10 in last 5 minutes",
                    "severity": "HIGH",
                    "notification_targets": ["admin@example.com"],
                    "enabled": True
                },
                {
                    "name": "Critical Issues",
                    "condition": "critical_issue detected",
                    "severity": "CRITICAL",
                    "notification_targets": ["admin@example.com", "ops-team@example.com"],
                    "enabled": True
                },
                {
                    "name": "API Response Time",
                    "condition": "response_time > 5000ms",
                    "severity": "MEDIUM",
                    "notification_targets": ["admin@example.com"],
                    "enabled": True
                }
            ],
            "alert_history_days": 30,
            "cleanup_after_days": 90
        }
        
        with open(alert_config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"告警配置已保存到: {alert_config_path}")
    
    def run_log_analysis_cycle(self):
        """运行日志分析周期"""
        logger.info("开始日志分析周期...")
        
        # 收集日志
        logs = self.collect_application_logs()
        
        if not logs:
            logger.info("未找到任何日志记录")
            return
        
        # 分析日志
        analysis_result = self.analyze_logs(logs)
        
        # 生成报告
        report_path = self.generate_log_report(analysis_result)
        
        # 存储分析结果
        self.store_analysis_results(analysis_result)
        
        # 设置告警机制
        self.setup_log_alerting()
        
        logger.info("日志分析周期完成")
        
        return {
            'logs_collected': len(logs),
            'errors_found': len(analysis_result['errors']),
            'warnings_found': len(analysis_result['warnings']),
            'report_path': report_path
        }


def run_log_management_system():
    """运行日志管理系统"""
    print("=" * 60)
    print("日志管理系统")
    print("=" * 60)
    
    log_system = LogManagementSystem()
    
    print("🔧 执行日志分析...")
    result = log_system.run_log_analysis_cycle()
    
    if result:
        print(f"\n📊 分析结果:")
        print(f"  - 收集日志数: {result['logs_collected']}")
        print(f"  - 发现错误数: {result['errors_found']}")
        print(f"  - 发现警告数: {result['warnings_found']}")
        print(f"  - 报告路径: {result['report_path']}")
    
        print(f"\n✅ 日志管理系统运行完成!")
        print(f"📁 分析报告和配置已保存到 {log_system.analysis_dir} 目录")
    else:
        print("\n⚠️  未找到任何日志进行分析")
    
    return result is not None if result else False


if __name__ == "__main__":
    success = run_log_management_system()
    sys.exit(0 if success else 1)