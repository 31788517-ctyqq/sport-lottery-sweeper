"""
数据源管理模块端到端测试
验证数据源管理功能的完整工作流程
"""
import asyncio
import pytest
from playwright.async_api import async_playwright
import time
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 设置环境变量以使用测试配置
os.environ.setdefault('TESTING', 'True')


async def test_datasource_management_e2e():
    """
    数据源管理模块端到端测试
    验证数据源的创建、编辑、删除等功能
    """
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 设置为True可在无头模式下运行
        page = await browser.new_page()
        
        try:
            # 访问前端页面
            print("正在访问系统...")
            await page.goto("http://localhost:3000")
            
            # 登录
            print("执行登录操作...")
            await page.fill("#username", "admin")
            await page.fill("#password", "admin123")
            await page.click("button[type='submit']")
            
            # 等待登录完成
            await page.wait_for_timeout(2000)
            
            # 导航到数据源管理页面
            print("导航到数据源管理...")
            await page.click("text=数据源管理")
            await page.wait_for_timeout(1000)
            
            # 点击数据源配置子菜单
            await page.click("text=数据源配置")
            await page.wait_for_timeout(2000)
            
            # 记录初始数据源数量
            initial_count = await page.locator(".data-source-item").count()
            print(f"初始数据源数量: {initial_count}")
            
            # 点击创建数据源按钮
            print("创建新数据源...")
            await page.click("button:has-text('新增')")
            await page.wait_for_timeout(1000)
            
            # 填写数据源表单
            datasource_name = f"测试数据源_{int(time.time())}"
            await page.fill("input[placeholder='请输入数据源名称']", datasource_name)
            await page.fill("input[placeholder='请输入数据源地址']", "https://api.example.com/data")
            
            # 选择数据源类型
            await page.click("text=请选择数据源类型")
            await page.click("text=API")
            
            # 点击保存按钮
            await page.click("button:has-text('保存')")
            await page.wait_for_timeout(2000)
            
            # 验证数据源创建成功
            print("验证数据源创建...")
            new_count = await page.locator(".data-source-item").count()
            assert new_count == initial_count + 1, f"数据源数量未正确增加，期望{initial_count + 1}，实际{new_count}"
            
            # 验证新数据源出现在列表中
            datasource_exists = await page.locator(f"text={datasource_name}").is_visible()
            assert datasource_exists, f"新创建的数据源 '{datasource_name}' 未在列表中显示"
            
            # 测试编辑功能
            print("测试编辑功能...")
            # 点击编辑按钮（假设编辑按钮是第一个数据源右侧的按钮）
            await page.locator(f"text={datasource_name}").locator("..").click()  # 定位到包含文本的元素的父级
            # 然后点击编辑按钮
            edit_button = page.locator("button:has-text('编辑')").first
            await edit_button.click()
            await page.wait_for_timeout(1000)
            
            # 修改数据源名称
            updated_name = f"更新_{datasource_name}"
            await page.fill("input[placeholder='请输入数据源名称']", updated_name)
            await page.click("button:has-text('保存')")
            await page.wait_for_timeout(2000)
            
            # 验证编辑成功
            print("验证编辑结果...")
            updated_exists = await page.locator(f"text={updated_name}").is_visible()
            assert updated_exists, f"更新后的数据源名称 '{updated_name}' 未在列表中显示"
            
            # 测试删除功能
            print("测试删除功能...")
            delete_button = page.locator(f"text={updated_name}").locator("..").locator("button:has-text('删除')")
            await delete_button.click()
            await page.wait_for_timeout(500)
            
            # 确认删除
            confirm_button = page.locator("button:has-text('确认')")
            await confirm_button.click()
            await page.wait_for_timeout(2000)
            
            # 验证数据源已被删除
            final_count = await page.locator(".data-source-item").count()
            assert final_count == initial_count, f"删除后数据源数量不正确，期望{initial_count}，实际{final_count}"
            
            print("数据源管理端到端测试通过!")
            
        except Exception as e:
            print(f"测试失败: {str(e)}")
            # 截图以便调试
            await page.screenshot(path=f"datasource_e2e_test_failure_{int(time.time())}.png")
            raise e
        finally:
            await browser.close()


def run_test():
    """运行测试"""
    print("开始执行数据源管理端到端测试...")
    asyncio.run(test_datasource_management_e2e())


if __name__ == "__main__":
    run_test()