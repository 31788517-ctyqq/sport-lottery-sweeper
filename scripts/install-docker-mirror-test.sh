#!/bin/bash
# 安装脚本

set -e

SCRIPT_NAME="docker-mirror-test"
SCRIPT_CONTENT=$(cat << 'EOF'
#!/bin/bash
# Docker镜像加速器性能测试工具
# 版本: 2.0
# 作者: Docker用户

set -euo pipefail

# 配置
CONFIG_FILE="/etc/docker/daemon.json"
BACKUP_DIR="/var/backup/docker"
LOG_DIR="/var/log/docker-tools"
EOF
# 这里接上面优化后的完整脚本内容
# ...
EOF
)

# 创建必要的目录
sudo mkdir -p "$BACKUP_DIR" "$LOG_DIR"
sudo chmod 755 "$BACKUP_DIR" "$LOG_DIR"

# 安装脚本到系统目录
echo "$SCRIPT_CONTENT" | sudo tee "/usr/local/bin/$SCRIPT_NAME" > /dev/null
sudo chmod +x "/usr/local/bin/$SCRIPT_NAME"

# 创建配置文件（默认镜像源）
sudo mkdir -p /etc/docker-tools
sudo tee /etc/docker-tools/mirrors.list > /dev/null << 'EOF'
# 常用Docker镜像加速器
https://registry.docker-cn.com
https://hub-mirror.c.163.com
https://docker.mirrors.ustc.edu.cn
https://mirror.ccs.tencentyun.com

# 注释掉不使用的镜像源
# https://example.com/mirror
EOF

# 创建手册页
sudo tee /usr/share/man/man1/docker-mirror-test.1 > /dev/null << 'EOF'
.TH DOCKER-MIRROR-TEST 1 "2024" "Docker Tools" "用户手册"
.SH NAME
docker-mirror-test \- 测试Docker镜像加速器性能
.SH SYNOPSIS
.B docker-mirror-test
.RI [ IMAGE_NAME ]
.SH DESCRIPTION
该工具用于测试不同Docker镜像加速器的下载速度和可用性。
.SH EXAMPLES
.TP
.B sudo docker-mirror-test
测试默认镜像(alpine:latest)
.TP
.B sudo docker-mirror-test ubuntu:20.04
测试特定镜像
.SH FILES
.I /etc/docker-tools/mirrors.list
镜像源列表配置文件
.I /var/log/docker-tools/
日志目录
.SH SEE ALSO
docker(1), systemctl(1)
EOF

# 创建自动完成
sudo tee /etc/bash_completion.d/docker-mirror-test > /dev/null << 'EOF'
_docker_mirror_test_completion() {
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    case "$prev" in
        docker-mirror-test)
            COMPREPLY=($(compgen -W "alpine ubuntu centos nginx redis" -- "$cur"))
            ;;
    esac
}
complete -F _docker_mirror_test_completion docker-mirror-test
EOF

echo "✅ 安装完成！"
echo ""
echo "使用方法："
echo "  sudo $SCRIPT_NAME                  # 测试默认镜像"
echo "  sudo $SCRIPT_NAME ubuntu:20.04     # 测试特定镜像"
echo ""
echo "自定义镜像源："
echo "  vim /etc/docker-tools/mirrors.list"