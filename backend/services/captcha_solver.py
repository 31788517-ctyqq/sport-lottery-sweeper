"""
打码服务模块
用于集成第三方打码服务或人工打码功能
"""
import logging
import time
import requests
import os
import random
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver


logger = logging.getLogger(__name__)


class CaptchaSolver(ABC):
    """
    打码服务抽象基类
    """
    
    @abstractmethod
    def solve_captcha(self, captcha_image_url: str) -> str:
        """
        解决验证码
        :param captcha_image_url: 验证码图片URL
        :return: 验证码结果
        """
        pass


class ManualCaptchaSolver(CaptchaSolver):
    """
    人工打码服务实现
    """
    
    def solve_captcha(self, captcha_image_url: str) -> str:
        """
        人工解决验证码
        :param captcha_image_url: 验证码图片URL
        :return: 验证码结果
        """
        logger.info(f"需要人工解决验证码，请访问: {captcha_image_url}")
        
        # 在实际应用中，这里应该连接到一个人工打码平台
        # 目前只是模拟人工输入
        logger.debug(f"请访问以下链接查看验证码: {captcha_image_url}")
        user_input = input("请输入验证码: ")
        return user_input


class YunDamaCaptchaSolver(CaptchaSolver):
    """
    云打码服务实现
    """
    
    def __init__(self):
        """
        初始化打码服务
        """
        self.username = os.getenv('YUNDAMA_USERNAME', '')
        self.password = os.getenv('YUNDAMA_PASSWORD', '')
        self.app_id = os.getenv('YUNDAMA_APP_ID', '')
        self.app_key = os.getenv('YUNDAMA_APP_KEY', '')
        self.base_url = "http://api.yundama.com/api.php"
        
        # 验证账户信息
        if not self.verify_account():
            logger.warning("打码服务账户验证失败")
    
    def verify_account(self) -> bool:
        """
        验证账户信息
        :return: 验证结果
        """
        try:
            params = {
                'method': 'balance',
                'username': self.username,
                'password': self.password,
                'appid': self.app_id,
                'appkey': self.app_key
            }
            
            response = requests.post(self.base_url, data=params)
            result = response.json()
            
            if result.get('ret') == 0:
                logger.info(f"打码服务账户余额: {result.get('balance')}")
                return True
            else:
                logger.error(f"打码服务账户验证失败: {result.get('desc')}")
                return False
        except Exception as e:
            logger.error(f"打码服务账户验证异常: {str(e)}")
            return False
    
    def solve_captcha(self, captcha_image_url: str) -> str:
        """
        通过第三方服务解决验证码
        :param captcha_image_url: 验证码图片URL
        :return: 验证码结果
        """
        try:
            # 下载验证码图片
            image_response = requests.get(captcha_image_url)
            if image_response.status_code != 200:
                raise Exception("下载验证码图片失败")
            
            # 准备上传参数
            params = {
                'method': 'upload',
                'username': self.username,
                'password': self.password,
                'appid': self.app_id,
                'appkey': self.app_key,
                'codetype': '1004',  # 4位字母数字验证码
                'timeout': '60'
            }
            
            # 上传图片
            files = {'file': ('captcha.jpg', image_response.content, 'image/jpeg')}
            response = requests.post(self.base_url, data=params, files=files)
            result = response.json()
            
            if result.get('ret') == 0:
                captcha_id = result.get('cid')
                logger.info(f"验证码上传成功，ID: {captcha_id}")
                
                # 轮询结果
                for i in range(30):  # 最多等待30次
                    time.sleep(2)
                    check_params = {
                        'method': 'result',
                        'cid': captcha_id,
                        'username': self.username,
                        'password': self.password
                    }
                    
                    check_response = requests.post(self.base_url, data=check_params)
                    check_result = check_response.json()
                    
                    if check_result.get('ret') == 0 and check_result.get('data'):
                        captcha_text = check_result['data']['text']
                        logger.info(f"验证码识别成功: {captcha_text}")
                        return captcha_text
                    elif check_result.get('ret') == -3003:  # 未完成
                        continue
                    else:
                        logger.error(f"验证码识别失败: {check_result}")
                        break
                
                logger.error("验证码识别超时")
                return ""
            else:
                logger.error(f"验证码上传失败: {result.get('desc')}")
                return ""
        except Exception as e:
            logger.error(f"验证码识别异常: {str(e)}")
            return ""


class ChaoJiYingCaptchaSolver(CaptchaSolver):
    """
    超级鹰打码服务实现
    """
    
    def __init__(self):
        """
        初始化超级鹰打码服务
        """
        self.username = os.getenv('CHAOJIYING_USERNAME', '')
        self.password = os.getenv('CHAOJIYING_PASSWORD', '')
        self.soft_id = os.getenv('CHAOJIYING_SOFT_ID', '')
        self.kind = os.getenv('CHAOJIYING_KIND', '1004')  # 验证码类型
        self.base_url = "http://upload.chaojiying.net/Upload/Processing.php"
    
    def solve_captcha(self, captcha_image_url: str) -> str:
        """
        通过超级鹰服务解决验证码
        :param captcha_image_url: 验证码图片URL
        :return: 验证码结果
        """
        try:
            # 下载验证码图片
            image_response = requests.get(captcha_image_url)
            if image_response.status_code != 200:
                raise Exception("下载验证码图片失败")
            
            # 准备上传参数
            params = {
                'user': self.username,
                'pass2': self.password,
                'softid': self.soft_id,
                'codetype': self.kind
            }
            
            # 上传图片
            files = {'userfile': ('captcha.jpg', image_response.content, 'image/jpeg')}
            response = requests.post(self.base_url, data=params, files=files)
            result = response.json()
            
            if result.get('err_no') == 0:
                captcha_text = result.get('pic_str', '')
                logger.info(f"超级鹰验证码识别成功: {captcha_text}")
                return captcha_text
            else:
                logger.error(f"超级鹰验证码识别失败: {result.get('err_str', 'Unknown error')}")
                return ""
        except Exception as e:
            logger.error(f"超级鹰验证码识别异常: {str(e)}")
            return ""


class CaptchaIntegration:
    """
    验证码集成服务，用于处理页面中的验证码
    """
    
    def __init__(self, solver: CaptchaSolver):
        """
        初始化验证码集成服务
        :param solver: 验证码解决器
        """
        self.solver = solver
        # 从环境变量获取配置
        self.captcha_detection_timeout = int(os.getenv('CAPTCHA_DETECTION_TIMEOUT', '30'))
        self.captcha_retry_attempts = int(os.getenv('CAPTCHA_RETRY_ATTEMPTS', '3'))
        self.captcha_retry_delay = float(os.getenv('CAPTCHA_RETRY_DELAY', '2.0'))
    
    def handle_captcha_on_page(self, driver: WebDriver, captcha_selector: str = None, 
                               input_selector: str = None, 
                               submit_selector: str = None) -> bool:
        """
        处理页面上的验证码
        :param driver: WebDriver实例
        :param captcha_selector: 验证码图片选择器
        :param input_selector: 验证码输入框选择器
        :param submit_selector: 提交按钮选择器
        :return: 是否成功处理验证码
        """
        try:
            # 使用配置中的选择器或默认值
            # 默认选择器
            default_selectors = {
                'captcha_img': 'img[src*="captcha"], .verify-img, #captcha, .vcode, [alt*="验证码"], [title*="验证码"]',
                'captcha_input': 'input[name="captcha"], input[name="verify"], input#captcha, input.vcode, input[placeholder*="验证码"]',
                'submit_btn': 'button[type="submit"], .submit-btn, #submit, [onclick*="submit"]',
                'verify_btn': '.verify-btn, #verify, button.verify, [onclick*="verify"]'
            }
            
            captcha_selector = captcha_selector or default_selectors['captcha_img']
            input_selector = input_selector or default_selectors['captcha_input']
            submit_selector = submit_selector or default_selectors['submit_btn']
            
            # 等待验证码元素出现
            captcha_element = WebDriverWait(driver, self.captcha_detection_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, captcha_selector))
            )
            
            # 获取验证码图片URL
            captcha_url = captcha_element.get_attribute('src')
            if not captcha_url:
                # 尝试获取data-src属性（懒加载图片）
                captcha_url = captcha_element.get_attribute('data-src')
            
            if not captcha_url:
                logger.error("未能获取验证码图片URL")
                return False
            
            # 确保URL是完整的
            if captcha_url.startswith('//'):
                captcha_url = 'https:' + captcha_url
            elif captcha_url.startswith('/'):
                current_url = driver.current_url
                base_url = '/'.join(current_url.split('/')[:3])
                captcha_url = base_url + captcha_url
            
            # 解决验证码
            for attempt in range(self.captcha_retry_attempts):
                captcha_text = self.solver.solve_captcha(captcha_url)
                if captcha_text:
                    logger.info(f"第{attempt+1}次尝试，验证码识别结果: {captcha_text}")
                    break
                else:
                    logger.warning(f"第{attempt+1}次尝试验证码识别失败，等待后重试...")
                    time.sleep(self.captcha_retry_delay)
            
            if not captcha_text:
                logger.error("多次尝试后验证码识别仍然失败")
                return False
            
            # 输入验证码
            captcha_input = driver.find_element(By.CSS_SELECTOR, input_selector)
            captcha_input.clear()
            captcha_input.send_keys(captcha_text)
            
            # 等待一段时间模拟人操作
            time.sleep(random.uniform(0.5, 1.5))
            
            # 点击提交按钮
            submit_button = driver.find_element(By.CSS_SELECTOR, submit_selector)
            submit_button.click()
            
            logger.info("验证码处理完成并已提交")
            return True
            
        except Exception as e:
            logger.error(f"处理页面验证码时发生异常: {str(e)}")
            return False
    
    def is_captcha_present(self, driver: WebDriver, captcha_selector: str = None) -> bool:
        """
        检查页面是否存在验证码
        :param driver: WebDriver实例
        :param captcha_selector: 验证码图片选择器
        :return: 是否存在验证码
        """
        try:
            default_selectors = {
                'captcha_img': 'img[src*="captcha"], .verify-img, #captcha, .vcode, [alt*="验证码"], [title*="验证码"]'
            }
            captcha_selector = captcha_selector or default_selectors['captcha_img']
            
            captcha_elements = driver.find_elements(By.CSS_SELECTOR, captcha_selector)
            return len(captcha_elements) > 0
        except:
            return False


# 验证码解决器工厂
def create_captcha_solver(solver_type: str = None) -> CaptchaSolver:
    """
    创建验证码解决器
    :param solver_type: 解决器类型
    :return: 验证码解决器实例
    """
    # 从环境变量获取服务类型
    service_type = solver_type or os.getenv('CAPTCHA_SERVICE_TYPE', 'manual')
    
    if service_type == 'manual':
        return ManualCaptchaSolver()
    elif service_type == 'yundama':
        return YunDamaCaptchaSolver()
    elif service_type == 'chaojiying':
        return ChaoJiYingCaptchaSolver()
    else:
        logger.warning(f"未知的验证码解决器类型: {service_type}，使用默认人工解决器")
        return ManualCaptchaSolver()


def get_captcha_solver(solver_type: str = None) -> CaptchaSolver:
    """
    获取验证码解决器实例（向后兼容）
    :param solver_type: 解决器类型
    :return: 验证码解决器实例
    """
    return create_captcha_solver(solver_type)


def integrate_with_scraper(scraper_instance):
    """
    将打码服务集成到爬虫实例中
    :param scraper_instance: 爬虫实例
    """
    # 获取验证码解决器
    solver = create_captcha_solver()
    captcha_integration = CaptchaIntegration(solver)
    
    # 将验证码集成服务附加到爬虫实例
    scraper_instance.captcha_integration = captcha_integration
    logger.info("打码服务已集成到爬虫实例中")


if __name__ == "__main__":
    # 示例用法
    logger.debug("打码服务模块已准备就绪")
    logger.debug("当前配置的服务类型:", os.getenv('CAPTCHA_SERVICE_TYPE', 'manual'))