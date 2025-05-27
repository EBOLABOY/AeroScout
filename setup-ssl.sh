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
echo -e "    AeroScout SSL证书配置脚本"
echo -e "    域名: $DOMAIN"
echo -e "========================================${NC}"
echo

# 检查是否为root用户或有sudo权限
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}检测到root用户${NC}"
elif ! sudo -n true 2>/dev/null; then
   echo -e "${YELLOW}需要sudo权限来安装证书${NC}"
   echo "请确保当前用户有sudo权限"
fi

echo -e "${YELLOW}SSL配置信息:${NC}"
echo "  域名: $DOMAIN"
echo "  邮箱: $EMAIL"
echo "  证书类型: Let's Encrypt"
echo

read -p "确认开始SSL配置? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo -e "${RED}SSL配置已取消${NC}"
    exit 1
fi

echo
echo -e "${GREEN}🔒 开始SSL证书配置...${NC}"
echo

# 检查域名解析
echo -e "${YELLOW}🔍 检查域名解析...${NC}"
if ! nslookup $DOMAIN > /dev/null 2>&1; then
    echo -e "${RED}❌ 域名解析失败，请检查DNS配置${NC}"
    echo "请确保 $DOMAIN 已正确解析到当前服务器IP"
    exit 1
fi

echo -e "${GREEN}✅ 域名解析正常${NC}"

# 安装certbot
echo -e "${YELLOW}📦 安装Certbot...${NC}"
if ! command -v certbot &> /dev/null; then
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y certbot
    elif command -v yum &> /dev/null; then
        sudo yum install -y certbot
    else
        echo -e "${RED}❌ 无法自动安装certbot，请手动安装${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Certbot安装完成${NC}"

# 创建webroot目录
echo -e "${YELLOW}📁 创建webroot目录...${NC}"
sudo mkdir -p /var/www/certbot

# 确保服务正在运行
echo -e "${YELLOW}🔄 确保服务正在运行...${NC}"
docker-compose -f docker-compose.domain.yml up -d

# 等待服务启动
sleep 10

# 测试HTTP访问
echo -e "${YELLOW}🌐 测试HTTP访问...${NC}"
if ! curl -f http://$DOMAIN/.well-known/acme-challenge/test 2>/dev/null; then
    echo -e "${YELLOW}⚠️  HTTP访问测试失败，但继续尝试获取证书${NC}"
fi

# 获取SSL证书
echo -e "${YELLOW}🔐 获取SSL证书...${NC}"
sudo certbot certonly \
    --webroot \
    -w /var/www/certbot \
    -d $DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive \
    --force-renewal

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSL证书获取成功${NC}"
    
    # 重启Nginx以加载证书
    echo -e "${YELLOW}🔄 重启Nginx服务...${NC}"
    docker-compose -f docker-compose.domain.yml restart nginx
    
    # 等待服务重启
    sleep 10
    
    # 测试HTTPS访问
    echo -e "${YELLOW}🔒 测试HTTPS访问...${NC}"
    if curl -f https://$DOMAIN/health 2>/dev/null; then
        echo -e "${GREEN}✅ HTTPS访问测试成功${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTPS访问测试失败，请检查配置${NC}"
    fi
    
    echo
    echo -e "${BLUE}========================================"
    echo -e "    🎉 SSL配置完成!"
    echo -e "========================================${NC}"
    echo
    echo -e "${GREEN}📋 访问地址:${NC}"
    echo "  HTTPS: https://$DOMAIN"
    echo "  API: https://$DOMAIN/api"
    echo "  文档: https://$DOMAIN/docs"
    echo
    echo -e "${GREEN}🔒 证书信息:${NC}"
    echo "  证书路径: /etc/letsencrypt/live/$DOMAIN/"
    echo "  有效期: 90天"
    echo "  自动续期: 建议配置cron任务"
    echo
    echo -e "${YELLOW}📝 自动续期配置:${NC}"
    echo "  添加到crontab: 0 12 * * * /usr/bin/certbot renew --quiet"
    echo "  重启命令: docker-compose -f docker-compose.domain.yml restart nginx"
    
else
    echo -e "${RED}❌ SSL证书获取失败${NC}"
    echo
    echo -e "${YELLOW}可能的原因:${NC}"
    echo "  1. 域名未正确解析到当前服务器"
    echo "  2. 防火墙阻止了80端口访问"
    echo "  3. 服务未正常启动"
    echo
    echo -e "${YELLOW}排查建议:${NC}"
    echo "  1. 检查域名解析: nslookup $DOMAIN"
    echo "  2. 检查防火墙: sudo ufw status"
    echo "  3. 检查服务状态: docker-compose -f docker-compose.domain.yml ps"
    echo "  4. 查看日志: docker-compose -f docker-compose.domain.yml logs nginx"
    
    exit 1
fi

echo
