#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 生产环境配置
DOMAIN="AeroScout.izlx.de"
EMAIL="1242772513@izlx.de"
SERVER_IP="47.79.39.147"

echo -e "${BLUE}========================================"
echo -e "    AeroScout 生产环境部署脚本"
echo -e "========================================"
echo -e "域名: ${DOMAIN}"
echo -e "服务器: ${SERVER_IP}"
echo -e "========================================${NC}"
echo

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}请不要使用root用户运行此脚本${NC}"
   exit 1
fi

# 确认部署
read -p "确认部署到生产环境? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo -e "${RED}部署已取消${NC}"
    exit 1
fi

echo
echo -e "${GREEN}🚀 开始生产环境部署...${NC}"
echo

# 1. 更新系统
echo -e "${YELLOW}📦 更新系统包...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. 安装必要软件
echo -e "${YELLOW}🔧 安装必要软件...${NC}"
sudo apt install -y curl wget git ufw

# 3. 安装 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}🐳 安装 Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    echo -e "${GREEN}✅ Docker 已安装${NC}"
fi

# 4. 安装 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}🔨 安装 Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo -e "${GREEN}✅ Docker Compose 已安装${NC}"
fi

# 5. 配置防火墙
echo -e "${YELLOW}🔥 配置防火墙...${NC}"
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 6. 创建必要目录
echo -e "${YELLOW}📁 创建必要目录...${NC}"
sudo mkdir -p /var/www/certbot
sudo mkdir -p /etc/letsencrypt

# 7. 设置环境变量
echo -e "${YELLOW}⚙️ 配置环境变量...${NC}"
cat > .env << EOF
# AeroScout 生产环境配置
NEXT_PUBLIC_API_URL=https://${DOMAIN}/api
SECRET_KEY=$(openssl rand -base64 32)
DOMAIN=${DOMAIN}
EMAIL=${EMAIL}
EOF

echo -e "${GREEN}✅ 环境变量配置完成${NC}"

# 8. 停止现有服务
echo -e "${YELLOW}🛑 停止现有服务...${NC}"
docker-compose -f docker-compose.production.yml down 2>/dev/null || true

# 9. 获取 SSL 证书
echo -e "${YELLOW}🔒 获取 SSL 证书...${NC}"

# 临时启动 nginx 用于证书验证
docker run --rm -d \
  --name temp-nginx \
  -p 80:80 \
  -v /var/www/certbot:/var/www/certbot \
  nginx:alpine

# 等待 nginx 启动
sleep 5

# 获取证书
docker run --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/www/certbot:/var/www/certbot \
  certbot/certbot \
  certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email ${EMAIL} \
  --agree-tos \
  --no-eff-email \
  -d ${DOMAIN} \
  -d www.${DOMAIN}

# 停止临时 nginx
docker stop temp-nginx 2>/dev/null || true

# 10. 构建并启动服务
echo -e "${YELLOW}🔨 构建并启动服务...${NC}"
docker-compose -f docker-compose.production.yml up -d --build

# 11. 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 60

# 12. 检查服务状态
echo -e "${YELLOW}📊 检查服务状态...${NC}"
docker-compose -f docker-compose.production.yml ps

# 13. 设置证书自动续期
echo -e "${YELLOW}🔄 设置证书自动续期...${NC}"
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/local/bin/docker-compose -f $(pwd)/docker-compose.production.yml exec certbot renew --quiet && /usr/local/bin/docker-compose -f $(pwd)/docker-compose.production.yml restart nginx") | crontab -

echo
echo -e "${BLUE}========================================"
echo -e "    🎉 生产环境部署完成!"
echo -e "========================================"
echo -e "${GREEN}🌐 访问地址:${NC}"
echo -e "  前端: https://${DOMAIN}"
echo -e "  后端API: https://${DOMAIN}/api"
echo -e "  API文档: https://${DOMAIN}/api/docs"
echo
echo -e "${GREEN}👤 默认管理员账户:${NC}"
echo -e "  邮箱: 1242772513@qq.com"
echo -e "  密码: 1242772513"
echo
echo -e "${YELLOW}📝 重要提醒:${NC}"
echo -e "  1. 请立即修改默认管理员密码"
echo -e "  2. SSL证书已配置自动续期"
echo -e "  3. 防火墙已配置完成"
echo -e "  4. 如需重启Docker服务: sudo systemctl restart docker"
echo
echo -e "${BLUE}🔍 常用命令:${NC}"
echo -e "  查看日志: docker-compose -f docker-compose.production.yml logs -f"
echo -e "  重启服务: docker-compose -f docker-compose.production.yml restart"
echo -e "  停止服务: docker-compose -f docker-compose.production.yml down"
echo -e "========================================${NC}"
