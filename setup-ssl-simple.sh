#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DOMAIN="AeroScout.izlx.de"
EMAIL="1242772513@izlx.de"

echo -e "${BLUE}========================================"
echo -e "    AeroScout SSL证书配置"
echo -e "    域名: $DOMAIN"
echo -e "========================================${NC}"
echo

echo -e "${YELLOW}开始配置SSL证书...${NC}"

# 安装certbot
echo -e "${YELLOW}📦 安装Certbot...${NC}"
sudo apt update
sudo apt install -y certbot

# 创建webroot目录
echo -e "${YELLOW}📁 创建webroot目录...${NC}"
sudo mkdir -p /var/www/certbot

# 获取SSL证书
echo -e "${YELLOW}🔐 获取SSL证书...${NC}"
sudo certbot certonly \
    --webroot \
    -w /var/www/certbot \
    -d $DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSL证书获取成功${NC}"
    
    # 重启Nginx
    echo -e "${YELLOW}🔄 重启Nginx服务...${NC}"
    docker-compose -f docker-compose.nginx.yml restart nginx
    
    echo -e "${GREEN}🎉 SSL配置完成！${NC}"
    echo -e "${GREEN}现在可以通过 https://$DOMAIN 访问应用${NC}"
else
    echo -e "${RED}❌ SSL证书获取失败${NC}"
    echo -e "${YELLOW}请检查域名解析和防火墙设置${NC}"
fi
