#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-29T00:44:00 - 创建后端单元测试示例
"""
示例后端单元测试
"""
import pytest


def test_addition():
    """测试基本加法"""
    assert 1 + 1 == 2


def test_string_concatenation():
    """测试字符串拼接"""
    result = "hello" + " " + "world"
    assert result == "hello world"


def test_list_operations():
    """测试列表操作"""
    numbers = [1, 2, 3]
    numbers.append(4)
    assert len(numbers) == 4
    assert numbers[-1] == 4


class TestExampleClass:
    """示例测试类"""
    
    def test_class_method(self):
        """测试类方法"""
        assert True
    
    def test_with_fixture(self, example_fixture):
        """使用fixture的测试"""
        assert example_fixture == "fixture_data"


@pytest.fixture
def example_fixture():
    """示例fixture"""
    return "fixture_data"


@pytest.mark.asyncio
async def test_async_function():
    """测试异步函数"""
    result = await async_example()
    assert result == "async_data"


async def async_example():
    """示例异步函数"""
    return "async_data"


# AI_DONE: coder1 @2026-01-29T00:44:00