"""
数据源管理模块端到端测试
使用Playwright测试数据源管理功能的完整工作流程
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright
import pytest
import time
import os


async def test_datasource_management_workflow():
    """
    数据源管理端到端测试流程
    验证数据源的创建、编辑、删除等功能
    """
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 设置为True可在无头模式下运行
        page = await browser.new_page()
        
        try:
            print("正在访问系统...")
            # 访问前端页面 - 使用正确的端口
            await page.goto("http://localhost:3001")
            
            # 等待页面加载
            await page.wait_for_selector("text=登录", timeout=10000)
            print("页面加载成功")
            
            # 登录
            print("执行登录操作...")
            # 尝试多种可能的输入框选择器
            try:
                await page.fill("[placeholder='请输入用户名']", "admin")
                await page.fill("[placeholder='请输入密码']", "admin123")
            except:
                # 如果上面的选择器失败，尝试其他可能的选择器
                try:
                    await page.fill("input#username", "admin")
                    await page.fill("input#password", "admin123")
                except:
                    # 再尝试其他选择器
                    await page.fill("input[type='text']", "admin")
                    await page.fill("input[type='password']", "admin123")
            
            # 点击登录按钮 - 尝试多种可能的选择器
            try:
                await page.click("button:has-text('登录')")
            except:
                try:
                    await page.click("button[type='submit']")
                except:
                    await page.click("button:has-text('登 录')")
            
            # 等待登录完成
            await page.wait_for_timeout(5000)
            
            # 验证登录成功 - 尝试多种可能的元素
            login_success = False
            try:
                login_success = await page.locator("text=首页").is_visible() or await page.locator("text=欢迎").is_visible()
            except:
                pass
                
            if not login_success:
                try:
                    login_success = await page.locator("text=数据源管理").is_visible()
                except:
                    pass
                    
            if not login_success:
                try:
                    login_success = await page.locator("text=admin").is_visible()
                except:
                    pass
                    
            assert login_success, "登录失败"
            print("登录成功")
            
            # 导航到数据源管理页面
            print("导航到数据源管理...")
            await page.click("text=数据源管理")
            await page.wait_for_timeout(1000)
            
            # 点击数据源配置子菜单
            await page.click("text=数据源配置")
            await page.wait_for_timeout(2000)
            
            # 等待数据源列表加载
            try:
                await page.wait_for_selector(".el-table__row", timeout=10000)
            except:
                # 尝试其他可能的选择器
                await page.wait_for_selector("tr", timeout=10000)
            print("进入数据源配置页面")
            
            # 记录初始数据源数量
            try:
                initial_rows = await page.locator(".el-table__row").count()
            except:
                initial_rows = await page.locator("tr").count() - 1  # 减去表头
            print(f"初始数据源数量: {initial_rows}")
            
            # 点击创建数据源按钮
            print("创建新数据源...")
            # 尝试多种可能的按钮选择器
            try:
                await page.click("button:has-text('新增数据源')")
            except:
                try:
                    await page.click("button:has-text('新增')")
                except:
                    await page.locator("button").nth(0).click()  # 尝试第一个按钮
            
            await page.wait_for_timeout(1000)
            
            # 等待模态框打开
            await page.wait_for_selector("text=新增数据源", timeout=10000)
            print("新增数据源窗口已打开")
            
            # 填写数据源表单
            datasource_name = f"测试API数据源_{int(time.time())}"
            try:
                await page.fill("input[placeholder='请输入数据源名称']", datasource_name)
            except:
                # 尝试其他可能的输入框选择器
                input_elements = await page.locator("input").all()
                for input_elem in input_elements:
                    placeholder = await input_elem.get_attribute("placeholder")
                    if placeholder and "数据源名称" in placeholder:
                        await input_elem.fill(datasource_name)
                        break
            
            try:
                await page.fill("input[placeholder='请输入数据源地址']", f"https://api.example.com/test/{int(time.time())}")
            except:
                # 尝试其他可能的输入框选择器
                input_elements = await page.locator("input").all()
                for input_elem in input_elements:
                    placeholder = await input_elem.get_attribute("placeholder")
                    if placeholder and "数据源地址" in placeholder:
                        await input_elem.fill(f"https://api.example.com/test/{int(time.time())}")
                        break
            
            # 选择数据源类型
            try:
                await page.click("label:has-text('API')")
            except:
                # 尝试其他选择器
                radios = await page.locator("input[type='radio']").all()
                for radio in radios:
                    value = await radio.get_attribute("value")
                    if value and ("api" in value.lower() or "API" in value):
                        await radio.click()
                        break
            
            # 点击保存按钮
            try:
                await page.click("button:has-text('保存')")
            except:
                # 尝试其他可能的按钮
                await page.locator("button:has-text('确 定')").click()
            
            await page.wait_for_timeout(2000)
            
            # 验证数据源创建成功
            print("验证数据源创建...")
            # 检查是否有成功提示
            success_msg = False
            try:
                success_msg = await page.locator("text=创建成功").is_visible()
            except:
                try:
                    success_msg = await page.locator("text=新增成功").is_visible()
                except:
                    success_msg = await page.locator("text=保存成功").is_visible()
            
            assert success_msg, "数据源创建失败，未找到成功提示"
            
            # 验证新数据源出现在列表中
            await page.wait_for_timeout(1000)
            try:
                new_rows = await page.locator(".el-table__row").count()
            except:
                new_rows = await page.locator("tr").count() - 1  # 减去表头
            
            assert new_rows == initial_rows + 1, f"数据源数量未正确增加，期望{initial_rows + 1}，实际{new_rows}"
            
            print(f"新数据源 '{datasource_name}' 创建成功")
            
            # 测试编辑功能
            print("测试编辑功能...")
            # 点击第一行的编辑按钮
            try:
                await page.locator("button:has-text('编辑')").first.click()
            except:
                # 尝试其他可能的编辑按钮
                buttons = await page.locator("button").all()
                for btn in buttons:
                    text = await btn.text_content()
                    if "编辑" in text:
                        await btn.click()
                        break
            
            await page.wait_for_timeout(1000)
            
            # 等待编辑窗口打开
            await page.wait_for_selector("text=编辑数据源", timeout=10000)
            print("编辑窗口已打开")
            
            # 修改数据源名称
            updated_name = f"更新_{datasource_name}"
            try:
                await page.fill("input[placeholder='请输入数据源名称']", updated_name)
            except:
                # 尝试其他可能的输入框选择器
                input_elements = await page.locator("input").all()
                for input_elem in input_elements:
                    placeholder = await input_elem.get_attribute("placeholder")
                    if placeholder and "数据源名称" in placeholder:
                        await input_elem.fill(updated_name)
                        break
            
            try:
                await page.click("button:has-text('保存')")
            except:
                # 尝试其他可能的按钮
                await page.locator("button:has-text('确 定')").click()
            
            await page.wait_for_timeout(2000)
            
            # 验证编辑成功
            print("验证编辑结果...")
            success_msg = False
            try:
                success_msg = await page.locator("text=更新成功").is_visible()
            except:
                try:
                    success_msg = await page.locator("text=编辑成功").is_visible()
                except:
                    success_msg = await page.locator("text=保存成功").is_visible()
            
            assert success_msg, "数据源编辑失败，未找到成功提示"
            
            # 验证列表中显示更新后的名称
            updated_exists = False
            try:
                updated_exists = await page.locator(f"text={updated_name}").is_visible()
            except:
                # 尝试查找包含更新后名称的元素
                all_texts = await page.inner_text("body")
                updated_exists = updated_name in all_texts
            
            assert updated_exists, f"更新后的数据源名称 '{updated_name}' 未在列表中显示"
            
            print(f"数据源已更新为 '{updated_name}'")
            
            # 测试删除功能
            print("测试删除功能...")
            # 点击删除按钮
            try:
                delete_btn = page.locator("button:has-text('删除')").first
                await delete_btn.scroll_into_view_if_needed()
                await delete_btn.click()
            except:
                # 尝试其他可能的删除按钮
                buttons = await page.locator("button").all()
                for btn in buttons:
                    text = await btn.text_content()
                    if "删除" in text:
                        await btn.click()
                        break
                        break
            
            await page.wait_for_timeout(500)
            
            # 确认删除
            try:
                confirm_button = page.locator("button:has-text('确定')")
                await confirm_button.click()
            except:
                # 尝试其他确认按钮
                try:
                    confirm_button = page.locator("button:has-text('是')")
                    await confirm_button.click()
                except:
                    # 尝试第一个出现的确认按钮
                    confirm_buttons = await page.locator("button").all()
                    for btn in confirm_buttons:
                        text = await btn.text_content()
                        if "确定" in text or "是" in text or "确认" in text:
                            await btn.click()
                            break
            
            await page.wait_for_timeout(2000)
            
            # 验证删除确认弹窗消失
            confirm_exists = False
            try:
                confirm_exists = await page.locator("button:has-text('确定')").is_visible()
            except:
                # 检查是否有任何确认相关的按钮
                all_buttons = await page.locator("button").all()
                for btn in all_buttons:
                    text = await btn.text_content()
                    if "确定" in text or "是" in text or "确认" in text:
                        confirm_exists = True
                        break
            
            assert not confirm_exists, "删除确认框未关闭"
            
            # 验证数据源已被删除
            try:
                final_rows = await page.locator(".el-table__row").count()
            except:
                final_rows = await page.locator("tr").count() - 1  # 减去表头
            
            assert final_rows == initial_rows, f"删除后数据源数量不正确，期望{initial_rows}，实际{final_rows}"
            
            print("数据源删除成功")
            
            print("✅ 数据源管理端到端测试通过!")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            # 截图以便调试
            timestamp = int(time.time())
            await page.screenshot(path=f"datasource_e2e_test_failure_{timestamp}.png")
            raise e
        finally:
            await browser.close()


def run_test():
    """运行测试"""
    print("🚀 开始执行数据源管理端到端测试...")
    asyncio.run(test_datasource_management_workflow())


if __name__ == "__main__":
    run_test()