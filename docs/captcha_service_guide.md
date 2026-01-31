# 打码服务集成指南

## 概述

本文档介绍了如何在项目中使用和配置打码服务，以应对网站的反爬虫机制和验证码保护。

## 配置选项

### 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# 启用打码服务
CAPTCHA_ENABLED=true
CAPTCHA_SERVICE_TYPE=manual  # 可选: manual, yundama, chaojiying, tencent_captcha

# 云打码服务配置
YUNDAMA_USERNAME=your_username
YUNDAMA_PASSWORD=your_password
YUNDAMA_APP_ID=your_app_id
YUNDAMA_APP_KEY=your_app_key

# 超级鹰服务配置
CHAOJIYING_USERNAME=your_username
CHAOJIYING_PASSWORD=your_password
CHAOJIYING_SOFT_ID=your_soft_id
CHAOJIYING_KIND=1004  # 验证码类型

# 腾讯验证码配置
TENCENT_CAPTCHA_APP_ID=your_app_id
TENCENT_CAPTCHA_APP_SECRET=your_app_secret

# 验证码处理配置
CAPTCHA_DETECTION_TIMEOUT=30
CAPTCHA_RETRY_ATTEMPTS=3
CAPTCHA_RETRY_DELAY=2.0
```

## 支持的服务提供商

### 1. 人工打码 (Manual)

- **优点**: 简单易用，无需额外费用
- **缺点**: 效率较低，需要人工干预
- **适用场景**: 测试环境，少量请求

### 2. 云打码 (YunDama)

- **优点**: 自动化处理，速度快
- **缺点**: 需要付费
- **适用场景**: 生产环境，中等请求量

### 3. 超级鹰 (ChaoJiYing)

- **优点**: 识别率高，支持多种验证码类型
- **缺点**: 需要付费
- **适用场景**: 生产环境，高精度需求

### 4. 腾讯验证码 (Tencent Captcha)

- **优点**: 安全性高，集成腾讯防护
- **缺点**: 配置较复杂
- **适用场景**: 高安全性要求场景

## 使用方法

### 在爬虫中集成打码服务

```python
from backend.services.captcha_solver import integrate_with_scraper, get_captcha_solver
from backend.scrapers.sources.super_advanced_five_hundred_scraper import SuperAdvancedFiveHundredScraper

# 创建爬虫实例
scraper = SuperAdvancedFiveHundredScraper()

# 集成打码服务
integrate_with_scraper(scraper)

# 使用爬虫（内部会自动处理验证码）
matches = scraper.get_matches(days=3)
```

### 直接使用打码服务

```python
from backend.services.captcha_solver import create_captcha_solver
from config.captcha_config import get_captcha_config

# 获取配置
config = get_captcha_config()

# 创建解决器
solver = create_captcha_solver('chaojiying', config)

# 解决验证码
captcha_text = solver.solve_captcha('http://example.com/captcha.jpg')
print(f"验证码识别结果: {captcha_text}")
```

## 验证码检测与处理

系统会自动检测以下类型的验证码：

- 图片验证码 (`img[src*='captcha']`)
- 验证码输入框 (`input[name='captcha']`)
- 提交按钮 (`button[type='submit']`)

检测逻辑包括：

1. 页面加载完成后自动检测验证码元素
2. 如果发现验证码，调用相应的解决器处理
3. 自动填充验证码并提交表单
4. 处理失败时自动重试

## 故障排除

### 常见问题

1. **验证码识别失败**
   - 检查网络连接
   - 验证服务提供商账户状态
   - 确认验证码URL可访问

2. **服务认证失败**
   - 检查配置文件中的认证信息
   - 确认用户名密码正确
   - 检查账户余额（付费服务）

3. **选择器不匹配**
   - 更新验证码元素选择器
   - 检查目标网站是否更改了HTML结构

### 日志监控

启用详细日志以监控验证码处理过程：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 扩展性

### 添加新的验证码服务

创建新的解决器类并继承 `CaptchaSolver` 抽象基类：

```python
from backend.services.captcha_solver import CaptchaSolver

class NewCaptchaSolver(CaptchaSolver):
    def __init__(self, config):
        self.config = config
    
    def solve_captcha(self, captcha_image_url):
        # 实现验证码解决逻辑
        pass
```

### 自定义选择器

根据目标网站更新验证码元素选择器：

```python
selectors = {
    'captcha_img': 'your-custom-selector',
    'captcha_input': 'your-input-selector',
    'submit_btn': 'your-submit-selector'
}
```

## 安全注意事项

1. 保护认证信息，不要硬编码在代码中
2. 定期轮换API密钥
3. 限制打码服务的使用频率
4. 监控异常使用情况

## 性能优化

1. 根据请求量选择合适的打码服务
2. 合理设置重试次数和延迟时间
3. 实施缓存机制避免重复处理
4. 使用代理IP轮换减少被封概率