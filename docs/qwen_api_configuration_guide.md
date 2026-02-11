# 阿里云通义千问API配置指南

## 概述

本文档介绍了如何将阿里云通义千问API配置到体育彩票扫盘系统的智能体开发中。我们使用的是DashScope的OpenAI兼容模式API端点。

## API端点

- **API地址**: `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`
- **文档参考**: [DashScope API文档](https://help.aliyun.com/zh/dashscope/developer-reference/use-qwen-by-calling-the-compatible-openai-api)

## 配置步骤

### 1. 获取API Key

1. 登录 [阿里云控制台](https://home.console.aliyun.com/)
2. 访问 [DashScope管理控制台](https://dashscope.console.aliyun.com/)
3. 在"API-KEY管理"页面中创建一个新的API Key

### 2. 配置环境变量

将获取的API Key添加到项目根目录的 `.env` 文件中：

```bash
QWEN_API_KEY=your-qwen-api-key-here
```

或者，在部署环境中设置环境变量：

```bash
export QWEN_API_KEY=your-qwen-api-key-here
```

### 3. 验证配置

启动应用后，系统会自动检测 `QWEN_API_KEY` 环境变量并注册Qwen提供商。如果配置成功，您将在日志中看到类似以下的消息：

```
INFO:LLM服务已初始化
INFO:Qwen提供商已注册
INFO:默认LLM提供商: qwen
```

## 在代码中使用

### 通过LLM服务调用

```python
from backend.main import llm_service

# 使用Qwen模型生成响应
response = await llm_service.generate_response(
    prompt="请分析这场比赛的关键因素",
    provider="qwen",
    model="qwen-max",  # 或其他支持的模型名称
    temperature=0.7
)
```

### 支持的模型

- `qwen-max` - 最强版本，适用于复杂任务
- `qwen-plus` - 平衡版本，兼顾性能和成本
- `qwen-turbo` - 快速版本，适用于简单任务
- `qwen-7b-chat` - 7B参数量的聊天模型
- 更多模型请参考 [通义千问模型列表](https://dashscope.console.aliyun.com/models)

## 故障排除

### API调用失败

1. 检查API Key是否正确配置
2. 检查网络连接是否正常访问 `dashscope.aliyuncs.com`
3. 检查API调用频率是否超过限制

### 权限问题

确保API Key具有调用所需模型的权限。

## 成本管理

系统会自动追踪API调用的成本，可以通过以下API获取成本指标：

```
GET /api/v1/llm/cost-metrics
```

## 注意事项

- 请妥善保管API Key，避免泄露
- 定期检查API使用量和费用
- 根据实际需求选择合适的模型和参数
- 合理设置 `temperature` 和 `max_tokens` 参数以控制成本和输出质量