#!/bin/bash
# scripts/start-with-llm.sh

echo "启动支持LLM功能的体育彩票系统..."

# 检查必需的环境变量
if [ -z "$OPENAI_API_KEY" ] && [ -z "$GEMINI_API_KEY" ] && [ -z "$QWEN_API_KEY" ]; then
    echo "警告: 未设置任何LLM API密钥，LLM功能将不可用"
fi

# 启动后端服务
echo "启动后端服务..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

echo "服务启动完成!"