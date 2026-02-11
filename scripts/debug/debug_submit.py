import asyncio
from playwright.async_api import async_playwright

async def check_submit_button():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto('http://localhost:3000/admin/data-source/config')
            await page.wait_for_load_state('networkidle')
            
            # 点击新增数据源按钮
            await page.click('button:has-text("新增数据源")')
            await page.wait_for_selector('text="新增数据源"', timeout=10000)
            
            # 填写表单
            await page.fill('input[placeholder*="请输入数据源名称"]', '测试数据源')
            await page.fill('input[placeholder*="请输入接口地址"]', 'https://api.example.com/data')
            
            # 选择分类
            await page.click('.el-select__wrapper')
            await page.click('text="比赛数据"')
            
            # 点击提交按钮
            submit_button = page.locator('button:has-text("提交")')
            await submit_button.scroll_into_view_if_needed()
            await submit_button.click()
            
            # 等待几秒钟并截图查看结果
            await page.wait_for_timeout(3000)
            await page.screenshot(path='debug_submit.png')
            
            print('截图已保存为 debug_submit.png')
            
        except Exception as e:
            print(f'测试失败: {str(e)}')
            await page.screenshot(path='error_debug.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(check_submit_button())