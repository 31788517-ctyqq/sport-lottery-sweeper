import asyncio
from playwright.async_api import async_playwright


async def test_with_detailed_debugging():
    """使用详细调试信息的测试"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 访问数据源管理页面
            print("正在访问数据源管理页面...")
            await page.goto("http://localhost:3000/admin/data-source/config")
            await page.wait_for_load_state('networkidle')
            
            # 等待页面加载完成
            print("等待页面加载...")
            await page.wait_for_selector('text="数据源管理"', timeout=10000)
            
            # 点击新增数据源按钮
            print("点击新增数据源按钮...")
            await page.locator('button:has-text("新增数据源")').click()
            
            # 等待对话框出现
            print("等待对话框出现...")
            await page.wait_for_selector('text="新增数据源"', timeout=10000)
            
            # 等待表单元素加载
            print("等待表单元素加载...")
            await page.wait_for_timeout(1000)
            
            # 查找所有表单输入框并打印它们的信息
            inputs = await page.query_selector_all('input')
            print(f"找到 {len(inputs)} 个输入框")
            for i, inp in enumerate(inputs):
                placeholder = await inp.get_attribute('placeholder')
                print(f"  输入框 {i}: placeholder='{placeholder}'")
            
            # 查找所有选择框并打印它们的信息
            selects = await page.query_selector_all('select, .el-select')
            print(f"找到 {len(selects)} 个选择控件")
            
            # 查找特定的输入框并填充
            print("尝试填充数据源名称...")
            name_input = page.locator('input[placeholder*="数据源名称"]')
            await name_input.wait_for(timeout=5000)
            await name_input.fill('测试数据源')
            print("数据源名称填充成功")
            
            print("尝试填充接口地址...")
            url_input = page.locator('input[placeholder*="接口地址"]')
            await url_input.wait_for(timeout=5000)
            await url_input.fill('https://api.example.com/data')
            print("接口地址填充成功")
            
            print("选择数据源类型...")
            type_radio = page.locator('label:has-text("API接口") input[type="radio"]')
            await type_radio.wait_for(timeout=5000)
            await type_radio.click()
            print("数据源类型选择成功")
            
            print("选择分类...")
            category_select = page.locator('.el-select').nth(0)  # 第一个选择框应该是分类
            await category_select.click()
            await page.wait_for_timeout(500)
            await page.locator('text="赛事数据"').click()
            print("分类选择成功")
            
            print("点击提交按钮...")
            submit_button = page.locator('button:has-text("提交")')
            await submit_button.scroll_into_view_if_needed()
            await submit_button.wait_for(timeout=5000)
            await submit_button.click()
            print("提交按钮点击成功")
            
            # 等待成功消息
            try:
                await page.wait_for_selector('text="创建成功"', timeout=10000)
                print("✅ 数据源创建成功!")
            except:
                print("❌ 未检测到创建成功提示")
                
                # 获取页面所有错误消息
                error_elements = await page.query_selector_all('.el-message, .el-notification, .error')
                for el in error_elements:
                    text = await el.text_content()
                    if text.strip():
                        print(f"页面消息: {text}")
                
                # 截图用于调试
                await page.screenshot(path='debug_flexible_test.png')
                
        except Exception as e:
            print(f"测试失败: {str(e)}")
            await page.screenshot(path='error_flexible_test.png')
            raise e
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_with_detailed_debugging())