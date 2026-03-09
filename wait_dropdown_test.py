import asyncio
from playwright.async_api import async_playwright


async def test_wait_dropdown_expansion():
    """等待下拉菜单完全展开后再选择选项"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 访问数据源管理页面
            print("1. 访问数据源管理页面...")
            await page.goto("http://localhost:3000/admin/data-source/config")
            await page.wait_for_load_state('networkidle')
            
            # 等待页面加载完成
            await page.wait_for_selector('text="数据源管理"', timeout=10000)
            
            # 点击新增数据源按钮
            print("2. 点击新增数据源按钮...")
            add_button = page.locator('button:has-text("新增数据源")')
            await add_button.wait_for(timeout=5000)
            await add_button.click()
            
            # 等待对话框出现
            print("3. 等待对话框出现...")
            await page.wait_for_selector('text="新增数据源"', timeout=10000)
            
            # 等待表单元素加载
            await page.wait_for_timeout(1000)
            
            # 填充必要的字段
            print("4. 填充数据源名称...")
            name_input = page.locator('input[placeholder*="数据源名称"]')
            await name_input.wait_for(timeout=5000)
            await name_input.fill('测试数据源')
            
            print("5. 填充接口地址...")
            url_input = page.locator('input[placeholder*="接口地址"]')
            await url_input.wait_for(timeout=5000)
            await url_input.fill('https://api.example.com/data')
            
            print("6. 使用JavaScript定位并点击分类选择器...")
            # 使用JavaScript找到并点击分类选择器
            await page.evaluate("""
                // 获取所有label元素
                const labels = Array.from(document.querySelectorAll('label'));
                // 找到包含"分类"的标签
                const categoryLabel = labels.find(label => label.textContent.includes('分类'));
                
                if (categoryLabel) {
                    // 找到该标签所在的form item
                    const formItem = categoryLabel.closest('.el-form-item');
                    
                    // 找到该form item内的select元素
                    const selectWrapper = formItem.querySelector('.el-select__wrapper');
                    
                    if (selectWrapper) {
                        // 滚动到元素并点击
                        selectWrapper.scrollIntoView({behavior: 'smooth'});
                        selectWrapper.focus();
                        
                        // 创建鼠标事件并派发
                        const event = new MouseEvent('mousedown', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        selectWrapper.dispatchEvent(event);
                    }
                }
            """)
            
            # 等待下拉菜单完全展开
            print("7. 等待下拉菜单展开...")
            await page.wait_for_timeout(2000)  # 等待菜单展开
            
            # 等待"赛事数据"选项可见
            await page.wait_for_selector('text="赛事数据"', state='visible', timeout=10000)
            
            # 选择"赛事数据"选项
            print("8. 选择'赛事数据'选项...")
            await page.click('text="赛事数据"')
            
            print("9. 点击提交按钮...")
            submit_button = page.locator('button:has-text("提交")')
            await submit_button.wait_for(timeout=5000)
            await submit_button.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await submit_button.click()
            
            # 等待成功消息
            print("10. 等待创建成功消息...")
            try:
                await page.wait_for_selector('text="创建成功"', timeout=10000)
                print("✅ 数据源创建成功!")
            except:
                print("❌ 未检测到创建成功提示")
                
                # 检查是否有错误消息
                error_msgs = await page.locator('.el-message, .el-notification').count()
                if error_msgs > 0:
                    error_texts = await page.locator('.el-message, .el-notification').all_text_contents()
                    for txt in error_texts:
                        if txt.strip():
                            print(f"错误消息: {txt}")
                
                # 检查是否是验证错误
                validation_errors = await page.locator('.el-form-item__error').count()
                if validation_errors > 0:
                    validation_texts = await page.locator('.el-form-item__error').all_text_contents()
                    for txt in validation_texts:
                        if txt.strip():
                            print(f"验证错误: {txt}")
                
                await page.screenshot(path='wait_dropdown_test_creation_failed.png')
                return  # 如果创建失败则退出测试
            
            # 等待页面更新
            await page.wait_for_timeout(2000)
            
            # 检查新创建的数据源是否出现在列表中
            print("11. 检查新创建的数据源是否出现在列表中...")
            data_source_exists = await page.locator('text="测试数据源"').count() > 0
            if data_source_exists:
                print("✅ 新创建的数据源出现在列表中")
            else:
                print("❌ 新创建的数据源未出现在列表中")
                
            # 查找并点击编辑按钮
            print("12. 查找并点击编辑按钮...")
            # 获取第一个编辑按钮
            edit_buttons = page.locator('button:has-text("编辑")')
            await edit_buttons.first.wait_for(timeout=5000)
            await edit_buttons.first.scroll_into_view_if_needed()
            await edit_buttons.first.click()
            
            # 等待编辑对话框出现
            print("13. 等待编辑对话框出现...")
            await page.wait_for_selector('text="编辑数据源"', timeout=10000)
            
            print("14. 更改分类为'球员信息'...")
            # 等待一点时间确保UI更新
            await page.wait_for_timeout(1000)
            
            # 再次使用JavaScript定位分类选择器
            await page.evaluate("""
                // 获取所有label元素
                const labels = Array.from(document.querySelectorAll('label'));
                // 找到包含"分类"的标签
                const categoryLabel = labels.find(label => label.textContent.includes('分类'));
                
                if (categoryLabel) {
                    // 找到该标签所在的form item
                    const formItem = categoryLabel.closest('.el-form-item');
                    
                    // 找到该form item内的select元素
                    const selectWrapper = formItem.querySelector('.el-select__wrapper');
                    
                    if (selectWrapper) {
                        // 滚动到元素并点击
                        selectWrapper.scrollIntoView({behavior: 'smooth'});
                        selectWrapper.focus();
                        
                        // 创建鼠标事件并派发
                        const event = new MouseEvent('mousedown', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        selectWrapper.dispatchEvent(event);
                    }
                }
            """)
            
            # 等待下拉菜单完全展开
            print("15. 等待下拉菜单展开...")
            await page.wait_for_timeout(2000)  # 等待菜单展开
            
            # 等待"球员信息"选项可见
            await page.wait_for_selector('text="球员信息"', state='visible', timeout=10000)
            
            # 选择"球员信息"选项
            print("16. 选择'球员信息'选项...")
            await page.click('text="球员信息"')
            
            print("17. 点击提交按钮...")
            await submit_button.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await submit_button.click()
            
            # 等待更新成功消息
            print("18. 等待更新成功消息...")
            try:
                await page.wait_for_selector('text="更新成功"', timeout=10000)
                print("✅ 数据源更新成功!")
            except:
                print("❌ 未检测到更新成功提示")
                
                # 获取错误信息
                error_msgs = await page.locator('.el-message, .el-notification').count()
                if error_msgs > 0:
                    error_texts = await page.locator('.el-message, .el-notification').all_text_contents()
                    for txt in error_texts:
                        if txt.strip():
                            print(f"错误消息: {txt}")
                            
                await page.screenshot(path='wait_dropdown_test_update_failed.png')
                
            print("✅ 等待下拉展开测试流程结束")
                
        except Exception as e:
            print(f"测试过程中出现错误: {str(e)}")
            await page.screenshot(path='wait_dropdown_test_error.png')
            raise e
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_wait_dropdown_expansion())