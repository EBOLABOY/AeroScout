# AeroScout 生产环境部署指南

## 部署信息
- **域名**: AeroScout.izlx.de
- **前端**: https://AeroScout.izlx.de
- **API**: https://AeroScout.izlx.de/api
- **文档**: https://AeroScout.izlx.de/docs

## 系统要求

### 最低配置
- **CPU**: 1核
- **内存**: 2GB
- **存储**: 20GB
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+

### 推荐配置
- **CPU**: 2核
- **内存**: 4GB
- **存储**: 50GB
- **操作系统**: Ubuntu 22.04 LTS

## 🚀 快速部署指南

### 一键部署命令
```bash
# 1. 克隆项目
git clone https://github.com/EBOLABOY/AeroScout.git
cd AeroScout

# 2. 给脚本执行权限
chmod +x first-time-deploy.sh setup-ssl-simple.sh

# 3. 执行首次部署
./first-time-deploy.sh

# 4. 配置SSL证书
./setup-ssl-simple.sh
```

### 部署完成后访问
- **前端**: https://AeroScout.izlx.de
- **API**: https://AeroScout.izlx.de/api
- **文档**: https://AeroScout.izlx.de/docs

---

## 📋 详细部署步骤

### 1. 准备服务器环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组
sudo usermod -aG docker $USER
```

### 2. 上传项目文件

```bash
# 方式1: 使用git克隆（推荐）
git clone https://github.com/EBOLABOY/AeroScout.git
cd AeroScout

# 方式2: 使用scp上传
scp -r ./AeroScout user@your-server-ip:/home/user/

# 方式3: 如果已有项目，更新到最新版本
git pull origin main
```

**注意：** 项目仓库地址为 https://github.com/EBOLABOY/AeroScout

### 3. 配置环境变量

```bash
# 复制环境变量文件
cp .env.production .env

# 编辑环境变量（重要！）
nano .env
```

**必须修改的配置项：**
- `SECRET_KEY`: 设置为强密码 (建议使用: `AeroScout2024!@#$%^&*()_+{}|:<>?[]\\;'\",./-=~`)
- `NEXT_PUBLIC_API_URL`: 确认为正确的后端地址 (https://AeroScout.izlx.de/api)

**环境变量示例：**
```bash
# .env 文件内容
SECRET_KEY=AeroScout2024!@#$%^&*()_+{}|:<>?[]\\;'\",./-=~
NEXT_PUBLIC_API_URL=https://AeroScout.izlx.de/api
```

**安全提醒：**
- SECRET_KEY 用于JWT令牌签名，必须保密
- 生产环境中请使用更复杂的密钥
- 可以使用以下命令生成随机密钥：
  ```bash
  openssl rand -hex 32
  # 或
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

### 4. 部署应用

#### **首次部署（推荐）**

```bash
# Linux/macOS
chmod +x first-time-deploy.sh
./first-time-deploy.sh

# Windows
first-time-deploy.bat
```

首次部署脚本会自动：
- 配置环境变量
- 运行数据库迁移
- 创建默认管理员账户
- 启动所有服务

#### **手动部署**

```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

或者完全手动：

```bash
# 构建并启动服务（使用Nginx反向代理）
docker-compose -f docker-compose.nginx.yml up -d --build

# 查看服务状态
docker-compose -f docker-compose.nginx.yml ps
```

### 5. 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

## 访问地址

部署完成后，您可以通过以下地址访问：

- **前端应用**: https://AeroScout.izlx.de
- **后端API**: https://AeroScout.izlx.de/api
- **API文档**: https://AeroScout.izlx.de/docs

### SSL证书配置

首次部署后需要配置SSL证书：

```bash
# 安装certbot
sudo apt install certbot

# 获取SSL证书
sudo certbot certonly --webroot -w /var/www/certbot -d AeroScout.izlx.de --email 1242772513@izlx.de --agree-tos

# 重启Nginx
docker-compose -f docker-compose.nginx.yml restart nginx
```

或者使用提供的脚本：

```bash
chmod +x setup-ssl-simple.sh
./setup-ssl-simple.sh
```

## 默认管理员账户

首次部署后，系统会自动创建一个默认管理员账户：

- **邮箱**: 1242772513@qq.com
- **密码**: 1242772513
- **权限**: 管理员

**⚠️ 重要提醒**：
1. 请在首次登录后立即修改默认密码
2. 该账户拥有完整的管理员权限
3. 可以创建邀请码和管理其他用户

## 监控和维护

### 查看服务状态
```bash
# 使用Nginx配置
docker-compose -f docker-compose.nginx.yml ps

# 检查所有容器健康状态
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose -f docker-compose.nginx.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.nginx.yml logs -f nginx
docker-compose -f docker-compose.nginx.yml logs -f backend
docker-compose -f docker-compose.nginx.yml logs -f frontend
docker-compose -f docker-compose.nginx.yml logs -f celery

# 查看最近的错误日志
docker-compose -f docker-compose.nginx.yml logs --tail=50 backend
```

### 重启服务
```bash
# 重启所有服务
docker-compose -f docker-compose.nginx.yml restart

# 重启特定服务
docker-compose -f docker-compose.nginx.yml restart nginx
docker-compose -f docker-compose.nginx.yml restart backend
```

### 更新应用
```bash
# 拉取最新代码
git pull origin main

# 重新构建并部署
docker-compose -f docker-compose.nginx.yml down
docker-compose -f docker-compose.nginx.yml up -d --build

# 检查更新后的服务状态
docker-compose -f docker-compose.nginx.yml ps
```

### SSL证书续期
```bash
# 手动续期证书
sudo certbot renew

# 重启Nginx以加载新证书
docker-compose -f docker-compose.nginx.yml restart nginx

# 设置自动续期（添加到crontab）
echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose -f $(pwd)/docker-compose.nginx.yml restart nginx" | sudo crontab -
```

### 使用监控脚本
```bash
chmod +x monitor.sh
./monitor.sh
```

## 备份和恢复

### 数据备份
```bash
# 创建备份目录
mkdir -p backups

# 备份数据库
docker cp aeroscout-backend:/app/aeroscout.db ./backups/aeroscout_$(date +%Y%m%d).db

# 备份配置文件
cp .env ./backups/
cp docker-compose.prod.yml ./backups/
```

### 自动备份脚本
```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /path/to/backup_script.sh
```

## 性能优化

### 1. 启用Nginx反向代理
```bash
# 安装Nginx
sudo apt install nginx

# 复制配置文件
sudo cp nginx.conf /etc/nginx/sites-available/aeroscout
sudo ln -s /etc/nginx/sites-available/aeroscout /etc/nginx/sites-enabled/

# 重启Nginx
sudo systemctl restart nginx
```

### 2. 配置HTTPS（推荐）
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. 数据库优化
- 考虑升级到PostgreSQL（高并发场景）
- 定期清理日志文件
- 监控磁盘空间使用

## 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   # 查看详细错误信息
   docker-compose -f docker-compose.nginx.yml logs

   # 检查特定服务
   docker-compose -f docker-compose.nginx.yml logs nginx
   docker-compose -f docker-compose.nginx.yml logs backend
   ```

2. **域名无法访问**
   ```bash
   # 检查域名解析
   nslookup AeroScout.izlx.de
   dig AeroScout.izlx.de

   # 检查Nginx状态
   docker-compose -f docker-compose.nginx.yml logs nginx

   # 测试HTTP访问
   curl -I http://AeroScout.izlx.de
   curl -I https://AeroScout.izlx.de
   ```

3. **SSL证书问题**
   ```bash
   # 检查证书状态
   sudo certbot certificates

   # 测试证书续期
   sudo certbot renew --dry-run

   # 检查证书文件
   sudo ls -la /etc/letsencrypt/live/AeroScout.izlx.de/
   ```

4. **端口被占用**
   ```bash
   # 查看端口使用情况
   sudo netstat -tlnp | grep :80
   sudo netstat -tlnp | grep :443
   ```

5. **内存不足**
   ```bash
   # 查看内存使用
   free -h
   docker stats

   # 重启服务释放内存
   docker-compose -f docker-compose.nginx.yml restart
   ```

6. **磁盘空间不足**
   ```bash
   # 查看磁盘使用
   df -h

   # 清理Docker
   docker system prune -a
   docker volume prune

   # 清理日志文件
   sudo journalctl --vacuum-time=7d
   ```

### 日志位置
```bash
# Docker容器日志
docker logs aeroscout-nginx
docker logs aeroscout-backend
docker logs aeroscout-frontend
docker logs aeroscout-celery

# 使用docker-compose查看日志
docker-compose -f docker-compose.nginx.yml logs nginx
docker-compose -f docker-compose.nginx.yml logs backend

# 系统日志
sudo tail -f /var/log/syslog
sudo journalctl -u docker -f

# SSL证书日志
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

## 安全建议

1. **定期更新系统和Docker**
2. **使用强密码和SSH密钥**
3. **配置防火墙规则**
4. **启用HTTPS**
5. **定期备份数据**
6. **监控系统资源和日志**

## 📞 联系支持

如果遇到问题，请：
1. 查看日志文件
2. 检查系统资源
3. 参考故障排除部分
4. 联系技术支持

**联系方式：**
- 邮箱: 1242772513@izlx.de
- 微信: Xinx--1996
- GitHub: https://github.com/EBOLABOY/AeroScout

---

## 📋 部署检查清单

### 部署前检查
- [ ] 服务器满足最低配置要求
- [ ] 域名 AeroScout.izlx.de 已正确解析
- [ ] 防火墙已开放 80 和 443 端口
- [ ] Docker 和 Docker Compose 已安装

### 部署过程检查
- [ ] 项目代码已从 GitHub 克隆
- [ ] 环境变量已正确配置
- [ ] 首次部署脚本执行成功
- [ ] SSL 证书配置完成
- [ ] 所有服务容器正常运行

### 部署后验证
- [ ] 前端页面可正常访问 (https://AeroScout.izlx.de)
- [ ] API 接口正常响应 (https://AeroScout.izlx.de/api)
- [ ] API 文档可访问 (https://AeroScout.izlx.de/docs)
- [ ] 默认管理员账户可正常登录
- [ ] SSL 证书有效且自动续期已配置

### 安全检查
- [ ] SECRET_KEY 已设置为强密码
- [ ] 默认管理员密码已修改
- [ ] 防火墙规则已正确配置
- [ ] SSL 证书有效期正常

**🎉 恭喜！AeroScout 已成功部署到生产环境！**
