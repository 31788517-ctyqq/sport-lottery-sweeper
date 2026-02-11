import asyncio
from playwright.async_api import async_playwright


async def test_create_and_edit_datasource_final():
    """最终的测试：创建和编辑数据源的完整流程"""
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
            
            print("6. 使用JavaScript直接选择分类...")
            # 通过data-test-id或更具体的属性来定位元素
            await page.evaluate("""
                // 找到具有prop="category"属性的el-select组件
                const categorySelect = Array.from(document.querySelectorAll('.el-select'))
                    .find(select => select.querySelector('label:contains("分类")') !== null);
                
                if (categorySelect) {
                    // 找到下拉箭头并点击
                    const arrow = categorySelect.querySelector('.el-select__caret');
                    if (arrow) {
                        arrow.click();
                    } else {
                        // 如果没有找到箭头，尝试直接点击wrapper
                        const wrapper = categorySelect.querySelector('.el-select__wrapper');
                        if (wrapper) {
                            wrapper.click();
                        }
                    }
                } else {
                    // 通过prop属性查找
                    const allSelects = document.querySelectorAll('.el-select');
                    for (let select of allSelects) {
                        const formItem = select.closest('.el-form-item');
                        if (formItem && formItem.querySelector('label:has-text("分类")')) {
                            const wrapper = select.querySelector('.el-select__wrapper');
                            if (wrapper) {
                                wrapper.click();
                                break;
                            }
                        }
                    }
                }
            """)
            
            await page.wait_for_timeout(1000)
            
            # 选择"赛事数据"选项
            await page.evaluate("""
                // 查找并点击"赛事数据"选项
                const options = document.querySelectorAll('.el-popper .el-select-dropdown__item');
                for (let option of options) {
                    if (option.textContent && option.textContent.includes('赛事数据')) {
                        option.click();
                        break;
                    }
                }
            """)
            
            print("7. 点击提交按钮...")
            submit_button = page.locator('button:has-text("提交")')
            await submit_button.wait_for(timeout=5000)
            await submit_button.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await submit_button.click()
            
            # 等待成功消息
            print("8. 等待创建成功消息...")
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
                
                await page.screenshot(path='final_test_creation_failed.png')
                return  # 如果创建失败则退出测试
            
            # 等待页面更新
            await page.wait_for_timeout(2000)
            
            # 检查新创建的数据源是否出现在列表中
            print("9. 检查新创建的数据源是否出现在列表中...")
            data_source_exists = await page.locator('text="测试数据源"').count() > 0
            if data_source_exists:
                print("✅ 新创建的数据源出现在列表中")
            else:
                print("❌ 新创建的数据源未出现在列表中")
                
            # 查找并点击编辑按钮
            print("10. 查找并点击编辑按钮...")
            # 获取第一个编辑按钮
            edit_buttons = page.locator('button:has-text("编辑")')
            await edit_buttons.first.wait_for(timeout=5000)
            await edit_buttons.first.scroll_into_view_if_needed()
            await edit_buttons.first.click()
            
            # 等待编辑对话框出现
            print("11. 等待编辑对话框出现...")
            await page.wait_for_selector('text="编辑数据源"', timeout=10000)
            
            print("12. 使用JavaScript更改分类为'球员信息'...")
            # 等待一点时间确保UI更新
            await page.wait_for_timeout(1000)
            
            # 再次打开下拉菜单
            await page.evaluate("""
                // 找到分类选择器并点击
                const allSelects = document.querySelectorAll('.el-select');
                for (let select of allSelects) {
                    const formItem = select.closest('.el-form-item');
                    if (formItem && formItem.querySelector('label:has-text("分类")')) {
                        const wrapper = select.querySelector('.el-select__wrapper');
                        if (wrapper) {
                            wrapper.click();
                            break;
                        }
                    }
                }
            """)
            
            await page.wait_for_timeout(1000)
            
            # 选择"球员信息"选项
            await page.evaluate("""
                // 查找并点击"球员信息"选项
                const options = document.querySelectorAll('.el-popper .el-select-dropdown__item');
                for (let option of options) {
                    if (option.textContent && option.textContent.includes('球员信息')) {
                        option.click();
                        break;
                    }
                }
            """)
            
            print("13. 点击提交按钮...")
            await submit_button.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await submit_button.click()
            
            # 等待更新成功消息
            print("14. 等待更新成功消息...")
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
                            
                await page.screenshot(path='final_test_update_failed.png')
                
            print("✅ 最终测试流程结束")
                
        except Exception as e:
            print(f"测试过程中出现错误: {str(e)}")
            await page.screenshot(path='final_test_error.png')
            raise e
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_create_and_edit_datasource_final())