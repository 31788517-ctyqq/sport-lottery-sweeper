#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统修复验证脚本
验证LLM错误修复、日志记录启用、认证配置
"""
import sys
import os
import requests
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.crud.llm_provider import llm_provider
from backend.models.user_activity import UserActivity
from backend.models.user import User

def test_llm_count():
    """测试LLM Provider计数功能"""
    print("🔍 测试LLM Provider计数功能...")
    db = SessionLocal()
    try:
        count = llm_provider.get_count(db)
        print(f"✅ LLM Provider计数成功: {count} 条记录")
        return True
    except Exception as e:
        print(f"❌ LLM Provider计数失败: {e}")
        return False
    finally:
        db.close()

def test_user_activity_logging():
    """测试用户活动日志记录"""
    print("🔍 测试用户活动日志记录...")
    db = SessionLocal()
    try:
        # 创建测试用户活动记录
        activity = UserActivity(
            user_id=1,
            activity_type="test_system_fix",
            description="系统修复验证测试",
            ip_address="127.0.0.1",
            details="{}"
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        
        # 验证记录是否成功插入
        count = db.query(UserActivity).filter(
            UserActivity.action == "test_system_fix"
        ).count()
        
        if count > 0:
            print(f"✅ 用户活动日志记录成功: {count} 条记录")
            # 清理测试数据
            db.query(UserActivity).filter(
                UserActivity.action == "test_system_fix"
            ).delete()
            db.commit()
            return True
        else:
            print("❌ 用户活动日志记录失败: 未找到测试记录")
            return False
    except Exception as e:
        print(f"❌ 用户活动日志记录异常: {e}")
        return False
    finally:
        db.close()

def test_authentication():
    """测试认证功能"""
    print("🔍 测试认证功能...")
    try:
        # 测试登录
        login_response = requests.post(
            'http://localhost:8000/api/v1/auth/login',
            json={'username': 'admin', 'password': 'admin123'},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['data']['access_token']
            print("✅ 认证登录成功")
            
            # 测试带认证的API调用
            headers = {'Authorization': f'Bearer {token}'}
            llm_response = requests.get(
                'http://localhost:8000/api/v1/llm-providers/count',
                headers=headers,
                timeout=10
            )
            
            if llm_response.status_code == 200:
                print("✅ 认证API调用成功")
                return True
            else:
                print(f"❌ 认证API调用失败: {llm_response.status_code}")
                return False
        else:
            print(f"❌ 认证登录失败: {login_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保服务已启动")
        return False
    except Exception as e:
        print(f"❌ 认证测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("🔧 系统修复验证开始")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待后端服务启动...")
    time.sleep(5)
    
    # 测试LLM错误修复
    llm_success = test_llm_count()
    print()
    
    # 测试日志记录
    log_success = test_user_activity_logging()
    print()
    
    # 测试认证
    auth_success = test_authentication()
    print()
    
    print("=" * 50)
    print("📊 验证结果总结:")
    print(f"✅ LLM错误修复: {'通过' if llm_success else '失败'}")
    print(f"✅ 日志记录启用: {'通过' if log_success else '失败'}")
    print(f"✅ 认证配置: {'通过' if auth_success else '失败'}")
    
    if llm_success and log_success and auth_success:
        print("🎉 所有修复验证通过！")
        return 0
    else:
        print("⚠️  部分验证失败，请检查相关配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())