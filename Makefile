.PHONY: help install dev test clean

# 默认显示帮助
help:
	@echo "可用的make命令:"
	@echo "  install    安装项目依赖"
	@echo "  dev        启动开发服务器"
	@echo "  test       运行测试"
	@echo "  clean      清理构建文件"

# 安装依赖
install:
	pip install -e .

# 启动开发服务器
dev:
	uvicorn src.backend.main:app --reload

# 运行测试
test:
	python -m pytest tests/

# 清理构建文件
clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage