# AeroScout 域名部署指南

## 🎯 部署目标
- **域名**: AeroScout.izlx.de
- **前端**: https://AeroScout.izlx.de
- **API**: https://AeroScout.izlx.de/api
- **文档**: https://AeroScout.izlx.de/docs

## 📋 部署前准备

### 1. 服务器要求
- **操作系统**: Ubuntu 20.04+ (推荐 22.04 LTS)
- **CPU**: 2核心 (最低1核)
- **内存**: 4GB (最低2GB)
- **存储**: 50GB (最低20GB)
- **网络**: 公网IP，支持80和443端口

### 2. 域名配置
确保域名 `AeroScout.izlx.de` 已正确解析到服务器IP：
```bash
# 检查域名解析
nslookup AeroScout.izlx.de
dig AeroScout.izlx.de
```

### 3. 防火墙配置
```bash
# Ubuntu/Debian
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# 检查状态
sudo ufw status
```

## 🚀 快速部署

### 方法一：一键部署脚本
```bash
# 1. 上传项目文件到服务器
scp -r ./AeroScout user@your-server-ip:/home/user/

# 2. 登录服务器
ssh user@your-server-ip

# 3. 进入项目目录
cd AeroScout

# 4. 给脚本执行权限
chmod +x deploy-domain.sh
chmod +x setup-ssl.sh

# 5. 执行部署
./deploy-domain.sh

# 6. 配置SSL证书
./setup-ssl.sh
```

### 方法二：手动部署
```bash
# 1. 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 2. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. 重新登录以应用docker组权限
exit
ssh user@your-server-ip

# 4. 部署应用
cd AeroScout
docker-compose -f docker-compose.domain.yml up -d --build

# 5. 配置SSL证书
sudo apt install certbot
sudo mkdir -p /var/www/certbot
sudo certbot certonly --webroot -w /var/www/certbot -d AeroScout.izlx.de --email 1242772513@izlx.de --agree-tos

# 6. 重启Nginx
docker-compose -f docker-compose.domain.yml restart nginx
```

## 🔧 配置文件说明

### 主要配置文件
- `docker-compose.domain.yml`: 域名部署的Docker配置
- `nginx.domain.conf`: Nginx反向代理配置
- `.env`: 环境变量配置

### 环境变量
```bash
# .env 文件内容
NEXT_PUBLIC_API_URL=https://AeroScout.izlx.de/api
SECRET_KEY=your_generated_secret_key
```

## 📊 服务监控

### 检查服务状态
```bash
# 查看所有服务状态
docker-compose -f docker-compose.domain.yml ps

# 查看服务日志
docker-compose -f docker-compose.domain.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.domain.yml logs -f nginx
docker-compose -f docker-compose.domain.yml logs -f backend
docker-compose -f docker-compose.domain.yml logs -f frontend
```

### 健康检查
```bash
# 检查前端
curl https://AeroScout.izlx.de

# 检查API
curl https://AeroScout.izlx.de/api/health

# 检查API文档
curl https://AeroScout.izlx.de/docs
```

## 🔒 SSL证书管理

### 证书自动续期
```bash
# 添加到crontab
crontab -e

# 添加以下行（每天中午12点检查续期）
0 12 * * * /usr/bin/certbot renew --quiet && docker-compose -f /path/to/AeroScout/docker-compose.domain.yml restart nginx
```

### 手动续期
```bash
sudo certbot renew
docker-compose -f docker-compose.domain.yml restart nginx
```

## 🛠️ 维护操作

### 更新应用
```bash
# 拉取最新代码
git pull

# 重新构建并部署
docker-compose -f docker-compose.domain.yml down
docker-compose -f docker-compose.domain.yml up -d --build
```

### 备份数据
```bash
# 创建备份目录
mkdir -p backups

# 备份数据库
docker cp aeroscout-backend:/app/aeroscout.db ./backups/aeroscout_$(date +%Y%m%d).db

# 备份配置文件
cp .env ./backups/
cp docker-compose.domain.yml ./backups/
```

### 重启服务
```bash
# 重启所有服务
docker-compose -f docker-compose.domain.yml restart

# 重启特定服务
docker-compose -f docker-compose.domain.yml restart nginx
docker-compose -f docker-compose.domain.yml restart backend
```

## 🔍 故障排除

### 常见问题

1. **域名无法访问**
   ```bash
   # 检查域名解析
   nslookup AeroScout.izlx.de
   
   # 检查防火墙
   sudo ufw status
   
   # 检查Nginx状态
   docker-compose -f docker-compose.domain.yml logs nginx
   ```

2. **SSL证书问题**
   ```bash
   # 检查证书状态
   sudo certbot certificates
   
   # 测试证书续期
   sudo certbot renew --dry-run
   
   # 重新获取证书
   sudo certbot delete --cert-name AeroScout.izlx.de
   sudo certbot certonly --webroot -w /var/www/certbot -d AeroScout.izlx.de
   ```

3. **API无法访问**
   ```bash
   # 检查后端服务
   docker-compose -f docker-compose.domain.yml logs backend
   
   # 检查Redis连接
   docker-compose -f docker-compose.domain.yml logs redis
   ```

### 日志位置
- Nginx日志: `docker-compose -f docker-compose.domain.yml logs nginx`
- 后端日志: `docker-compose -f docker-compose.domain.yml logs backend`
- 前端日志: `docker-compose -f docker-compose.domain.yml logs frontend`

## 👤 默认账户信息

部署完成后，系统会自动创建默认管理员账户：
- **邮箱**: 1242772513@qq.com
- **密码**: 1242772513
- **权限**: 管理员

**⚠️ 重要**: 请在首次登录后立即修改默认密码！

## 📞 技术支持

如遇问题，请：
1. 查看相关日志文件
2. 检查服务状态和网络连接
3. 参考故障排除部分
4. 联系技术支持: 1242772513@izlx.de
