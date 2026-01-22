# --- 第一阶段：基础镜像和依赖安装 ---
# 使用官方 Python 3.11 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录，后续的指令都在这个目录下执行
WORKDIR /app

# 设置环境变量（可选，用于代理或调整 pip 行为）
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_RETRIES=3

# 复制依赖文件
COPY requirements.txt .

# 设置 pip 镜像源并安装依赖（使用清华源）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口（如果你的应用需要）
EXPOSE 8000

# 运行应用
CMD ["python", "main.py"]