import asyncio
from playwright.async_api import async_playwright


async def test_submit_issue():
    """测试提交按钮问题"""
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
            
            # 填充必要的字段
            print("填充数据源名称...")
            await page.fill('input[placeholder*="数据源名称"]', '测试数据源')
            
            print("填充接口地址...")
            await page.fill('input[placeholder*="接口地址"]', 'https://api.example.com/data')
            
            print("选择分类...")
            # 点击下拉框
            await page.click('.el-select__wrapper')
            await page.wait_for_timeout(500)
            # 选择"赛事数据"选项
            await page.click('text="赛事数据"')
            
            print("点击提交按钮...")
            submit_button = page.locator('button:has-text("提交")')
            await submit_button.scroll_into_view_if_needed()
            # 等待按钮可用
            await page.wait_for_timeout(500)
            await submit_button.click()
            
            # 等待响应
            await page.wait_for_timeout(3000)
            
            # 检查是否有成功消息
            success_msg = await page.locator('text="创建成功"').count()
            if success_msg > 0:
                print("✅ 数据源创建成功!")
            else:
                print("❌ 未检测到创建成功提示")
                
                # 检查是否有错误消息
                error_msgs = await page.locator('.el-message, .el-notification').count()
                if error_msgs > 0:
                    error_texts = await page.locator('.el-message, .el-notification').all_text_contents()
                    for txt in error_texts:
                        if txt.strip():
                            print(f"错误消息: {txt}")
                
                # 截图用于调试
                await page.screenshot(path='submit_test_debug.png')
                
        except Exception as e:
            print(f"测试失败: {str(e)}")
            await page.screenshot(path='submit_test_error.png')
            raise e
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_submit_issue())