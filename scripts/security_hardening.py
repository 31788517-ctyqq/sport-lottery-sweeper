#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全加固脚本
用于实现API速率限制、增强输入验证和安全头设置
"""

import os
import sys
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
import re
import logging
import sqlite3

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class SecurityHardening:
    """安全加固系统"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "data/sport_lottery.db"
        self.rate_limits_db = {}
        self.security_rules = {}
        self.blocked_ips = set()
        
        # 初始化安全相关的数据库表
        self.init_security_tables()
        
        # 加载默认安全规则
        self.load_default_security_rules()
    
    def init_security_tables(self):
        """初始化安全相关的数据库表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建API速率限制表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_rate_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT UNIQUE,
                    request_count INTEGER DEFAULT 0,
                    window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    blocked_until TIMESTAMP,
                    reason TEXT
                )
            """)
            
            # 创建安全事件日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    source_ip TEXT,
                    user_agent TEXT,
                    path TEXT,
                    details TEXT,
                    severity TEXT
                )
            """)
            
            # 创建IP黑名单表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ip_blacklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT UNIQUE,
                    added_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT,
                    expires_at TIMESTAMP
                )
            """)
            
            # 创建输入验证规则表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS input_validation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT,
                    param_name TEXT,
                    validation_regex TEXT,
                    error_message TEXT,
                    enabled BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("安全相关数据库表初始化完成")
        except Exception as e:
            logger.error(f"初始化安全表失败: {str(e)}")
    
    def load_default_security_rules(self):
        """加载默认安全规则"""
        self.security_rules = {
            'rate_limit': {
                'default_window': 60,  # 60秒窗口
                'default_max_requests': 100,  # 每个窗口最多100个请求
                'sensitive_max_requests': 20,  # 敏感端点每分钟最多20个请求
                'blacklist_threshold': 500  # 超过500个请求加入黑名单
            },
            'input_validation': {
                'sql_injection_patterns': [
                    r"(?i)(union\s+select|drop\s+\w+|exec\s*\(|;|--|/\*|\*/|xp_|sp_|select\b|insert\b|update\b|delete\b)",
                    r"(?i)(\bwaitfor\s+delay\b|\bshutdown\b|\balter\s+\w+)"
                ],
                'xss_patterns': [
                    r"<script[^>]*>", r"javascript:", r"on\w+\s*=", 
                    r"<iframe[^>]*>", r"<object[^>]*>", r"<embed[^>]*>"
                ],
                'path_traversal_patterns': [
                    r"\.\./", r"\.\.\\", r"%2e%2e%2f", r"%2e%2e%5c"
                ]
            },
            'blocked_ips': set(),
            'whitelist_ips': set()
        }
        
        # 加载IP黑名单
        self.load_ip_blacklist()
        
        logger.info("默认安全规则加载完成")
    
    def load_ip_blacklist(self):
        """从数据库加载IP黑名单"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT ip_address FROM ip_blacklist WHERE expires_at IS NULL OR expires_at > ?", 
                          [datetime.now()])
            blacklisted_ips = cursor.fetchall()
            
            for ip_row in blacklisted_ips:
                self.blocked_ips.add(ip_row[0])
            
            conn.close()
            logger.info(f"从数据库加载了 {len(self.blocked_ips)} 个被阻止的IP地址")
        except Exception as e:
            logger.error(f"加载IP黑名单失败: {str(e)}")
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """检查IP是否被阻止"""
        return ip_address in self.blocked_ips
    
    def add_to_blocklist(self, ip_address: str, reason: str = "", duration_hours: int = 24):
        """将IP添加到阻止列表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(hours=duration_hours)
            
            cursor.execute("""
                INSERT OR REPLACE INTO ip_blacklist (ip_address, reason, expires_at)
                VALUES (?, ?, ?)
            """, (ip_address, reason, expires_at))
            
            conn.commit()
            conn.close()
            
            self.blocked_ips.add(ip_address)
            logger.info(f"IP地址 {ip_address} 已被添加到阻止列表，原因: {reason}")
        except Exception as e:
            logger.error(f"添加IP到阻止列表失败: {str(e)}")
    
    def check_rate_limit(self, ip_address: str, endpoint: str = "/", user_id: str = None) -> tuple[bool, str]:
        """检查API速率限制"""
        try:
            # 组合键，区分不同用户
            user_key = f"{ip_address}:{user_id}" if user_id else ip_address
            
            now = datetime.now()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取或创建限制记录
            cursor.execute("""
                INSERT OR IGNORE INTO api_rate_limits (ip_address) VALUES (?)
            """, (user_key,))
            
            # 查询当前限制状态
            cursor.execute("""
                SELECT request_count, window_start, blocked_until FROM api_rate_limits 
                WHERE ip_address = ?
            """, (user_key,))
            
            result = cursor.fetchone()
            if not result:
                # 如果没有记录，创建一个
                cursor.execute("""
                    INSERT INTO api_rate_limits (ip_address, request_count, window_start)
                    VALUES (?, 1, ?)
                """, (user_key, now))
                conn.commit()
                conn.close()
                return True, "OK"
            
            request_count, window_start_str, blocked_until_str = result
            
            # 解析时间
            try:
                window_start = datetime.fromisoformat(window_start_str.replace('Z', '+00:00')) if window_start_str else now
            except ValueError:
                window_start = now
                
            blocked_until = None
            if blocked_until_str:
                try:
                    blocked_until = datetime.fromisoformat(blocked_until_str.replace('Z', '+00:00'))
                except ValueError:
                    pass
            
            # 检查是否仍在封禁期内
            if blocked_until and blocked_until > now:
                conn.close()
                return False, f"IP已被暂时封禁，直到 {blocked_until.strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 检查是否超过限制窗口
            window_duration = self.security_rules['rate_limit']['default_window']
            if (now - window_start).seconds > window_duration:
                # 重置窗口和计数
                cursor.execute("""
                    UPDATE api_rate_limits 
                    SET request_count = 1, window_start = ?, blocked_until = NULL
                    WHERE ip_address = ?
                """, (now, user_key))
                conn.commit()
                conn.close()
                return True, "OK"
            
            # 检查是否超过请求数限制
            max_requests = self.security_rules['rate_limit']['default_max_requests']
            if endpoint.startswith(('/api/v1/admin', '/api/v1/auth')):
                # 管理和认证端点更严格的限制
                max_requests = self.security_rules['rate_limit']['sensitive_max_requests']
            
            if request_count >= max_requests:
                # 检查是否需要封禁IP
                if request_count >= self.security_rules['rate_limit']['blacklist_threshold']:
                    cursor.execute("""
                        UPDATE api_rate_limits 
                        SET blocked_until = ?, reason = 'Rate limit exceeded threshold'
                        WHERE ip_address = ?
                    """, (now + timedelta(hours=24), user_key))
                    conn.commit()
                    self.add_to_blocklist(ip_address, "超过速率限制阈值")
                    conn.close()
                    return False, "请求过于频繁，IP已被暂时封禁"
                
                conn.close()
                remaining_time = window_duration - (now - window_start).seconds
                return False, f"超出速率限制，请等待 {remaining_time} 秒后再试"
            
            # 增加请求计数
            cursor.execute("""
                UPDATE api_rate_limits 
                SET request_count = request_count + 1
                WHERE ip_address = ?
            """, (user_key,))
            
            conn.commit()
            conn.close()
            return True, "OK"
            
        except Exception as e:
            logger.error(f"检查速率限制失败: {str(e)}")
            return True, "Error checking rate limit, allowing request"  # 失败时允许请求
    
    def validate_input(self, input_value: str, input_type: str = "general") -> tuple[bool, str]:
        """验证输入值的安全性"""
        if input_value is None:
            return True, "OK"
        
        input_str = str(input_value)
        
        # 根据输入类型选择验证规则
        patterns_to_check = []
        if input_type == "sql_injection":
            patterns_to_check = self.security_rules['input_validation']['sql_injection_patterns']
        elif input_type == "xss":
            patterns_to_check = self.security_rules['input_validation']['xss_patterns']
        elif input_type == "path_traversal":
            patterns_to_check = self.security_rules['input_validation']['path_traversal_patterns']
        else:
            # 一般输入，检查所有类型
            for patterns in self.security_rules['input_validation'].values():
                patterns_to_check.extend(patterns)
        
        for pattern in patterns_to_check:
            if re.search(pattern, input_str, re.IGNORECASE):
                return False, f"检测到潜在的{input_type}攻击模式"
        
        return True, "OK"
    
    def sanitize_input(self, input_value: str) -> str:
        """清理输入值"""
        if input_value is None:
            return None
        
        # 移除潜在危险字符
        sanitized = input_value
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '--', '/*', '*/']
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    def log_security_event(self, event_type: str, source_ip: str, path: str, 
                          user_agent: str = "", details: str = "", severity: str = "LOW"):
        """记录安全事件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO security_events (event_type, source_ip, path, user_agent, details, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event_type, source_ip, path, user_agent, details, severity))
            
            conn.commit()
            conn.close()
            
            logger.info(f"安全事件已记录: {event_type} from {source_ip} at {path}")
        except Exception as e:
            logger.error(f"记录安全事件失败: {str(e)}")
    
    def add_input_validation_rule(self, endpoint: str, param_name: str, 
                                 validation_regex: str, error_message: str):
        """添加输入验证规则"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO input_validation_rules (endpoint, param_name, validation_regex, error_message)
                VALUES (?, ?, ?, ?)
            """, (endpoint, param_name, validation_regex, error_message))
            
            conn.commit()
            conn.close()
            
            logger.info(f"输入验证规则已添加: {endpoint}.{param_name}")
        except Exception as e:
            logger.error(f"添加输入验证规则失败: {str(e)}")
    
    def get_validation_rules_for_endpoint(self, endpoint: str) -> List[Dict]:
        """获取特定端点的验证规则"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT param_name, validation_regex, error_message FROM input_validation_rules
                WHERE endpoint = ? AND enabled = TRUE
            """, (endpoint,))
            
            rules = []
            for row in cursor.fetchall():
                param_name, validation_regex, error_message = row
                rules.append({
                    'param_name': param_name,
                    'validation_regex': validation_regex,
                    'error_message': error_message
                })
            
            conn.close()
            return rules
        except Exception as e:
            logger.error(f"获取验证规则失败: {str(e)}")
            return []
    
    def apply_security_headers(self, response_headers: Dict) -> Dict:
        """应用安全头"""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'no-referrer-when-downgrade',
            'Access-Control-Allow-Origin': '*',  # 在生产环境中应限制为特定域名
        }
        
        # 更新传入的头部
        response_headers.update(security_headers)
        return response_headers
    
    def run_security_audit(self) -> Dict:
        """运行安全审计"""
        logger.info("开始安全审计...")
        
        audit_result = {
            'checks': {},
            'findings': [],
            'recommendations': []
        }
        
        # 检查速率限制配置
        audit_result['checks']['rate_limit_config'] = {
            'window': self.security_rules['rate_limit']['default_window'],
            'max_requests': self.security_rules['rate_limit']['default_max_requests']
        }
        
        # 检查IP黑名单大小
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ip_blacklist WHERE expires_at IS NULL OR expires_at > ?", 
                      [datetime.now()])
        blacklist_count = cursor.fetchone()[0]
        
        audit_result['checks']['blacklisted_ips'] = blacklist_count
        
        # 检查最近的安全事件
        cursor.execute("""
            SELECT event_type, COUNT(*) as count FROM security_events 
            WHERE timestamp > ? GROUP BY event_type
        """, [(datetime.now() - timedelta(days=1)).isoformat()])
        
        recent_events = cursor.fetchall()
        audit_result['checks']['recent_security_events'] = {
            event_type: count for event_type, count in recent_events
        }
        
        conn.close()
        
        # 生成发现和建议
        if blacklist_count > 50:
            audit_result['findings'].append(f"发现 {blacklist_count} 个被阻止的IP地址，可能存在攻击活动")
            audit_result['recommendations'].append("检查被阻止的IP地址，确认是否为恶意流量")
        
        if 'authentication_failed' in audit_result['checks']['recent_security_events']:
            count = audit_result['checks']['recent_security_events']['authentication_failed']
            if count > 10:
                audit_result['findings'].append(f"过去24小时内发生 {count} 次认证失败，可能存在暴力破解")
                audit_result['recommendations'].append("启用更强的认证保护机制，如验证码或锁定账户")
        
        logger.info("安全审计完成")
        return audit_result


def run_security_hardening():
    """运行安全加固"""
    print("=" * 60)
    print("安全加固系统")
    print("=" * 60)
    
    security_system = SecurityHardening()
    
    print("🔧 实施安全措施...")
    
    # 演示速率限制功能
    print("\n🔒 测试速率限制...")
    allowed, message = security_system.check_rate_limit("192.168.1.100", "/api/v1/data")
    print(f"   速率限制检查: {allowed}, 消息: {message}")
    
    # 演示输入验证功能
    print("\n🛡️  测试输入验证...")
    test_inputs = [
        ("normal_input", "general"),
        ("'; DROP TABLE users;--", "sql_injection"),
        ("<script>alert('xss')</script>", "xss")
    ]
    
    for test_input, input_type in test_inputs:
        is_valid, msg = security_system.validate_input(test_input, input_type)
        print(f"   输入 '{test_input[:20]}...' 类型'{input_type}': {is_valid}, 消息: {msg}")
    
    # 演示安全头部
    print("\n🔐 应用安全头部...")
    sample_headers = {"Content-Type": "application/json"}
    secured_headers = security_system.apply_security_headers(sample_headers)
    print(f"   应用了 {len(secured_headers)-1} 个安全头部")
    
    # 运行安全审计
    print("\n🔍 运行安全审计...")
    audit_result = security_system.run_security_audit()
    
    print(f"   安全审计完成，发现 {len(audit_result['findings'])} 个问题")
    if audit_result['findings']:
        print("   发现的问题:")
        for finding in audit_result['findings']:
            print(f"     - {finding}")
    
    print(f"\n✅ 安全加固完成!")
    print(f"🛡️  实施了速率限制、输入验证和安全头部")
    print(f"📊 安全审计已运行并生成报告")
    
    return True


if __name__ == "__main__":
    success = run_security_hardening()
    sys.exit(0 if success else 1)