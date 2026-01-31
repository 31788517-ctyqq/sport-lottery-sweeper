#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境安全检查脚本
用于检查Sport Lottery Sweeper System的安全配置
"""

import os
import sys
import hashlib
import secrets
import subprocess
from pathlib import Path

def check_secret_key_strength(secret_key):
    """检查SECRET_KEY强度"""
    if len(secret_key) < 32:
        return False, f"SECRET_KEY长度小于32位 ({len(secret_key)}位)，不够安全"
    if secret_key == "your-very-long-and-random-secret-key-here-replace-with-production-key":
        return False, "检测到默认SECRET_KEY，请修改为随机生成的密钥"
    return True, "SECRET_KEY符合安全要求"

def check_sensitive_in_code(file_path, extensions=('.py', '.js', '.ts', '.jsx', '.tsx')):
    """检查代码中是否有敏感信息"""
    sensitive_patterns = [
        'secret_key=', 'secretkey', 'password=', 'passwd=', 'pwd=', 
        'api_key=', 'apikey', 'token=', 'access_token=', 'auth_token=',
        'client_secret=', 'private_key=', 'privatekey', 'credential'
    ]
    
    issues = []
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith(extensions):
                file_path_full = os.path.join(root, file)
                try:
                    with open(file_path_full, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern in sensitive_patterns:
                            if pattern.lower() in content.lower():
                                issues.append(f"可能的敏感信息在 {file_path_full}: {pattern}")
                except Exception:
                    continue  # 跳过无法读取的文件
    return issues

def check_file_permissions(file_path):
    """检查重要文件的权限"""
    issues = []
    try:
        stat_result = os.stat(file_path)
        # 检查是否只有所有者可写
        if stat_result.st_mode & 0o777 != 0o600:
            issues.append(f"文件 {file_path} 权限过于宽松 ({oct(stat_result.st_mode & 0o777)})，建议设为600")
    except Exception as e:
        issues.append(f"无法检查 {file_path} 权限: {e}")
    return issues

def check_env_vars():
    """检查环境变量配置"""
    issues = []
    
    # 检查SECRET_KEY
    secret_key = os.getenv('SECRET_KEY') or os.getenv('JWT_SECRET_KEY')
    if secret_key:
        is_strong, msg = check_secret_key_strength(secret_key)
        if not is_strong:
            issues.append(msg)
    else:
        issues.append("未在环境变量中找到SECRET_KEY")
    
    # 检查数据库配置
    db_url = os.getenv('DATABASE_URL', '')
    if 'sqlite://' in db_url:
        issues.append("生产环境不建议使用SQLite，建议使用PostgreSQL或MySQL")
    
    # 检查DEBUG模式
    debug = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
    if debug:
        issues.append("生产环境中不应启用DEBUG模式")
    
    return issues

def check_docker_security():
    """检查Docker配置安全"""
    issues = []
    
    # 检查是否有特权模式运行的容器
    try:
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                               capture_output=True, text=True)
        containers = result.stdout.strip().split('\n') if result.stdout else []
        
        for container in containers:
            inspect_result = subprocess.run(['docker', 'inspect', container], 
                                         capture_output=True, text=True)
            if '"Privileged": true' in inspect_result.stdout:
                issues.append(f"容器 {container} 以特权模式运行，存在安全隐患")
    except Exception as e:
        issues.append(f"无法检查Docker安全配置: {e}")
    
    return issues

def main():
    """主检查函数"""
    print("🔐 Sport Lottery Sweeper System 安全检查")
    print("="*50)
    
    issues = []
    
    # 检查当前目录下的.env文件
    env_file = Path('./.env')
    if env_file.exists():
        env_issues = check_file_permissions(env_file)
        issues.extend(env_issues)
    else:
        print("⚠️  未找到.env文件")
    
    # 检查环境变量
    env_issues = check_env_vars()
    issues.extend(env_issues)
    
    # 检查代码中的敏感信息
    sensitive_issues = check_sensitive_in_code('.')
    issues.extend(sensitive_issues[:10])  # 限制输出前10个问题
    if len(sensitive_issues) > 10:
        issues.append(f"... 还有{len(sensitive_issues)-10}个潜在敏感信息问题")
    
    # 检查Docker安全配置
    try:
        docker_issues = check_docker_security()
        issues.extend(docker_issues)
    except Exception:
        # 如果Docker未安装，跳过此项检查
        pass
    
    # 输出检查结果
    if issues:
        print(f"\n🚨 发现 {len(issues)} 个安全问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n💡 建议修复措施:")
        print("  1. 使用足够长且随机的SECRET_KEY")
        print("  2. 将敏感信息存储在环境变量或安全的密钥管理系统中")
        print("  3. 生产环境禁用DEBUG模式")
        print("  4. 生产环境使用PostgreSQL或MySQL而非SQLite")
        print("  5. 限制配置文件的访问权限 (chmod 600)")
        print("  6. 不要在代码中硬编码敏感信息")
    else:
        print("\n✅ 未发现明显安全问题")
    
    print(f"\n📋 检查完成，共发现 {len(issues)} 个问题")
    return len(issues) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)