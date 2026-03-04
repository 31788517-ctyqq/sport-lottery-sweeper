#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Null安全工具包单元测试
"""

import unittest
import sys
import os
from typing import Dict, List, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from backend.utils.null_safety import (
    NullSafety,
    null_safe,
    safe_dict_get,
    safe_list_get,
    coalesce,
    safe_get,
    ensure_not_null
)
from backend.core.exceptions import BusinessException


class TestNullSafetyCoalesce(unittest.TestCase):
    """测试coalesce函数"""
    
    def test_coalesce_with_values(self):
        """测试有值的情况"""
        self.assertEqual(NullSafety.coalesce(None, None, "default"), "default")
        self.assertEqual(NullSafety.coalesce(None, 0, False), 0)
        self.assertEqual(NullSafety.coalesce("first", "second"), "first")
    
    def test_coalesce_all_none(self):
        """测试所有值都为None"""
        self.assertIsNone(NullSafety.coalesce(None, None, None))
    
    def test_coalesce_empty_string(self):
        """测试空字符串不被视为None"""
        self.assertEqual(NullSafety.coalesce(None, "", "default"), "")
    
    def test_coalesce_zero_value(self):
        """测试0值不被视为None"""
        self.assertEqual(NullSafety.coalesce(None, 0, "default"), 0)
    
    def test_coalesce_alias(self):
        """测试coalesce函数别名"""
        self.assertEqual(coalesce(None, "value"), "value")


class TestNullSafetySafeGet(unittest.TestCase):
    """测试safe_get函数"""
    
    def setUp(self):
        """测试数据准备"""
        self.test_data = {
            "user": {
                "profile": {
                    "name": "John",
                    "age": 30,
                    "address": {
                        "city": "New York",
                        "country": "USA"
                    }
                },
                "roles": ["admin", "user"]
            }
        }
    
    def test_safe_get_basic(self):
        """测试基础路径获取"""
        self.assertEqual(
            NullSafety.safe_get(self.test_data, "user.profile.name"),
            "John"
        )
        self.assertEqual(
            NullSafety.safe_get(self.test_data, "user.profile.age"),
            30
        )
    
    def test_safe_get_nested(self):
        """测试嵌套路径获取"""
        self.assertEqual(
            NullSafety.safe_get(self.test_data, "user.profile.address.city"),
            "New York"
        )
    
    def test_safe_get_list_index(self):
        """测试列表索引获取"""
        self.assertEqual(
            NullSafety.safe_get(self.test_data, "user.roles[0]"),
            "admin"
        )
        self.assertEqual(
            NullSafety.safe_get(self.test_data, "user.roles[1]"),
            "user"
        )
    
    def test_safe_get_none_value(self):
        """测试获取None值"""
        data = {"value": None}
        self.assertIsNone(NullSafety.safe_get(data, "value"))
        self.assertEqual(
            NullSafety.safe_get(data, "value", "default"),
            "default"
        )
    
    def test_safe_get_none_object(self):
        """测试对象为None"""
        self.assertEqual(
            NullSafety.safe_get(None, "any.path", "default"),
            "default"
        )
    
    def test_safe_get_invalid_path(self):
        """测试无效路径"""
        self.assertEqual(
            NullSafety.safe_get(self.test_data, "user.profile.invalid_key", "not_found"),
            "not_found"
        )
        self.assertEqual(
            NullSafety.safe_get(self.test_data, "user.roles[10]", "out_of_range"),
            "out_of_range"
        )
    
    def test_safe_get_with_default(self):
        """测试使用默认值"""
        self.assertEqual(
            NullSafety.safe_get(self.test_data, "user.profile.email", "no-email@example.com"),
            "no-email@example.com"
        )
    
    def test_safe_get_alias(self):
        """测试safe_get函数别名"""
        self.assertEqual(
            safe_get(self.test_data, "user.profile.name"),
            "John"
        )


class TestNullSafetyEnsureNotNull(unittest.TestCase):
    """测试ensure_not_null函数"""
    
    def test_ensure_not_null_with_value(self):
        """测试有值的情况"""
        result = NullSafety.ensure_not_null("test_value", "test_param")
        self.assertEqual(result, "test_value")
    
    def test_ensure_not_null_with_none(self):
        """测试值为None时抛出异常"""
        with self.assertRaises(BusinessException) as cm:
            NullSafety.ensure_not_null(None, "test_param")
        
        exception = cm.exception
        self.assertIn("test_param cannot be null", str(exception))
    
    def test_ensure_not_null_custom_message(self):
        """测试自定义错误消息"""
        custom_message = "Custom error message"
        with self.assertRaises(BusinessException) as cm:
            NullSafety.ensure_not_null(
                None, 
                "test_param", 
                error_message=custom_message
            )
        
        self.assertEqual(str(cm.exception), custom_message)
    
    def test_ensure_not_null_alias(self):
        """测试ensure_not_null函数别名"""
        self.assertEqual(ensure_not_null("value"), "value")


class TestNullSafetyDecorator(unittest.TestCase):
    """测试null_safe装饰器"""
    
    def test_null_safe_decorator_success(self):
        """测试装饰器正常执行"""
        
        @null_safe
        def safe_function(obj):
            return obj.name
        
        class TestObject:
            def __init__(self, name):
                self.name = name
        
        obj = TestObject("test")
        result = safe_function(obj)
        self.assertEqual(result, "test")
    
    def test_null_safe_decorator_attribute_error(self):
        """测试装饰器捕获AttributeError"""
        
        @null_safe
        def unsafe_function(obj):
            return obj.name
        
        # obj为None，访问.name会引发AttributeError
        with self.assertRaises(BusinessException) as cm:
            unsafe_function(None)
        
        exception = cm.exception
        self.assertIn("Null value encountered", str(exception))
        self.assertIn("unsafe_function", str(exception))
    
    def test_null_safe_decorator_type_error(self):
        """测试装饰器捕获TypeError"""
        
        @null_safe
        def type_error_function(obj):
            # 尝试连接字符串，如果obj为None会引发TypeError
            return "prefix_" + obj
        
        with self.assertRaises(BusinessException) as cm:
            type_error_function(None)
        
        self.assertIn("Null value encountered", str(cm.exception))


class TestNullSafetyNormalizeNull(unittest.TestCase):
    """测试normalize_null函数"""
    
    def test_normalize_null_with_value(self):
        """测试有值的情况"""
        self.assertEqual(NullSafety.normalize_null("test"), "test")
        self.assertEqual(NullSafety.normalize_null(123), 123)
        self.assertEqual(NullSafety.normalize_null([1, 2, 3]), [1, 2, 3])
    
    def test_normalize_null_none(self):
        """测试None值"""
        self.assertEqual(NullSafety.normalize_null(None), "")
        self.assertEqual(NullSafety.normalize_null(None, "default"), "default")
    
    def test_normalize_empty_string(self):
        """测试空字符串"""
        self.assertEqual(NullSafety.normalize_null(""), "")
        self.assertEqual(NullSafety.normalize_null("   "), "")
    
    def test_normalize_empty_collection(self):
        """测试空集合"""
        self.assertEqual(NullSafety.normalize_null([]), "")
        self.assertEqual(NullSafety.normalize_null({}), "")
        self.assertEqual(NullSafety.normalize_null(set()), "")
        self.assertEqual(NullSafety.normalize_null((),), "")
    
    def test_normalize_custom_default(self):
        """测试自定义默认值"""
        self.assertEqual(NullSafety.normalize_null(None, "N/A"), "N/A")
        self.assertEqual(NullSafety.normalize_null("", "empty"), "empty")


class TestSafeDictGet(unittest.TestCase):
    """测试safe_dict_get函数"""
    
    def test_safe_dict_get_existing_key(self):
        """测试存在的键"""
        data = {"key": "value"}
        self.assertEqual(safe_dict_get(data, "key"), "value")
    
    def test_safe_dict_get_missing_key(self):
        """测试不存在的键"""
        data = {"key": "value"}
        self.assertEqual(safe_dict_get(data, "missing"), None)
        self.assertEqual(safe_dict_get(data, "missing", "default"), "default")
    
    def test_safe_dict_get_none_dict(self):
        """测试字典为None"""
        self.assertEqual(safe_dict_get(None, "any_key", "default"), "default")
    
    def test_safe_dict_get_nested(self):
        """测试嵌套字典"""
        data = {"user": {"profile": {"name": "John"}}}
        # safe_dict_get不支持点分路径，只支持一级
        self.assertEqual(safe_dict_get(data, "user"), {"profile": {"name": "John"}})


class TestSafeListGet(unittest.TestCase):
    """测试safe_list_get函数"""
    
    def test_safe_list_get_valid_index(self):
        """测试有效索引"""
        data = ["a", "b", "c"]
        self.assertEqual(safe_list_get(data, 0), "a")
        self.assertEqual(safe_list_get(data, 2), "c")
    
    def test_safe_list_get_out_of_range(self):
        """测试越界索引"""
        data = ["a", "b", "c"]
        self.assertEqual(safe_list_get(data, 10), None)
        self.assertEqual(safe_list_get(data, 10, "default"), "default")
    
    def test_safe_list_get_negative_index(self):
        """测试负索引"""
        data = ["a", "b", "c"]
        self.assertEqual(safe_list_get(data, -1), "c")
        self.assertEqual(safe_list_get(data, -3), "a")
    
    def test_safe_list_get_none_list(self):
        """测试列表为None"""
        self.assertEqual(safe_list_get(None, 0, "default"), "default")
    
    def test_safe_list_get_invalid_index_type(self):
        """测试无效索引类型"""
        data = ["a", "b", "c"]
        self.assertEqual(safe_list_get(data, "invalid", "default"), "default")


class TestNullSafetySafeCall(unittest.TestCase):
    """测试safe_call函数"""
    
    def test_safe_call_success(self):
        """测试成功调用"""
        def add(a, b):
            return a + b
        
        result = NullSafety.safe_call(add, 1, 2)
        self.assertEqual(result, 3)
    
    def test_safe_call_attribute_error(self):
        """测试捕获AttributeError"""
        def bad_function(obj):
            return obj.name
        
        result = NullSafety.safe_call(bad_function, None)
        self.assertIsNone(result)
    
    def test_safe_call_type_error(self):
        """测试捕获TypeError"""
        def bad_function(obj):
            return obj + "suffix"
        
        result = NullSafety.safe_call(bad_function, None)
        self.assertIsNone(result)
    
    def test_safe_call_other_exception(self):
        """测试其他异常不被捕获"""
        def raising_function():
            raise ValueError("Intentional error")
        
        with self.assertRaises(ValueError):
            NullSafety.safe_call(raising_function)


class TestNullSafetyIntegration(unittest.TestCase):
    """测试Null安全工具包集成"""
    
    def test_chained_null_safety(self):
        """测试链式null安全操作"""
        data = {
            "users": [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": None},
                None,
                {"name": None, "age": 25}
            ]
        }
        
        # 安全获取嵌套数据
        first_user_name = safe_get(data, "users[0].name", "Unknown")
        self.assertEqual(first_user_name, "John")
        
        # 处理None值
        second_user_age = safe_get(data, "users[1].age")
        normalized_age = NullSafety.normalize_null(second_user_age, 0)
        self.assertEqual(normalized_age, 0)
        
        # 链式coalesce
        third_user_name = coalesce(
            safe_get(data, "users[2].name"),
            safe_get(data, "users[2].email"),
            "No user found"
        )
        self.assertEqual(third_user_name, "No user found")
    
    def test_real_world_scenario(self):
        """测试真实场景"""
        class User:
            def __init__(self, profile=None):
                self.profile = profile
        
        class Profile:
            def __init__(self, name=None, settings=None):
                self.name = name
                self.settings = settings
        
        # 模拟复杂对象结构
        user = User(Profile(name=None))
        
        # 安全获取，避免AttributeError
        user_name = safe_get(user, "profile.name", "Guest")
        self.assertEqual(user_name, "Guest")
        
        # 确保不为null
        with self.assertRaises(BusinessException):
            ensure_not_null(None, "user_profile")


def run_tests():
    """运行所有测试"""
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)