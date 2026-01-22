# 使用Python 3.11官方镜像作为基础
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    # 编译依赖
    gcc \
    g++ \
    # PostgreSQL客户端库
    libpq-dev \
    # 爬虫相关依赖
    curl \
    wget \
    # PDF生成依赖
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    # Playwright浏览器依赖
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    # 清理缓存
    && rm -rf /var/lib/apt/lists/*

# 安装Playwright浏览器
RUN pip install playwright==1.40.0 \
    && playwright install chromium \
    && playwright install-deps chromium

# 复制依赖文件
COPY requirements.txt .
COPY requirements-dev.txt .

# 创建虚拟环境并安装生产依赖
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# 第二阶段：运行阶段
FROM python:3.11-slim as runner

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    # Celery设置
    C_FORCE_ROOT=true

# 安装运行时系统依赖
RUN apt-get update && apt-get install -y \
    # PostgreSQL客户端库
    libpq-dev \
    # PDF生成依赖
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    # Playwright浏览器依赖
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    # 进程管理
    supervisor \
    # 网络工具
    curl \
    # 清理缓存
    && rm -rf /var/lib/apt/lists/*

# 从builder阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 创建非root用户
RUN groupadd -r football && useradd -r -g football football \
    && mkdir -p /app/uploads /app/logs /app/data \
    && chown -R football:football /app \
    && chmod -R 755 /app

# 切换用户
USER football

# 复制项目文件
COPY --chown=football:football . .

# 复制supervisor配置
COPY --chown=football:football docker/supervisor/ /etc/supervisor/conf.d/

# 复制启动脚本
COPY --chown=football:football docker/scripts/entrypoint.sh /entrypoint.sh
COPY --chown=football:football docker/scripts/start.sh /start.sh

# 设置执行权限
RUN chmod +x /entrypoint.sh /start.sh

# 创建必要的目录
RUN mkdir -p /app/logs/celery /app/logs/gunicorn /app/logs/uvicorn

# 暴露端口
EXPOSE 8000 5555 9000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 设置入口点
ENTRYPOINT ["/entrypoint.sh"]

# 设置默认命令
CMD ["/start.sh"]