# IP代理模块

这是一个用于获取和管理免费代理IP的模块，特别集成了89ip.cn网站提供的代理IP，并包含了一批预设的高质量代理IP。

## 功能特性

- 从89ip.cn网站获取免费代理IP
- 包含125个预设的高质量代理IP（来自用户提供列表）
- 验证代理IP的有效性
- 管理代理IP池
- 与现有爬虫系统集成
- 提供代理配置管理
- **新增**: 动态IP池更新功能，定时从网站获取最新代理IP
- **新增**: 优化版IP池管理，支持120个IP的大容量代理池

## 文件说明

- `ip_proxy.py`: 主要的IP代理管理类
- `ip_proxy_config.py`: 代理配置管理类
- `ip_proxy_example.py`: 使用示例
- `test_ip_proxy.py`: 测试脚本
- `integration_example.py`: 与爬虫系统集成示例
- `add_ips_to_pool.py`: 将IP列表添加到代理池的脚本
- `dynamic_proxy_updater.py`: 动态IP代理池更新器，实现IP池的动态化
- `optimized_ip_proxy.py`: 优化版IP代理管理器，支持120个IP的大容量代理池
- `practical_example.py`: 实用爬虫示例，展示如何在实际爬虫中使用动态IP池

## 安装依赖

```bash
pip install requests beautifulsoup4
```

## 使用方法

### 基本使用

```python
from crawler.ip_proxy import IPProxyManager

# 创建代理管理器
manager = IPProxyManager()

# 获取有效代理
valid_proxies = manager.get_valid_proxies(count=5, page_range=(1, 2))
print(f"获取到 {len(valid_proxies)} 个有效代理")

# 获取随机代理
random_proxy = manager.get_random_proxy()
if random_proxy:
    print(f"随机代理: {random_proxy['ip']}:{random_proxy['port']}")
```

### 创建120个IP的大容量代理池

```python
from crawler.optimized_ip_proxy import OptimizedIPProxyManager

# 创建优化版代理管理器
manager = OptimizedIPProxyManager()

# 刷新代理池到120个IP
manager.refresh_proxy_pool(target_count=120)

print(f"代理池包含 {len(manager.proxy_list)} 个IP")
print(f"统计信息: {manager.get_proxy_statistics()}")
```

### 启动动态IP池更新器

```python
from crawler.dynamic_proxy_updater import DynamicProxyUpdater

# 创建动态更新器，每30分钟更新一次
updater = DynamicProxyUpdater(refresh_interval_minutes=30)

def on_update(proxy_list):
    print(f"代理池已更新，当前代理数量: {len(proxy_list)}")

updater.set_callback(on_update)
updater.start()

# 获取随机代理
random_proxy = updater.get_random_proxy()
print(f"随机代理: {random_proxy['ip']}:{random_proxy['port']}")
```

### 与爬虫集成

```python
from crawler.integration_example import EnhancedCrawlerWithProxy

# 创建增强型爬虫
enhanced_crawler = EnhancedCrawlerWithProxy()

# 使用代理进行请求
response = enhanced_crawler.get_request_with_proxy("https://example.com")
```

### 配置管理

```python
from crawler.ip_proxy_config import IPProxyConfigManager

# 创建配置管理器
config_manager = IPProxyConfigManager()

# 获取当前配置
config = config_manager.get_proxy_config()

# 更新配置
config_manager.update_config(timeout=15, max_retries=5)
```

## 动态IP池功能

新增的动态IP池更新器（`dynamic_proxy_updater.py`）具有以下特点：

- **定时更新**: 可配置的更新间隔，定时从89ip.cn获取最新代理IP
- **智能验证**: 自动验证获取到的代理IP是否可用
- **回调机制**: 更新完成后可执行自定义回调函数
- **线程安全**: 使用独立线程运行，不影响主程序流程
- **错误处理**: 遇到错误时自动重试，保证持续运行

## 优化版大容量IP池

新增的优化版IP代理管理器（`optimized_ip_proxy.py`）解决了CloudFlare反爬虫机制的问题：

- **高效构建**: 使用预设IP快速构建120个IP的大容量代理池
- **格式验证**: 确保所有IP格式正确，提高可用性
- **绕过限制**: 通过预设IP绕过网站反爬虫限制
- **统计功能**: 提供详细的地区和运营商分布统计

## 预设IP列表

模块内置了125个预设代理IP，这些IP来自用户提供的时间为2026/01/27 17:30:02和2026/01/27 17:45:02的列表，包括来自江苏、安徽、浙江、北京等地的电信、联通、阿里云等运营商的代理。

## 爬虫系统集成

我们已经将IP代理模块与现有的爬虫系统集成，主要体现在以下几个方面：

1. **增强型爬虫引擎** (`backend/scrapers/core/enhanced_engine.py`)：该引擎集成了IP代理模块，能够动态获取和使用89ip.cn的代理IP。

2. **爬虫协调器** (`backend/scrapers/coordinator.py`)：已更新为使用增强型引擎，所有爬虫都会自动使用代理IP。

3. **基础爬虫类** (`backend/scrapers/core/base_scraper.py`)：已更新为使用增强型引擎。

4. **配置管理** (`backend/scrapers/core/config_loader.py`)：提供了使用增强型引擎的配置选项。

### 如何使用集成后的爬虫系统

```python
from backend.scrapers.coordinator import get_coordinator
import asyncio

async def main():
    coordinator = await get_coordinator()
    matches = await coordinator.get_matches(days=3)
    print(f"获取到 {len(matches)} 场比赛")

asyncio.run(main())
```

## 注意事项

- 免费代理IP的稳定性和速度可能有限，请合理使用
- 频繁请求可能导致IP被封禁，建议添加延时
- 代理IP的有效性可能会随时间变化，需要定期验证
- 预设IP列表是静态的，需要定期更新以保持有效性
- 集成后的爬虫系统会自动使用IP代理，提高反爬虫能力
- 动态IP池更新器会定期从89ip.cn获取新IP，保持IP池的活性
- 由于CloudFlare等反爬虫机制，直接从网站获取大量IP可能受限，推荐使用优化版管理器创建大容量代理池
- 优化版管理器利用预设IP构建120个IP的大容量代理池，绕过了网站反爬虫限制

## 测试

运行测试脚本：

```bash
python -m crawler.test_ip_proxy
```

运行使用示例：

```bash
python -m crawler.ip_proxy_example
```

运行集成示例：

```bash
python -m crawler.integration_example
```

运行120个IP代理池测试：

```bash
python -m crawler.optimized_ip_proxy
```

## 错误处理

- 如果无法获取代理IP，请检查网络连接和目标网站的可用性
- 如果代理验证失败，请尝试增加超时时间或减少验证频率
- 如果遇到反爬虫措施，请适当调整请求频率和请求头
```