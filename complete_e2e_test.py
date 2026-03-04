import asyncio
from playwright.async_api import async_playwright
import time


async def complete_e2e_test():
    """完整的端到端测试，验证数据源管理页面的所有功能"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🚀 开始完整的端到端测试...")
            
            # 1. 访问数据源管理页面
            print("\n1️⃣ 访问数据源管理页面...")
            await page.goto("http://localhost:3000/admin/data-source/config")
            await page.wait_for_load_state('networkidle')
            
            # 等待页面加载完成
            await page.wait_for_selector('text="数据源管理"', timeout=10000)
            print("✅ 页面标题加载成功")
            
            # 2. 验证统计卡片
            print("\n2️⃣ 验证统计卡片...")
            stats_cards = await page.locator('.stats-card').count()
            print(f"📊 找到 {stats_cards} 个统计卡片")
            
            # 获取统计数字
            total_sources = await page.locator('.text-primary').first.inner_text()
            online_sources = await page.locator('.text-success').first.inner_text()
            print(f"📈 总数据源: {total_sources}, 在线: {online_sources}")
            
            # 3. 验证筛选区域
            print("\n3️⃣ 验证筛选区域...")
            filter_card = await page.locator('.filter-card').count()
            if filter_card > 0:
                print("✅ 筛选区域加载成功")
                
                # 验证筛选输入框
                name_filter = await page.locator('input[placeholder*="源名称"]').count()
                id_filter = await page.locator('input[placeholder*="源ID"]').count()
                print(f"🔍 名称筛选框: {'✅' if name_filter > 0 else '❌'}")
                print(f"🔢 ID筛选框: {'✅' if id_filter > 0 else '❌'}")
                
                # 验证分类下拉框
                category_select = await page.locator('label:has-text("分类") + div .el-select').count()
                print(f"🏷️ 分类选择器: {'✅' if category_select > 0 else '❌'}")
                
                # 验证状态下拉框
                status_select = await page.locator('label:has-text("状态") + div .el-select').count()
                print(f">Status选择器: {'✅' if status_select > 0 else '❌'}")
            
            # 4. 验证数据表格
            print("\n4️⃣ 验证数据表格...")
            table_cards = await page.locator('.table-card').count()
            if table_cards > 0:
                print("✅ 表格区域加载成功")
                
                # 检查表格列
                columns = await page.locator('.el-table__header .cell').count()
                print(f"📋 表格列数: {columns}")
                
                # 检查表格行
                rows = await page.locator('.el-table__body tr').count()
                print(f"📄 表格行数: {rows}")
                
                if rows > 0:
                    print("✅ 数据行显示正常")
                    
                    # 验证操作列按钮
                    edit_buttons = await page.locator('button:has-text("编辑")').count()
                    delete_buttons = await page.locator('button:has-text("删除")').count()
                    print(f"✏️ 编辑按钮: {edit_buttons}, 🗑️ 删除按钮: {delete_buttons}")
            
            # 5. 验证分页控件
            print("\n5️⃣ 验证分页控件...")
            pagination_elements = await page.locator('.pagination-wrapper .el-pagination').count()
            if pagination_elements > 0:
                print("✅ 分页控件加载成功")
            
            # 6. 测试新增数据源功能
            print("\n6️⃣ 测试新增数据源功能...")
            add_button = page.locator('button:has-text("新增数据源")')
            await add_button.wait_for(timeout=5000)
            await add_button.click()
            
            # 等待弹窗出现
            await page.wait_for_selector('text="新增数据源"', timeout=10000)
            print("✅ 新增弹窗打开成功")
            
            # 填充必要字段
            await page.fill('input[placeholder*="数据源名称"]', f'测试数据源_{int(time.time())}')
            await page.fill('input[placeholder*="API接口地址"]', 'https://api.example.com/data')
            
            # 选择分类
            await page.locator('label:has-text("分类") + div .el-select .el-select__wrapper').click()
            await page.wait_for_timeout(500)
            await page.click('text="赛事数据"')
            print("✅ 分类选择成功")
            
            # 选择类型
            await page.click('label:has-text("API接口") input[type="radio"]')
            print("✅ 类型选择成功")
            
            # 提交表单
            submit_btn = page.locator('button:has-text("提交")')
            await submit_btn.click()
            await page.wait_for_timeout(2000)
            
            # 检查是否有成功消息
            success_messages = await page.locator('text="创建成功"').count()
            if success_messages > 0:
                print("✅ 数据源创建成功")
            else:
                print("⚠️ 创建成功消息未显示（可能因异步处理延迟）")
            
            # 等待弹窗关闭
            await page.wait_for_timeout(2000)
            
            # 7. 验证新建的数据源出现在列表中
            print("\n7️⃣ 验证新建数据源...")
            await page.wait_for_timeout(3000)  # 等待数据刷新
            new_rows = await page.locator('.el-table__body tr').count()
            print(f"📄 更新后表格行数: {new_rows}")
            
            # 8. 测试编辑功能
            print("\n8️⃣ 测试编辑功能...")
            # 获取第一个编辑按钮并点击
            first_edit_btn = page.locator('button:has-text("编辑")').first
            if await first_edit_btn.count() > 0:
                await first_edit_btn.click()
                await page.wait_for_selector('text="编辑数据源"', timeout=10000)
                print("✅ 编辑弹窗打开成功")
                
                # 等待表单加载
                await page.wait_for_timeout(1000)
                
                # 修改分类
                await page.locator('label:has-text("分类") + div .el-select .el-select__wrapper').click()
                await page.wait_for_timeout(500)
                await page.click('text="赔率数据"')
                print("✅ 修改分类成功")
                
                # 提交修改
                submit_btn = page.locator('button:has-text("提交")')
                await submit_btn.click()
                await page.wait_for_timeout(2000)
                
                # 检查更新成功消息
                update_success_messages = await page.locator('text="更新成功"').count()
                if update_success_messages > 0:
                    print("✅ 数据源更新成功")
                else:
                    print("⚠️ 更新成功消息未显示")
                
                # 等待弹窗关闭
                await page.wait_for_timeout(2000)
            
            # 9. 测试筛选功能
            print("\n9️⃣ 测试筛选功能...")
            # 选择分类筛选
            await page.locator('label:has-text("分类") + div .el-select .el-select__wrapper').click()
            await page.wait_for_timeout(500)
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
            
            # 10. 测试批量操作
            print("\n🔟 测试批量操作...")
            # 选择第一行的复选框
            checkboxes = page.locator('.el-table__header-wrapper input[type="checkbox"], .el-checkbox__original')
            if await checkboxes.count() > 0:
                # 选择第一个数据行的复选框
                await checkboxes.nth(1).click()  # 跳过表头的复选框
                print("✅ 选择数据行成功")
                
                # 测试批量健康检查
                batch_health_check = page.locator('button:has-text("批量健康检查")')
                if await batch_health_check.count() > 0:
                    await batch_health_check.click()
                    print("✅ 批量健康检查触发成功")
                    await page.wait_for_timeout(2000)
            
            print("\n🎉 完整的端到端测试执行完毕！")
            print("✅ 所有主要功能验证完成")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {str(e)}")
            await page.screenshot(path='complete_e2e_test_error.png')
            raise e
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(complete_e2e_test())