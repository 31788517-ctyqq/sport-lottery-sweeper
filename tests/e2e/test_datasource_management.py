import asyncio
from playwright.async_api import async_playwright
import pytest
import os
import time


@pytest.mark.asyncio
async def test_datasource_management():
    """测试数据源管理页面的完整工作流程"""
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 设为False以便观察测试过程
        page = await browser.new_page()
        
        # 设置超时时间
        page.set_default_timeout(30000)
        
        try:
            # 访问数据源管理页面
            print("正在访问数据源管理页面...")
            await page.goto("http://localhost:3000/admin/data-source/config")
            
            # 等待页面加载完成
            await page.wait_for_load_state('networkidle')
            
            # 检查页面标题或主要元素是否存在
            print("检查页面是否加载完成...")
            await page.wait_for_selector('text="数据源管理"', timeout=10000)
            
            # 点击新增数据源按钮
            print("点击新增数据源按钮...")
            await page.click('button:has-text("新增数据源")')
            
            # 等待对话框出现
            await page.wait_for_selector('text="新增数据源"', timeout=10000)
            
            # 填写表单字段
            print("填写表单...")
            await page.fill('input[placeholder*="请输入数据源名称"]', '测试数据源')
            await page.fill('input[placeholder*="请输入接口地址"]', 'https://api.example.com/data')
            
            # 选择内容分类
            print("选择分类...")
            await page.click('.el-select__wrapper')
            await page.click('text="比赛数据"')
            
            # 点击提交按钮
            print("点击提交按钮...")
            submit_button = page.locator('button:has-text("提交")')
            await submit_button.scroll_into_view_if_needed()
            await submit_button.click()
            
            # 等待提交完成
            await page.wait_for_timeout(2000)
            
            # 检查是否有成功提示
            success_msg = page.locator('text="创建成功"')
            if await success_msg.count() > 0:
                print("✅ 数据源创建成功!")
            else:
                print("❌ 未检测到创建成功提示")
                
            # 等待页面更新
            await page.wait_for_timeout(2000)
            
            # 检查新创建的数据源是否出现在列表中
            print("检查新创建的数据源是否出现在列表中...")
            data_source_exists = await page.locator('text="测试数据源"').count() > 0
            if data_source_exists:
                print("✅ 新创建的数据源出现在列表中")
            else:
                print("❌ 新创建的数据源未出现在列表中")
                
        except Exception as e:
            print(f"测试过程中出现错误: {str(e)}")
            # 截图以便调试
            await page.screenshot(path="datasource_management_error.png")
            raise e
        finally:
            # 关闭浏览器
            await browser.close()


@pytest.mark.asyncio
async def test_datasource_edit():
    """测试数据源编辑功能"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 访问数据源管理页面
            await page.goto("http://localhost:3000/admin/data-source/config")
            await page.wait_for_load_state('networkidle')
            
            # 等待页面加载完成
            await page.wait_for_selector('text="数据源管理"', timeout=10000)
            
            # 找到第一个编辑按钮并点击
            print("查找并点击编辑按钮...")
            edit_button = page.locator('button:has-text("编辑")').first
            await edit_button.scroll_into_view_if_needed()
            await edit_button.click()
            
            # 等待编辑对话框出现
            await page.wait_for_selector('text="编辑数据源"', timeout=10000)
            
            # 更改分类
            print("更改分类...")
            await page.click('.el-select__wrapper')
            await page.click('text="球员信息"')
            
            # 点击提交按钮
            print("点击提交按钮...")
            submit_button = page.locator('button:has-text("提交")')
            await submit_button.scroll_into_view_if_needed()
            await submit_button.click()
            
            # 等待提交完成
            await page.wait_for_timeout(2000)
            
            # 检查是否有成功提示
            success_msg = page.locator('text="更新成功"')
            if await success_msg.count() > 0:
                print("✅ 数据源更新成功!")
            else:
                print("❌ 未检测到更新成功提示")
                
        except Exception as e:
            print(f"编辑测试过程中出现错误: {str(e)}")
            await page.screenshot(path="datasource_edit_error.png")
            raise e
        finally:
            await browser.close()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_datasource_management())
    asyncio.run(test_datasource_edit())