# AeroScout 生产环境部署指南

## 服务器信息
- **IPv4地址**: 47.79.39.147
- **IPv6地址**: 240b:4009:25a:1801:ffff:64f7:fd92:e919

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

## 部署步骤

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
# 方式1: 使用git克隆
git clone <your-repo-url>
cd AeroScout

# 方式2: 使用scp上传
scp -r ./AeroScout user@47.79.39.147:/home/user/
```

### 3. 配置环境变量

```bash
# 复制环境变量文件
cp .env.production .env

# 编辑环境变量（重要！）
nano .env
```

**必须修改的配置项：**
- `SECRET_KEY`: 设置为强密码
- `NEXT_PUBLIC_API_URL`: 确认为正确的后端地址

### 4. 部署应用

```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

或者手动部署：

```bash
# 构建并启动服务
docker-compose -f docker-compose.prod.yml up -d --build

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps
```

### 5. 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 3000  # 前端
sudo ufw allow 8000  # 后端API
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## 访问地址

部署完成后，您可以通过以下地址访问：

- **前端应用**: http://47.79.39.147:3000
- **后端API**: http://47.79.39.147:8000
- **API文档**: http://47.79.39.147:8000/docs

## 监控和维护

### 查看服务状态
```bash
docker-compose -f docker-compose.prod.yml ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f celery
```

### 重启服务
```bash
docker-compose -f docker-compose.prod.yml restart
```

### 更新应用
```bash
# 拉取最新代码
git pull

# 重新构建并部署
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
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
   docker-compose -f docker-compose.prod.yml logs
   ```

2. **端口被占用**
   ```bash
   # 查看端口使用情况
   sudo netstat -tlnp | grep :3000
   sudo netstat -tlnp | grep :8000
   ```

3. **内存不足**
   ```bash
   # 查看内存使用
   free -h
   docker stats
   ```

4. **磁盘空间不足**
   ```bash
   # 清理Docker
   docker system prune -a
   docker volume prune
   ```

### 日志位置
- Docker容器日志: `docker logs <container_name>`
- Nginx日志: `/var/log/nginx/`
- 系统日志: `/var/log/syslog`

## 安全建议

1. **定期更新系统和Docker**
2. **使用强密码和SSH密钥**
3. **配置防火墙规则**
4. **启用HTTPS**
5. **定期备份数据**
6. **监控系统资源和日志**

## 联系支持

如果遇到问题，请：
1. 查看日志文件
2. 检查系统资源
3. 参考故障排除部分
4. 联系技术支持
