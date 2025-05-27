# AeroScout 生产环境迁移指南

## 🎯 目标配置

- **域名**: AeroScout.izlx.de
- **前端**: https://AeroScout.izlx.de
- **后端API**: https://AeroScout.izlx.de/api
- **SSL证书**: Let's Encrypt 自动管理
- **反向代理**: Nginx

## 📋 迁移步骤

### 步骤1: 准备服务器环境

#### 1.1 服务器要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **内存**: 最少2GB，推荐4GB
- **存储**: 最少20GB，推荐50GB
- **网络**: 公网IP，域名已解析

#### 1.2 域名解析配置
确保域名已正确解析到服务器IP：
```bash
# 检查域名解析
nslookup AeroScout.izlx.de
dig AeroScout.izlx.de

# 应该返回你的服务器IP: 47.79.39.147
```

### 步骤2: 上传代码到服务器

#### 方法1: 使用Git（推荐）
```bash
# 在服务器上
git clone <your-repository-url> AeroScout
cd AeroScout

# 或者如果已有仓库
git pull origin main
```

#### 方法2: 使用SCP上传
```bash
# 在本地环境
# 压缩项目（排除不必要文件）
tar -czf aeroscout.tar.gz \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='aeroscout-frontend/node_modules' \
  --exclude='aeroscouthq_backend/__pycache__' \
  --exclude='aeroscouthq_backend/logs' \
  --exclude='.env' \
  AeroScout/

# 上传到服务器
scp aeroscout.tar.gz user@47.79.39.147:/home/user/

# 在服务器上解压
ssh user@47.79.39.147
cd /home/user
tar -xzf aeroscout.tar.gz
cd AeroScout
```

#### 方法3: 使用rsync同步
```bash
# 在本地环境
rsync -avz --exclude='node_modules' \
  --exclude='.git' \
  --exclude='aeroscout-frontend/node_modules' \
  --exclude='aeroscouthq_backend/__pycache__' \
  --exclude='aeroscouthq_backend/logs' \
  --exclude='.env' \
  ./ user@47.79.39.147:/home/user/AeroScout/
```

### 步骤3: 执行生产环境部署

#### 3.1 使用自动部署脚本（推荐）
```bash
# 在服务器上
cd AeroScout
chmod +x deploy-production.sh
./deploy-production.sh
```

#### 3.2 手动部署步骤
如果自动脚本失败，可以手动执行：

```bash
# 1. 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 2. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. 配置防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 4. 创建环境变量文件
cat > .env << EOF
NEXT_PUBLIC_API_URL=https://AeroScout.izlx.de/api
SECRET_KEY=$(openssl rand -base64 32)
DOMAIN=AeroScout.izlx.de
EMAIL=1242772513@izlx.de
EOF

# 5. 获取SSL证书
sudo mkdir -p /var/www/certbot /etc/letsencrypt

# 临时启动nginx获取证书
docker run --rm -d --name temp-nginx -p 80:80 -v /var/www/certbot:/var/www/certbot nginx:alpine

# 获取证书
docker run --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/www/certbot:/var/www/certbot \
  certbot/certbot \
  certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email 1242772513@izlx.de \
  --agree-tos --no-eff-email \
  -d AeroScout.izlx.de -d www.AeroScout.izlx.de

# 停止临时nginx
docker stop temp-nginx

# 6. 启动生产环境
docker-compose -f docker-compose.production.yml up -d --build
```

### 步骤4: 验证部署

#### 4.1 检查服务状态
```bash
# 查看容器状态
docker-compose -f docker-compose.production.yml ps

# 查看日志
docker-compose -f docker-compose.production.yml logs -f

# 检查健康状态
curl -k https://AeroScout.izlx.de/health
curl -k https://AeroScout.izlx.de/api/health
```

#### 4.2 测试功能
1. **访问前端**: https://AeroScout.izlx.de
2. **测试登录**: 使用默认管理员账户
   - 邮箱: 1242772513@qq.com
   - 密码: 1242772513
3. **测试API**: https://AeroScout.izlx.de/api/docs
4. **测试搜索功能**: 进行一次完整的航班搜索

### 步骤5: 安全配置

#### 5.1 修改默认密码
1. 登录系统
2. 进入用户设置
3. 修改管理员密码为强密码

#### 5.2 配置SSL证书自动续期
```bash
# 添加到crontab
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/local/bin/docker-compose -f $(pwd)/docker-compose.production.yml exec certbot renew --quiet && /usr/local/bin/docker-compose -f $(pwd)/docker-compose.production.yml restart nginx") | crontab -
```

#### 5.3 配置监控
```bash
# 创建监控脚本
cat > monitor-production.sh << 'EOF'
#!/bin/bash
cd /path/to/AeroScout
docker-compose -f docker-compose.production.yml ps
curl -s https://AeroScout.izlx.de/health || echo "Frontend health check failed"
curl -s https://AeroScout.izlx.de/api/health || echo "Backend health check failed"
EOF

chmod +x monitor-production.sh

# 添加到crontab（每5分钟检查一次）
(crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/AeroScout/monitor-production.sh") | crontab -
```

## 🔧 常用运维命令

### 服务管理
```bash
# 查看服务状态
docker-compose -f docker-compose.production.yml ps

# 重启所有服务
docker-compose -f docker-compose.production.yml restart

# 重启单个服务
docker-compose -f docker-compose.production.yml restart frontend
docker-compose -f docker-compose.production.yml restart backend

# 查看日志
docker-compose -f docker-compose.production.yml logs -f
docker-compose -f docker-compose.production.yml logs -f backend

# 停止服务
docker-compose -f docker-compose.production.yml down

# 完全重新部署
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d --build
```

### 数据库管理
```bash
# 进入后端容器
docker exec -it aeroscout-backend bash

# 运行数据库迁移
docker exec -it aeroscout-backend alembic upgrade head

# 创建管理员账户
docker exec -it aeroscout-backend python init_default_admin.py
```

### SSL证书管理
```bash
# 手动续期证书
docker-compose -f docker-compose.production.yml exec certbot renew

# 检查证书状态
docker-compose -f docker-compose.production.yml exec certbot certificates
```

## 🚨 故障排除

### 常见问题

1. **域名无法访问**
   - 检查域名解析
   - 检查防火墙设置
   - 检查nginx配置

2. **SSL证书获取失败**
   - 确认域名已正确解析
   - 检查80端口是否开放
   - 查看certbot日志

3. **服务启动失败**
   - 检查Docker和Docker Compose版本
   - 查看容器日志
   - 检查端口占用

4. **API无法访问**
   - 检查后端容器状态
   - 查看nginx代理配置
   - 检查网络连接

### 日志查看
```bash
# 查看所有服务日志
docker-compose -f docker-compose.production.yml logs

# 查看特定服务日志
docker-compose -f docker-compose.production.yml logs backend
docker-compose -f docker-compose.production.yml logs frontend
docker-compose -f docker-compose.production.yml logs nginx

# 实时查看日志
docker-compose -f docker-compose.production.yml logs -f
```

## 📞 技术支持

如果遇到问题，请：
1. 查看相关日志文件
2. 检查服务状态
3. 参考故障排除部分
4. 联系技术支持: 1242772513@izlx.de
