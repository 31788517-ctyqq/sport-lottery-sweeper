import asyncio
from playwright.async_api import async_playwright


async def test_debug_version():
    """调试版本的测试，输出更多信息"""
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
            
            print("6. 使用JavaScript点击分类下拉框...")
            # 使用JavaScript直接点击分类选择器
            await page.evaluate("""
                // 获取所有label元素
                const labels = Array.from(document.querySelectorAll('label'));
                // 找到第二个包含"分类"的标签（内容分类）
                const categoryLabels = labels.filter(label => label.textContent.includes('分类'));
                if (categoryLabels.length >= 2) {
                    const targetLabel = categoryLabels[1];
                    
                    // 找到该标签所在的form item
                    const formItem = targetLabel.closest('.el-form-item');
                    
                    // 找到该form item内的select元素
                    const selectWrapper = formItem.querySelector('.el-select__wrapper');
                    
                    if (selectWrapper) {
                        // 滚动到元素并点击
                        selectWrapper.scrollIntoView({behavior: 'smooth'});
                        
                        // 创建并派发事件
                        const mouseDownEvent = new MouseEvent('mousedown', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        selectWrapper.dispatchEvent(mouseDownEvent);
                        
                        // 再创建并派发click事件，确保展开
                        const clickEvent = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        selectWrapper.dispatchEvent(clickEvent);
                    }
                }
            """)
            
            # 等待下拉菜单展开
            await page.wait_for_timeout(1000)
            
            # 查看下拉选项的顺序，"体育情报", "赛事数据", "赔率数据", "指数数据"
            # 我们要选择"赛事数据"，它是第2个选项
            print("7. 使用键盘选择'赛事数据'（第2个选项）...")
            await page.keyboard.press('ArrowDown')  # 选择第1个选项 "体育情报"
            await page.wait_for_timeout(300)
            await page.keyboard.press('ArrowDown')  # 选择第2个选项 "赛事数据"
            await page.wait_for_timeout(300)
            await page.keyboard.press('Enter')      # 确认选择
            
            # 检查是否选择了正确的值
            await page.wait_for_timeout(500)
            selected_value = await page.evaluate("""
                // 获取所有label元素
                const labels = Array.from(document.querySelectorAll('label'));
                // 找到第二个包含"分类"的标签（内容分类）
                const categoryLabels = labels.filter(label => label.textContent.includes('分类'));
                if (categoryLabels.length >= 2) {
                    const targetLabel = categoryLabels[1];
                    
                    // 找到该标签所在的form item
                    const formItem = targetLabel.closest('.el-form-item');
                    
                    // 找到该form item内的select元素
                    const selectInput = formItem.querySelector('.el-select__input');
                    if (selectInput) {
                        return selectInput.value || 'no value';
                    }
                    
                    const selectSpan = formItem.querySelector('.el-select__selection .el-select__selected-item span');
                    if (selectSpan) {
                        return selectSpan.textContent || 'no text';
                    }
                }
                return 'not found';
            """)
            print(f"当前选择的值: {selected_value}")
            
            print("8. 点击提交按钮...")
            submit_button = page.locator('button:has-text("提交")')
            await submit_button.wait_for(timeout=5000)
            await submit_button.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await submit_button.click()
            
            # 等待成功消息或错误消息
            print("9. 等待响应消息...")
            # 等待几秒钟查看是否有任何消息
            await page.wait_for_timeout(3000)
            
            # 检查是否有成功消息
            success_msg_count = await page.locator('text="创建成功"').count()
            if success_msg_count > 0:
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
                
                # 检查是否是验证错误
                validation_errors = await page.locator('.el-form-item__error').count()
                if validation_errors > 0:
                    validation_texts = await page.locator('.el-form-item__error').all_text_contents()
                    for txt in validation_texts:
                        if txt.strip():
                            print(f"验证错误: {txt}")
                
                # 获取所有表单错误
                form_items_with_error = await page.locator('.el-form-item.is-error .el-form-item__label').all_text_contents()
                if form_items_with_error:
                    print(f"表单项错误: {form_items_with_error}")
                
                await page.screenshot(path='final_debug_test_creation_failed.png')
                return  # 如果创建失败则退出测试
            
            # 等待页面更新
            await page.wait_for_timeout(2000)
            
            # 检查新创建的数据源是否出现在列表中
            print("10. 检查新创建的数据源是否出现在列表中...")
            data_source_exists = await page.locator('text="测试数据源"').count() > 0
            if data_source_exists:
                print("✅ 新创建的数据源出现在列表中")
            else:
                print("❌ 新创建的数据源未出现在列表中")
                
            # 查找并点击编辑按钮
            print("11. 查找并点击编辑按钮...")
            # 获取第一个编辑按钮
            edit_buttons = page.locator('button:has-text("编辑")')
            await edit_buttons.first.wait_for(timeout=5000)
            await edit_buttons.first.scroll_into_view_if_needed()
            await edit_buttons.first.click()
            
            # 等待编辑对话框出现
            print("12. 等待编辑对话框出现...")
            await page.wait_for_selector('text="编辑数据源"', timeout=10000)
            
            print("13. 更改分类为'球员信息'...")
            # 等待一点时间确保UI更新
            await page.wait_for_timeout(1000)
            
            # 再次使用JavaScript点击分类选择器
            await page.evaluate("""
                // 获取所有label元素
                const labels = Array.from(document.querySelectorAll('label'));
                // 找到第二个包含"分类"的标签（内容分类）
                const categoryLabels = labels.filter(label => label.textContent.includes('分类'));
                if (categoryLabels.length >= 2) {
                    const targetLabel = categoryLabels[1];
                    
                    // 找到该标签所在的form item
                    const formItem = targetLabel.closest('.el-form-item');
                    
                    // 找到该form item内的select元素
                    const selectWrapper = formItem.querySelector('.el-select__wrapper');
                    
                    if (selectWrapper) {
                        // 滚动到元素并点击
                        selectWrapper.scrollIntoView({behavior: 'smooth'});
                        
                        // 创建并派发事件
                        const mouseDownEvent = new MouseEvent('mousedown', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        selectWrapper.dispatchEvent(mouseDownEvent);
                        
                        // 再创建并派发click事件，确保展开
                        const clickEvent = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        selectWrapper.dispatchEvent(clickEvent);
                    }
                }
            """)
            
            # 等待下拉菜单展开
            await page.wait_for_timeout(1000)
            
            # 选择"球员信息"选项
            print("14. 使用键盘选择'球员信息'...")
            await page.keyboard.press('ArrowDown')  # "体育情报"
            await page.wait_for_timeout(300)
            await page.keyboard.press('ArrowDown')  # "赛事数据"
            await page.wait_for_timeout(300)
            await page.keyboard.press('ArrowDown')  # "赔率数据"
            await page.wait_for_timeout(300)
            await page.keyboard.press('ArrowDown')  # "指数数据"
            await page.wait_for_timeout(300)
            await page.keyboard.press('ArrowDown')  # "球员信息"
            await page.wait_for_timeout(300)
            await page.keyboard.press('Enter')      # 确认选择
            
            # 检查是否选择了正确的值
            await page.wait_for_timeout(500)
            selected_value = await page.evaluate("""
                // 获取所有label元素
                const labels = Array.from(document.querySelectorAll('label'));
                // 找到第二个包含"分类"的标签（内容分类）
                const categoryLabels = labels.filter(label => label.textContent.includes('分类'));
                if (categoryLabels.length >= 2) {
                    const targetLabel = categoryLabels[1];
                    
                    // 找到该标签所在的form item
                    const formItem = targetLabel.closest('.el-form-item');
                    
                    // 找到该form item内的select元素
                    const selectInput = formItem.querySelector('.el-select__input');
                    if (selectInput) {
                        return selectInput.value || 'no value';
                    }
                    
                    const selectSpan = formItem.querySelector('.el-select__selection .el-select__selected-item span');
                    if (selectSpan) {
                        return selectSpan.textContent || 'no text';
                    }
                }
                return 'not found';
            """)
            print(f"当前选择的值: {selected_value}")
            
            print("15. 点击提交按钮...")
            await submit_button.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await submit_button.click()
            
            # 等待更新成功消息
            print("16. 等待更新成功消息...")
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
                            
                await page.screenshot(path='final_debug_test_update_failed.png')
                
            print("✅ 调试测试流程结束")
                
        except Exception as e:
            print(f"测试过程中出现错误: {str(e)}")
            await page.screenshot(path='final_debug_test_error.png')
            raise e
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_debug_version())