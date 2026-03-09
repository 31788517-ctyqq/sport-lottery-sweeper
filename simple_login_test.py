"""
简化版登录测试
验证前端登录功能是否正常
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright
import time


async def test_login():
    """
    测试登录功能
    """
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("正在访问前端系统...")
            # 访问前端页面 - 使用正确的端口
            await page.goto("http://localhost:3001")
            
            # 等待页面加载
            await page.wait_for_timeout(2000)
            
            # 检查页面标题或其他标识
            title = await page.title()
            print(f"页面标题: {title}")
            
            # 查找页面上的所有输入框
            inputs = await page.locator("input").all()
            print(f"找到 {len(inputs)} 个输入框")
            
            for i, inp in enumerate(inputs):
                placeholder = await inp.get_attribute("placeholder")
                inp_type = await inp.get_attribute("type")
                print(f"  输入框 {i}: type={inp_type}, placeholder='{placeholder}'")
            
            # 查找所有按钮
            buttons = await page.locator("button").all()
            print(f"找到 {len(buttons)} 个按钮")
            
            for i, btn in enumerate(buttons):
                btn_text = await btn.text_content()
                print(f"  按钮 {i}: text='{btn_text.strip()}'")
            
            # 尝试登录
            print("\n尝试登录...")
            
            # 根据上面的输出，填写正确的选择器
            # 通常是用户名输入框（type=text 或 placeholder包含用户名相关文字）
            username_inputs = [inp for inp in inputs if 
                              (await inp.get_attribute("type")) in ["text", "email", "tel"] or
                              (await inp.get_attribute("placeholder")).lower() in ["请输入用户名", "用户名", "账号", "username"]]
            
            password_inputs = [inp for inp in inputs if 
                              (await inp.get_attribute("type")) == "password" or
                              (await inp.get_attribute("placeholder")).lower() in ["请输入密码", "密码", "password"]]
            
            if username_inputs:
                await username_inputs[0].fill("admin")
                print("已填写用户名")
            else:
                print("未找到用户名输入框")
                
            if password_inputs:
                await password_inputs[0].fill("admin123")
                print("已填写密码")
            else:
                print("未找到密码输入框")
            
            # 查找登录按钮
            login_buttons = [btn for btn in buttons if 
                           "登录" in await btn.text_content() or
                           "登 录" in await btn.text_content() or
                           "submit" in (await btn.get_attribute("type") or "").lower()]
            
            if login_buttons:
                await login_buttons[0].click()
                print("已点击登录按钮")
            else:
                print("未找到登录按钮")
                
            # 等待登录结果
            await page.wait_for_timeout(5000)
            
            # 检查登录结果
            content = await page.content()
            if "数据源管理" in content or "首页" in content or "欢迎" in content:
                print("✅ 登录成功")
            else:
                print("❌ 登录可能失败")
                # 输出页面内容的一部分用于调试
                print("页面内容片段:", content[:500] + "...")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            # 截图以便调试
            timestamp = int(time.time())
            await page.screenshot(path=f"login_test_failure_{timestamp}.png")
            raise e
        finally:
            await browser.close()


def run_test():
    """运行测试"""
    print("🚀 开始执行登录测试...")
    asyncio.run(test_login())


if __name__ == "__main__":
    run_test()