# AeroScout 部署指南

## 🚀 服务器部署步骤

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登录以应用Docker组权限
```

### 2. 克隆项目

```bash
# 克隆项目到服务器
git clone https://github.com/your-username/AeroScout.git
cd AeroScout

# 创建环境变量文件
cp .env.example .env
```

### 3. 配置环境变量

编辑 `.env` 文件：

```bash
nano .env
```

填入以下配置：

```env
# 前端配置
NEXT_PUBLIC_API_URL=https://AeroScout.izlx.de/api

# 后端安全配置（请生成强密码）
SECRET_KEY=AeroScout2024!@#$%^&*()_+{}|:<>?[];\',./`~1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ

# 其他配置保持默认即可
```

### 4. 部署选择

#### 选项A：生产环境部署（推荐）

```bash
# 使用生产环境配置部署
docker-compose -f docker-compose.production.yml up -d --build
```

#### 选项B：简单部署

```bash
# 使用简化配置部署
docker-compose -f docker-compose.prod.yml up -d --build
```

### 5. 配置域名和SSL

#### 5.1 域名解析
确保域名 `AeroScout.izlx.de` 解析到您的服务器IP。

#### 5.2 SSL证书（如果使用生产环境配置）
```bash
# 安装Certbot
sudo apt install certbot

# 获取SSL证书
sudo certbot certonly --webroot -w /var/www/certbot -d AeroScout.izlx.de --email 1242772513@izlx.de --agree-tos
```

### 6. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 健康检查
curl http://localhost:8000/health
curl http://localhost:3000
```

### 7. 访问应用

- **前端**：https://AeroScout.izlx.de
- **后端API**：https://AeroScout.izlx.de/api
- **API文档**：https://AeroScout.izlx.de/api/docs

### 8. 默认管理员账户

- **邮箱**：1242772513@qq.com
- **密码**：1242772513

**⚠️ 重要：首次登录后请立即修改密码！**

## 🔧 维护命令

### 更新应用
```bash
git pull
docker-compose down
docker-compose up -d --build
```

### 查看日志
```bash
docker-compose logs -f [service_name]
```

### 备份数据
```bash
docker cp aeroscout-backend:/app/data/aeroscout.db ./backup_$(date +%Y%m%d).db
```

### 重启服务
```bash
docker-compose restart [service_name]
```

## 🔍 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo netstat -tlnp | grep :80
   sudo netstat -tlnp | grep :443
   ```

2. **Docker权限问题**
   ```bash
   sudo usermod -aG docker $USER
   # 重新登录
   ```

3. **域名无法访问**
   ```bash
   # 检查防火墙
   sudo ufw status
   sudo ufw allow 80
   sudo ufw allow 443
   ```

4. **SSL证书问题**
   ```bash
   # 检查证书状态
   sudo certbot certificates
   
   # 续期证书
   sudo certbot renew
   ```

## 📞 支持

如有问题，请联系：
- **邮箱**：1242772513@izlx.de
- **微信**：Xinx--1996
