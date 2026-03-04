# 远程生产发布 Runbook（SSH + 域名 + 证书 + 反向代理）

本方案基于以下文件：
- `docker-compose.edge.yml`
- `deploy/nginx/nginx.edge.template.conf`
- `deploy/remote/setup-prod.sh`
- `scripts/deploy/remote-publish.ps1`

## 1. 前置条件

1. 域名 `A` 记录已指向服务器公网 IP（根域名 + `www`）。
2. 服务器系统为 Ubuntu，且可 SSH 登录。
3. 本机具备 `ssh`、`scp`、`tar` 命令。
4. 服务器放通端口：`22`、`80`、`443`。

## 2. 一键发布（在本机 PowerShell 执行）

```powershell
.\scripts\deploy\remote-publish.ps1 `
  -HostName "<服务器IP或域名>" `
  -UserName "<SSH用户名>" `
  -Domain "<你的域名>" `
  -CertbotEmail "<证书通知邮箱>" `
  -SshKeyPath "C:\Users\<你>\.ssh\id_rsa"
```

发布动作会自动完成：
1. 上传当前项目代码包到远程服务器。
2. 安装 Docker / Docker Compose（如未安装）。
3. 启动生产容器栈（后端、前端、Postgres、Redis、Nginx 反向代理）。
4. 自动申请 Let's Encrypt 证书并热加载 Nginx。

## 3. 服务架构

1. `reverse-proxy (nginx)`：暴露 `80/443`，做 HTTPS 与反向代理。
2. `frontend`：仅内网暴露 `80`，由 Nginx 反代。
3. `backend`：仅内网暴露 `8000`，由 Nginx 反代 `/api` 和 `/ws`。
4. `postgres`、`redis`：仅内网访问。

## 4. 发布后检查

```bash
docker compose -f docker-compose.edge.yml ps
curl -I https://<你的域名>/
curl https://<你的域名>/api/v1/health/live
```

## 5. 证书续期

远程已生成脚本：

```bash
deploy/remote/renew-certs.sh <域名> <邮箱> /opt/sport-lottery-sweeper
```

建议加入 `crontab`（每天 2 次）：

```bash
0 3,15 * * * /opt/sport-lottery-sweeper/deploy/remote/renew-certs.sh <域名> <邮箱> /opt/sport-lottery-sweeper >> /var/log/sls-cert-renew.log 2>&1
```

## 6. Rollback (Auto + Manual)

`scripts/deploy/remote-publish.ps1` now creates a backup before each deploy:

- Backup directory: `${RemoteDir}_backups`
- File pattern: `sls_release_backup_<timestamp>.tar.gz`
- Retention: latest 5 backups
- Auto rollback: if remote deploy fails, it restores the previous backup and reruns `setup-prod.sh`

Manual rollback on server:

```bash
REMOTE_DIR=/opt/sport-lottery-sweeper
BACKUP_DIR="${REMOTE_DIR}_backups"
LATEST_BACKUP=$(ls -1t "$BACKUP_DIR"/sls_release_backup_*.tar.gz | head -n 1)

find "$REMOTE_DIR" -mindepth 1 -maxdepth 1 ! -name deploy -exec rm -rf {} +
tar -xzf "$LATEST_BACKUP" -C "$REMOTE_DIR"

cd "$REMOTE_DIR"
chmod +x deploy/remote/setup-prod.sh
./deploy/remote/setup-prod.sh "<domain>" "<certbot-email>" "$REMOTE_DIR"
```
