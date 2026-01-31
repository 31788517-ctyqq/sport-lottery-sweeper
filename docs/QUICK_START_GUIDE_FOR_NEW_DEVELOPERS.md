# 新开发者快速入门指南

## 项目概览

体育彩票扫盘系统是一个专业的足球数据采集、分析和预测平台，结合了传统数据科学技术和现代AI技术，包括大语言模型(LLM)、智能体系统等AI原生能力。

### 核心功能
- **数据采集**：从多个博彩公司抓取实时赔率数据
- **预测分析**：使用机器学习和LLM进行比赛预测
- **智能决策**：智能体系统自动执行对冲策略
- **个性化服务**：基于用户画像的个性化推荐

### 技术栈
- **后端**：Python + FastAPI + SQLAlchemy + Celery
- **前端**：Vue 3 + TypeScript + Tailwind CSS
- **数据库**：PostgreSQL (生产) / SQLite (开发)
- **AI/LLM**：OpenAI API, Google Gemini, 通义千问
- **部署**：Docker + Docker Compose

## 环境搭建

### 1. 前置要求
```bash
# 系统要求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- pnpm
```

### 2. 克隆项目
```bash
git clone <repository-url>
cd sport-lottery-sweeper
```

### 3. 安装后端依赖
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器依赖
playwright install chromium
```

### 4. 安装前端依赖
```bash
cd frontend
pnpm install
```

### 5. 配置环境变量
复制 `.env.example` 为 `.env` 并填入相应配置：
```bash
cp .env.example .env
```

特别是AI相关的API密钥：
```bash
# .env 文件
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here  
QWEN_API_KEY=your_qwen_api_key_here
```

## 项目结构

```
├── backend/                 # 后端代码
│   ├── agents/             # AI智能体
│   ├── api/                # API路由
│   ├── models/             # 数据模型
│   ├── services/           # 业务服务
│   │   ├── llm_service.py  # LLM服务
│   │   └── ...            # 其他服务
│   └── main.py             # 应用入口
├── frontend/               # 前端代码
├── docs/                   # 文档
├── scripts/                # 脚本
├── tests/                  # 测试
└── docker/                 # Docker配置
```

## 核心模块详解

### 1. LLM服务 (AI核心)
位于 `backend/services/llm_service.py`，提供统一的LLM接口：

```python
# 使用示例
from backend.main import llm_service

# 生成响应
response = await llm_service.generate_response(
    prompt="分析这场比赛的关键因素",
    provider="qwen"  # 或 "openai", "gemini"
)
```

### 2. 智能体系统
位于 `backend/agents/` 目录，包括：

- **BaseAgent**：智能体基类
- **OddsMonitorAgent**：监控赔率变化
- **RecommendationAgent**：个性化推荐
- **协作预测网络**：多智能体协作完成复杂任务

### 3. 实时推理服务
位于 `backend/services/lightweight_inference_service.py`，提供低延迟推理能力。

## 运行项目

### 1. 后端开发模式
```bash
# 启动后端
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或使用启动脚本
./scripts/start-dev-simple.sh
```

### 2. 前端开发模式
```bash
cd frontend
pnpm run dev
```

### 3. Docker部署
```bash
# 启动完整环境
docker-compose up -d

# 查看服务状态
docker-compose ps
```

## AI能力开发

### 1. 添加新的LLM提供商
创建新的提供商类继承 `BaseLLMProvider`：

```python
from backend.services.llm_service import BaseLLMProvider

class NewProviderLLM(BaseLLMProvider):
    def __init__(self, api_key: str):
        # 初始化提供商客户端
        pass
        
    async def generate_response(self, prompt: str, **kwargs) -> str:
        # 实现生成响应的逻辑
        pass
```

然后在 `LLMService` 中注册：

```python
# 在 init_llm_service() 函数中
llm_service.register_provider("new_provider", api_key)
```

### 2. 创建新的智能体
继承 `BaseAgent` 类：

```python
from backend.agents.base_agent import BaseAgent

class MyNewAgent(BaseAgent):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 实现智能体逻辑
        pass
```

### 3. 智能体间通信
使用 `CommunicationHub` 和 `Message` 类实现智能体间通信：

```python
from backend.agents.communication_protocol import CommunicationHub, Message, MessageType

# 发送消息
message = Message(
    MessageType.REQUEST,
    self.name,
    "target_agent",
    {"data": "content"}
)
await self.comm_hub.send_message(message)
```

## 代码规范

### 1. Python规范
- 使用 `black` 格式化代码 (`black .`)
- 使用 `isort` 排序导入 (`isort .`)
- 遵循 PEP 8 规范
- 添加类型注解

### 2. 前端规范
- 使用 TypeScript
- 组件遵循单一职责原则
- 使用 ESLint 和 Prettier

### 3. 文档规范
- 函数和类需包含 docstring
- 复杂逻辑需添加注释
- API 端点需在 Swagger 中文档化

## 调试技巧

### 1. 后端调试
```python
# 使用日志
from backend.logging import logger
logger.info("Debug message")

# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 前端调试
- 使用浏览器开发者工具
- Vue DevTools
- 网络请求面板检查API调用

### 3. LLM调试
- 查看LLM请求日志
- 检查API使用量和成本
- 验证API密钥有效性

## 常见问题

### 1. API密钥问题
- 检查 `.env` 文件中的API密钥
- 确认API密钥有效性
- 检查提供商账户余额

### 2. 数据库连接问题
- 检查数据库服务是否运行
- 确认数据库连接字符串
- 运行数据库迁移

### 3. 爬虫被封禁
- 检查IP池系统
- 调整请求频率
- 更新反检测策略

## 测试

### 1. 单元测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_specific_module.py
```

### 2. 集成测试
```bash
# 运行集成测试
pytest tests/integration/
```

### 3. AI功能测试
```bash
# 运行AI增强功能测试
python test_ai_enhancements.py
```

## 贡献指南

### 1. 分支策略
- `main`：生产就绪代码
- `develop`：开发分支
- `feature/*`：功能分支
- `hotfix/*`：紧急修复

### 2. 提交规范
- 使用语义化提交信息
- 例如：`feat: 添加新的LLM提供商` 或 `fix: 修复智能体通信问题`

### 3. PR流程
1. Fork仓库
2. 创建功能分支
3. 提交更改
4. 确保测试通过
5. 提交PR并等待审查

## 学习资源

### 1. 内部文档
- [PROJECT_OVERVIEW_LATEST.md](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/docs/PROJECT_OVERVIEW_LATEST.md)：项目最新概述
- [AI_ARCHITECTURE_DEEP_DIVE.md](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/docs/AI_ARCHITECTURE_DEEP_DIVE.md)：AI架构深度解析
- [PROJECT_STANDARDS.md](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/PROJECT_STANDARDS.md)：项目开发标准

### 2. 外部资源
- FastAPI文档
- Vue 3文档
- OpenAI API文档
- 机器学习资源

## 联系方式

如遇问题，请联系：
- 项目负责人
- 查阅相关文档
- 提交GitHub Issue