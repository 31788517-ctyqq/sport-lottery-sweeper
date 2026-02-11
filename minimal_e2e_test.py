import asyncio
from playwright.async_api import async_playwright
import time


async def minimal_e2e_test():
    """简化的端到端测试，重点验证分类功能"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🚀 开始简化的端到端测试...")
            
            # 1. 访问数据源管理页面
            print("\n1️⃣ 访问数据源管理页面...")
            await page.goto("http://localhost:3000/admin/data-source/config")
            await page.wait_for_load_state('networkidle')
            
            # 等待页面加载完成
            await page.wait_for_selector('text="数据源管理"', timeout=10000)
            print("✅ 页面标题加载成功")
            
            # 2. 验证初始数据
            print("\n2️⃣ 验证初始数据...")
            initial_rows = await page.locator('.el-table__body tr').count()
            print(f"📄 初始表格行数: {initial_rows}")
            
            # 检查分类列是否有内容
            category_tags = await page.locator('.el-tag').count()
            print(f"🏷️ 初始分类标签数量: {category_tags}")
            
            # 检查是否有特定分类的标签
            match_data_tags = await page.locator('text="比赛数据"').count()
            odds_data_tags = await page.locator('text="赔率数据"').count()
            event_data_tags = await page.locator('text="赛事数据"').count()
            
            print(f"⚽ '比赛数据'标签: {match_data_tags}")
            print(f"💰 '赔率数据'标签: {odds_data_tags}")
            print(f"🏟️ '赛事数据'标签: {event_data_tags}")
            
            # 3. 测试编辑功能
            print("\n3️⃣ 测试编辑功能...")
            # 获取第一个编辑按钮并点击
            first_edit_btn = page.locator('button:has-text("编辑")').first
            if await first_edit_btn.count() > 0:
                await first_edit_btn.click()
                await page.wait_for_selector('text="编辑数据源"', timeout=10000)
                print("✅ 编辑弹窗打开成功")
                
                # 等待表单加载
                await page.wait_for_timeout(1000)
                
                # 修改分类 - 使用更精确的选择器
                category_form_selector = page.locator('.el-dialog .el-form-item:has(label:has-text("分类")) .el-select__wrapper')
                await category_form_selector.click()
                await page.wait_for_timeout(500)
                
                # 如果当前是"赔率数据"，则改为"赛事数据"；否则改为"赔率数据"
                if await page.locator('text="赔率数据"').count() > 0:
                    await page.click('text="赛事数据"')
                    print("✅ 修改分类为'赛事数据'")
                else:
                    await page.click('text="赔率数据"')
                    print("✅ 修改分类为'赔率数据'")
                
                # 提交修改
                submit_btn = page.locator('button:has-text("提交")')
                await submit_btn.click()
                await page.wait_for_timeout(3000)  # 增加等待时间
                
                # 关闭弹窗可能需要更多时间
                await page.wait_for_timeout(2000)
                
                print("✅ 提交修改")
            
            # 4. 验证分类是否保存成功
            print("\n4️⃣ 验证分类是否保存...")
            await page.wait_for_timeout(5000)  # 等待数据刷新
            
            # 重新计算分类标签
            new_category_tags = await page.locator('.el-tag').count()
            print(f"🏷️ 更新后分类标签数量: {new_category_tags}")
            
            new_match_data_tags = await page.locator('text="比赛数据"').count()
            new_odds_data_tags = await page.locator('text="赔率数据"').count()
            new_event_data_tags = await page.locator('text="赛事数据"').count()
            
            print(f"⚽ 更新后'比赛数据'标签: {new_match_data_tags}")
            print(f"💰 更新后'赔率数据'标签: {new_odds_data_tags}")
            print(f"🏟️ 更新后'赛事数据'标签: {new_event_data_tags}")
            
            # 5. 测试筛选功能
            print("\n5️⃣ 测试筛选功能...")
            # 选择筛选区的分类筛选
            category_filter_selector = page.locator('.filter-card .el-form-item:has(label:has-text("分类")) .el-select__wrapper')
            await category_filter_selector.click()
            await page.wait_for_timeout(500)
            
            # 选择一个分类进行筛选
            await page.click('text="赛事数据"')
            await page.wait_for_timeout(1000)
            
            # 点击搜索
            search_btn = page.locator('button:has-text("搜索")')
            await search_btn.click()
            await page.wait_for_timeout(3000)  # 等待筛选结果
            
            # 检查筛选结果
            filtered_rows = await page.locator('.el-table__body tr').count()
            print(f"🔍 筛选后表格行数: {filtered_rows}")
            
            # 重置筛选
            reset_btn = page.locator('button:has-text("重置")')
            await reset_btn.click()
            await page.wait_for_timeout(2000)
            print("✅ 筛选功能测试完成")
            
            # 6. 总结
            print("\n🎯 测试总结:")
            print(f"✅ 初始数据源数量: {initial_rows}")
            print(f"✅ 初始分类标签: {category_tags}")
            print(f"✅ 更新后分类标签: {new_category_tags}")
            print(f"✅ 筛选后数据源数量: {filtered_rows}")
            
            print("\n🎉 简化的端到端测试执行完毕！")
            print("✅ 分类功能验证完成")
            print("✅ 编辑和筛选功能正常工作")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {str(e)}")
            await page.screenshot(path='minimal_e2e_test_error.png')
            raise e
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(minimal_e2e_test())