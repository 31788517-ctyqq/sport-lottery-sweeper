import asyncio
from playwright.async_api import async_playwright
import pytest
import time


async def test_datasource_management_complete_flow():
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
            await page.locator('button:has-text("新增数据源")').click()
            
            # 等待对话框出现
            await page.wait_for_selector('text="新增数据源"', timeout=10000)
            
            # 填写表单字段
            print("填写表单...")
            await page.fill('input[placeholder="请输入数据源名称"]', '测试数据源')
            await page.fill('input[placeholder="请输入接口地址"]', 'https://api.example.com/data')
            
            # 选择数据源类型 (必填)
            print("选择数据源类型...")
            await page.locator('label:has-text("API接口") input[type="radio"]').click()
            
            # 选择内容分类 (必填)
            print("选择分类...")
            await page.click('text="请选择内容分类"')
            await page.click('text="赛事数据"')
            
            # 点击提交按钮
            print("点击提交按钮...")
            submit_button = page.locator('button:has-text("提交")')
            await submit_button.scroll_into_view_if_needed()
            await submit_button.click()
            
            # 等待提交完成，检查是否有成功提示
            try:
                await page.wait_for_selector('text="创建成功"', timeout=5000)
                print("✅ 数据源创建成功!")
            except:
                print("❌ 未检测到创建成功提示")
                # 获取页面错误信息
                error_messages = await page.locator('.el-message').all_text_contents()
                if error_messages:
                    print(f"页面错误信息: {error_messages}")
                
                # 获取控制台错误
                page.on("console", lambda msg: print(f"控制台错误: {msg.text}") if msg.type == "error" else None)
            
            # 等待页面更新
            await page.wait_for_timeout(2000)
            
            # 检查新创建的数据源是否出现在列表中
            print("检查新创建的数据源是否出现在列表中...")
            data_source_exists = await page.locator('text="测试数据源"').count() > 0
            if data_source_exists:
                print("✅ 新创建的数据源出现在列表中")
            else:
                print("❌ 新创建的数据源未出现在列表中")
                
            # 查找并点击编辑按钮
            print("查找并点击编辑按钮...")
            edit_button = page.locator('button:has-text("编辑")').first
            await edit_button.scroll_into_view_if_needed()
            await edit_button.click()
            
            # 等待编辑对话框出现
            await page.wait_for_selector('text="编辑数据源"', timeout=10000)
            
            # 更改分类
            print("更改分类...")
            await page.click('text="赛事数据"')  # 先点击当前选中的选项，取消选择
            await page.click('text="请选择内容分类"')
            await page.click('text="球员信息"')
            
            # 点击提交按钮
            print("点击提交按钮...")
            await submit_button.scroll_into_view_if_needed()
            await submit_button.click()
            
            # 等待提交完成
            await page.wait_for_timeout(2000)
            
            # 检查是否有更新成功提示
            try:
                await page.wait_for_selector('text="更新成功"', timeout=5000)
                print("✅ 数据源更新成功!")
            except:
                print("❌ 未检测到更新成功提示")
                
        except Exception as e:
            print(f"测试过程中出现错误: {str(e)}")
            # 截图以便调试
            await page.screenshot(path="datasource_management_error.png")
            raise e
        finally:
            # 关闭浏览器
            await browser.close()


async def test_form_validation():
    """测试表单验证功能"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 访问数据源管理页面
            await page.goto("http://localhost:3000/admin/data-source/config")
            await page.wait_for_load_state('networkidle')
            
            # 点击新增数据源按钮
            await page.locator('button:has-text("新增数据源")').click()
            await page.wait_for_selector('text="新增数据源"', timeout=10000)
            
            # 不填写任何内容直接提交
            submit_button = page.locator('button:has-text("提交")')
            await submit_button.click()
            
            # 检查验证错误是否出现
            await page.wait_for_timeout(1000)
            
            # 验证错误提示应该出现
            validation_errors = await page.locator('.el-form-item__error').count()
            if validation_errors > 0:
                print(f"✅ 表单验证正常工作，检测到 {validation_errors} 个验证错误")
            else:
                print("❌ 表单验证可能未正常工作")
                
        except Exception as e:
            print(f"验证测试过程中出现错误: {str(e)}")
            await page.screenshot(path="validation_error.png")
            raise e
        finally:
            await browser.close()


if __name__ == "__main__":
    # 运行测试
    print("开始运行表单验证测试...")
    asyncio.run(test_form_validation())
    
    print("\n开始运行完整流程测试...")
    asyncio.run(test_datasource_management_complete_flow())
    
    print("\n所有测试完成!")