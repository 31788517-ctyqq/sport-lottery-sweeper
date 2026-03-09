# 阿里云轻量服务器部署北单过滤器页面指南

## 概述

本文档详细介绍如何将`http://localhost:3000/admin/beidan-filter`页面功能部署到阿里云轻量服务器，包括前端页面和后端服务的完整部署流程。

**文档版本**: v1.0  
**作者**: 系统助手  
**更新日期**: 2026-02-16  
**文档ID**: BD-DEPLOY-GUIDE-001

## 一、准备工作

### 1.1 阿里云轻量服务器配置要求

- 推荐配置：2核4G内存，5M带宽
- 操作系统：Ubuntu 20.04 LTS 或更高版本
- 确保服务器已开通且处于运行状态

### 1.2 安全组规则配置

在阿里云控制台配置安全组规则：

| 端口范围 | 授权对象 | 协议类型 | 说明 |
|----------|----------|----------|------|
| 80/80    | 0.0.0.0/0 | TCP      | HTTP访问 |
| 443/443  | 0.0.0.0/0 | TCP      | HTTPS访问 |
| 3000/3000| 0.0.0.0/0 | TCP      | 前端调试（可选） |

### 1.3 本地开发环境准备

- 确保本地项目已完全运行正常
- 确认`http://localhost:3000/admin/beidan-filter`页面功能完整

## 二、前端页面部署

### 2.1 构建前端静态资源

在本地项目目录执行以下命令：

```bash
cd frontend
npm run build
```

执行后会在`frontend/dist`目录生成构建后的静态文件。

### 2.2 上传构建文件

推荐使用SFTP工具（如FileZilla）上传文件：

- 主机：阿里云服务器公网IP
- 用户名：root
- 端口：22
- 上传路径：`/www/beidan-filter`

### 2.3 配置Nginx服务

登录阿里云服务器并执行以下命令：

```bash
# 创建项目目录
mkdir -p /www/beidan-filter

# 安装Nginx
sudo apt update && sudo apt install nginx -y

# 创建Nginx配置文件
sudo cat > /etc/nginx/sites-available/beidan-filter <<EOF
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或服务器IP

    # 前端页面配置
    location / {
        root /www/beidan-filter;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API代理配置（连接到后端服务）
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 启用配置
sudo ln -s /etc/nginx/sites-available/beidan-filter /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

## 三、后端服务部署

### 3.1 服务器环境配置

```bash
# 更新系统包
sudo apt update

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv -y

# 安装Git
sudo apt install git -y

# 安装Supervisor（用于保持服务常驻）
sudo apt install supervisor -y
```

### 3.2 部署后端代码

```bash
# 克隆代码到服务器
sudo mkdir -p /opt/sport-lottery
sudo chown $USER:$USER /opt/sport-lottery
cd /opt/sport-lottery

# 这里使用git clone或上传本地代码
git clone 你的代码仓库地址 .  # 或手动上传代码

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 配置Supervisor管理后端服务

```bash
# 创建Supervisor配置文件
sudo cat > /etc/supervisor/conf.d/backend.conf <<EOF
[program:backend]
command=/opt/sport-lottery/venv/bin/python backend_start_8000.py
directory=/opt/sport-lottery
autostart=true
autorestart=true
stderr_logfile=/var/log/beidan-backend.err.log
stdout_logfile=/var/log/beidan-backend.out.log
user=root
environment=PATH="/opt/sport-lottery/venv/bin"
EOF

# 重载Supervisor配置
sudo supervisorctl reload
```

## 四、环境变量与配置

### 4.1 前端环境变量

修改前端的环境配置，确保API请求能正确代理到后端：

```bash
# 修改 frontend/.env.production
VITE_API_BASE_URL=http://your-server-ip/api
```

重新构建并部署后，再执行构建命令：

```bash
npm run build
# 重新上传dist目录内容
```

### 4.2 后端环境变量

确保后端的配置文件适应生产环境：

```bash
# 在服务器的项目根目录创建或修改 .env 文件
DATABASE_URL=sqlite:////opt/sport-lottery/data/sport_lottery.db
# 或使用PostgreSQL
# DATABASE_URL=postgresql://username:password@localhost/dbname
```

## 五、HTTPS配置（推荐）

为了安全访问，建议配置SSL证书：

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com
```

Certbot会自动修改Nginx配置以启用HTTPS。

## 六、验证部署

### 6.1 访问页面

打开浏览器访问：
```
http://your-server-ip/admin/beidan-filter
```
或使用域名：
```
https://your-domain.com/admin/beidan-filter
```

### 6.2 检查关键配置

```bash
# 检查Nginx配置
sudo nginx -T | grep -A 10 'server_name your-domain.com'

# 检查后端服务状态
sudo supervisorctl status backend

# 检查API连接
curl -I http://localhost:8000/health
```

## 七、高级配置建议

### 7.1 缓存优化

在Nginx配置中添加静态资源缓存：

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 7.2 安全头配置

在Nginx配置中添加安全头：

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

### 7.3 日志轮转

配置日志轮转以避免日志文件过大：

```bash
sudo nano /etc/logrotate.d/beidan-app
```

添加以下内容：

```
/var/log/beidan-backend*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0640 root root
    postrotate
        supervisorctl restart backend
    endscript
}
```

## 八、故障排除

### 8.1 常见问题

1. **页面无法访问**
   - 检查安全组规则是否开启相应端口
   - 检查Nginx服务状态：`sudo systemctl status nginx`

2. **API请求失败**
   - 检查后端服务是否正常运行：`sudo supervisorctl status backend`
   - 检查Nginx代理配置是否正确

3. **静态资源404错误**
   - 检查前端构建文件是否完整上传
   - 确认Nginx配置中的root路径是否正确

### 8.2 调试命令

```bash
# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log

# 查看后端服务日志
sudo tail -f /var/log/beidan-backend*.log

# 检查端口占用情况
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8000
```

## 九、维护与更新

### 9.1 更新前端页面

```bash
# 在本地重新构建
cd frontend
npm run build

# 上传新的dist目录内容到服务器的/www/beidan-filter目录
# 无需重启服务，静态文件会自动更新
```

### 9.2 更新后端服务

```bash
# 登录服务器更新代码
cd /opt/sport-lottery
git pull origin main

# 如有依赖更新
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo supervisorctl restart backend
```

## 十、性能优化建议

1. **启用Gzip压缩**
   在Nginx配置中启用gzip压缩以减少传输数据量

2. **数据库优化**
   - 定期对数据库进行维护
   - 添加必要的索引以提高查询性能

3. **缓存策略**
   - 对静态资源启用长期缓存
   - 考虑使用Redis缓存API响应

4. **监控告警**
   - 设置服务器资源监控
   - 配置应用健康检查

---

> **注意**：首次部署建议先通过`http://服务器IP:3000`直接访问前端调试，确认功能正常后再配置Nginx。如果遇到问题，可通过`journalctl -u nginx -f`实时查看Nginx日志。