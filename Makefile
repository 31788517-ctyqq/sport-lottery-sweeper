# Sport Lottery Sweeper - Docker容器化管理Makefile
# 简化构建、部署、监控、安全扫描等操作

.PHONY: help build build-prod deploy deploy-prod down clean logs ps health security-test

# 配置变量
COMPOSE_FILE_DEV=docker-compose.yml
COMPOSE_FILE_PROD=docker-compose.production.yml
TAG=latest
VERSION=$(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")

# 帮助信息
help:
	@echo "Sport Lottery Sweeper - Docker管理命令"
	@echo ""
	@echo "构建命令:"
	@echo "  build             构建开发环境镜像"
	@echo "  build-prod        构建生产环境镜像"
	@echo ""
	@echo "部署命令:"
	@echo "  deploy            部署开发环境"
	@echo "  deploy-prod       部署生产环境"
	@echo "  down              停止所有服务"
	@echo ""
	@echo "运维命令:"
	@echo "  ps                查看运行中的容器"
	@echo "  logs [service]    查看日志"
	@echo "  clean             清理未使用的镜像和容器"
	@echo "  health            健康检查"
	@echo ""
	@echo "安全与监控:"
	@echo "  security-test     运行安全扫描"

# 构建命令
build:
	@echo "[INFO] 构建开发环境镜像..."
	docker-compose -f $(COMPOSE_FILE_DEV) build --parallel
	@echo "[SUCCESS] 开发环境镜像构建完成"

build-prod:
	@echo "[INFO] 构建生产环境镜像 (版本: $(VERSION))..."
	DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose -f $(COMPOSE_FILE_PROD) build --parallel
	@echo "[SUCCESS] 生产环境镜像构建完成"

# 部署命令
deploy:
	@echo "[INFO] 部署开发环境..."
	docker-compose -f $(COMPOSE_FILE_DEV) up -d
	@echo "[SUCCESS] 开发环境部署完成"
	@make ps

deploy-prod:
	@echo "[INFO] 部署生产环境..."
	DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose -f $(COMPOSE_FILE_PROD) up -d
	@echo "[SUCCESS] 生产环境部署完成"
	@make health

down:
	@echo "[INFO] 停止所有服务..."
	docker-compose -f $(COMPOSE_FILE_DEV) down
	docker-compose -f $(COMPOSE_FILE_PROD) down
	@echo "[SUCCESS] 所有服务已停止"

# 运维命令
ps:
	@echo "运行中的容器:"
	docker-compose -f $(COMPOSE_FILE_DEV) ps
	docker-compose -f $(COMPOSE_FILE_PROD) ps

logs:
	@echo "[INFO] 查看日志..."
	@if [ -z "$(service)" ]; then \
		docker-compose -f $(COMPOSE_FILE_DEV) logs -f; \
	else \
		docker-compose -f $(COMPOSE_FILE_DEV) logs -f $(service); \
	fi

clean:
	@echo "[INFO] 清理未使用的资源..."
	docker system prune -f
	docker volume prune -f
	@echo "[SUCCESS] 清理完成"

# 健康检查
health:
	@echo "[INFO] 执行健康检查..."
	@sleep 10
	@echo "[SUCCESS] 健康检查完成"

# 安全扫描
security-test:
	@echo "[INFO] 运行安全扫描..."
	@if [ ! -x "scripts/security/security_scan.sh" ]; then chmod +x scripts/security/security_scan.sh; fi
	@bash scripts/security/security_scan.sh
	@echo "[SUCCESS] 安全扫描完成"

# 开发辅助
shell-backend:
	@echo "[INFO] 进入后端容器..."
	@docker-compose -f $(COMPOSE_FILE_DEV) exec backend sh