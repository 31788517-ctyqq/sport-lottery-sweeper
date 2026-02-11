import asyncio
from playwright.async_api import async_playwright


async def inspect_form_structure():
    """检查表单结构以找到正确的选择器"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # headless模式用于检查页面结构
        page = await browser.new_page()
        
        try:
            # 访问数据源管理页面
            print("访问数据源管理页面...")
            await page.goto("http://localhost:3000/admin/data-source/config")
            await page.wait_for_load_state('networkidle')
            
            # 等待页面加载完成
            await page.wait_for_selector('text="数据源管理"', timeout=10000)
            
            # 点击新增数据源按钮
            print("点击新增数据源按钮...")
            add_button = page.locator('button:has-text("新增数据源")')
            await add_button.wait_for(timeout=5000)
            await add_button.click()
            
            # 等待对话框出现
            print("等待对话框出现...")
            await page.wait_for_selector('text="新增数据源"', timeout=10000)
            
            # 等待表单元素加载
            await page.wait_for_timeout(2000)
            
            # 获取整个对话框的HTML内容
            dialog_html = await page.locator('.el-dialog').first.inner_html()
            print("对话框HTML结构:")
            print(dialog_html[:2000] + ("..." if len(dialog_html) > 2000 else ""))
            
            # 查找所有带prop属性的元素
            props = await page.locator('*[prop]').count()
            print(f"\n找到 {props} 个带prop属性的元素:")
            for i in range(props):
                element = page.locator('*[prop]').nth(i)
                prop_value = await element.get_attribute('prop')
                tag_name = await element.evaluate('(el) => el.tagName')
                print(f"- {tag_name} with prop='{prop_value}'")
            
            # 特别查找分类相关的元素
            print("\n查找分类相关元素:")
            category_count = await page.locator('text="分类"').count()
            print(f"找到 {category_count} 个包含'分类'的元素")
            
            for i in range(category_count):
                category_elem = page.locator('text="分类"').nth(i)
                parent = category_elem.locator('..')
                parent_html = await parent.inner_html()
                print(f"第{i+1}个'分类'的父元素HTML片段:")
                print(parent_html[:500])
            
        except Exception as e:
            print(f"检查过程中出现错误: {str(e)}")
            await page.screenshot(path='inspect_error.png')
            raise e
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_form_structure())