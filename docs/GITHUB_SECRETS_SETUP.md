# GitHub Repository Secrets Configuration Guide
# GitHub仓库Secrets配置指南

## 🔐 Required Secrets for CI/CD Pipeline

### **Infrastructure & Deployment Secrets**
```bash
# Staging Environment
STAGING_HOST=your-staging-server.com
STAGING_USERNAME=deploy-user
STAGING_SSH_KEY=-----BEGIN RSA PRIVATE KEY-----\n...
-----END RSA PRIVATE KEY-----

# Production Environment  
PRODUCTION_HOST=your-production-server.com
PRODUCTION_USERNAME=deploy-user
PRODUCTION_SSH_KEY=-----BEGIN RSA PRIVATE KEY-----\n...
-----END RSA PRIVATE KEY-----
```

### **Database Secrets**
```bash
# PostgreSQL
POSTGRES_USER=sport_lottery_user
POSTGRES_PASSWORD=your_secure_postgres_password

# Redis
REDIS_PASSWORD=your_secure_redis_password
```

### **Application Secrets**
```bash
# Security
SECRET_KEY=your_django_secret_key_min_50_chars
JWT_SECRET_KEY=your_jwt_secret_key_min_50_chars

# External Services
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
GRAFANA_PASSWORD=your_grafana_admin_password
```

### **Container Registry**
```bash
# Docker Hub (if using Docker Hub instead of GHCR)
DOCKERHUB_USERNAME=your_dockerhub_username
DOCKERHUB_TOKEN=your_dockerhub_access_token
```

### **SonarQube Cloud**
```bash
# SonarCloud (already configured in workflow)
SONAR_TOKEN=your_sonarcloud_token
SONAR_ORGANIZATION=your_sonarcloud_org
SONAR_PROJECT_KEY=sport-lottery-sweeper
SONAR_HOST_URL=https://sonarcloud.io
```

## 📋 How to Add Secrets

### **Step 1: Navigate to Repository Settings**
1. Go to your GitHub repository
2. Click on **Settings** tab
3. Scroll down to **Secrets and variables** section
4. Click on **Actions**

### **Step 2: Add New Secret**
1. Click **New repository secret** button
2. Enter **Name** (exactly as shown above)
3. Enter **Value** (the actual secret value)
4. Click **Add secret**

### **Step 3: Verify Secrets**
Ensure all secrets are added correctly:
- ✅ Staging deployment secrets
- ✅ Production deployment secrets  
- ✅ Database credentials
- ✅ Application secrets
- ✅ SSL certificate secrets (if applicable)

## 🔒 Security Best Practices

### **SSH Key Generation**
```bash
# Generate SSH key pair for deployment
ssh-keygen -t rsa -b 4096 -C "deploy@sport-lottery-sweeper" -f ~/.ssh/deploy_key

# Add public key to server authorized_keys
ssh-copy-id -i ~/.ssh/deploy_key.pub user@server

# Use private key content as STAGING_SSH_KEY/PRODUCTION_SSH_KEY
cat ~/.ssh/deploy_key
```

### **Password Generation**
```bash
# Generate secure passwords
openssl rand -base64 32  # For POSTGRES_PASSWORD
openssl rand -base64 24  # For REDIS_PASSWORD
openssl rand -base64 50  # For JWT_SECRET_KEY
```

### **Secret Rotation**
- Rotate secrets every 90 days
- Update GitHub secrets immediately after rotation
- Restart affected services after secret updates

## 🚨 Emergency Procedures

### **If Secrets Are Compromised**
1. Immediately rotate compromised secrets
2. Update GitHub repository secrets
3. Restart all running deployments
4. Review access logs for unauthorized activity
5. Consider rotating related secrets as precaution

### **Access Control**
- Limit repository access to essential team members
- Use GitHub's fine-grained access tokens when possible
- Regularly audit who has admin access to the repository