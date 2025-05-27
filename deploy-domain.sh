#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo -e "    AeroScout 域名部署脚本"
echo -e "    目标域名: AeroScout.izlx.de"
echo -e "========================================${NC}"
echo

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}请不要使用root用户运行此脚本${NC}"
   echo "建议使用普通用户，脚本会在需要时提示输入sudo密码"
   exit 1
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker未安装，请先安装Docker${NC}"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose未安装，请先安装Docker Compose${NC}"
    exit 1
fi

echo -e "${YELLOW}部署配置:${NC}"
echo "  域名: AeroScout.izlx.de"
echo "  前端: https://AeroScout.izlx.de"
echo "  API: https://AeroScout.izlx.de/api"
echo "  默认管理员: 1242772513@qq.com"
echo "  默认密码: 1242772513"
echo

read -p "确认开始部署? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo -e "${RED}部署已取消${NC}"
    exit 1
fi

echo
echo -e "${GREEN}🚀 开始域名部署...${NC}"
echo

# 生成强密钥
SECRET_KEY=$(openssl rand -hex 32)

# 设置环境变量
export NEXT_PUBLIC_API_URL="https://AeroScout.izlx.de/api"
export SECRET_KEY="$SECRET_KEY"

# 写入.env文件
cat > .env << EOF
# AeroScout 域名部署环境变量配置
NEXT_PUBLIC_API_URL=https://AeroScout.izlx.de/api
SECRET_KEY=$SECRET_KEY
EOF

echo -e "${GREEN}✅ 环境变量配置完成${NC}"
echo

# 停止现有服务
echo -e "${YELLOW}🛑 停止现有服务...${NC}"
docker-compose -f docker-compose.domain.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# 清理旧镜像
echo -e "${YELLOW}🧹 清理旧镜像...${NC}"
docker system prune -f

# 创建必要的目录
echo -e "${YELLOW}📁 创建必要的目录...${NC}"
sudo mkdir -p /var/www/certbot
sudo mkdir -p /etc/letsencrypt

# 构建并启动服务（不包含SSL）
echo -e "${YELLOW}🔨 构建并启动服务...${NC}"
docker-compose -f docker-compose.domain.yml up -d --build

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 30

# 检查服务状态
echo -e "${YELLOW}📊 检查服务状态...${NC}"
docker-compose -f docker-compose.domain.yml ps

echo
echo -e "${BLUE}========================================"
echo -e "    🎉 基础部署完成!"
echo -e "========================================${NC}"
echo
echo -e "${GREEN}📋 部署信息:${NC}"
echo "  域名: AeroScout.izlx.de"
echo "  HTTP访问: http://AeroScout.izlx.de"
echo "  API文档: http://AeroScout.izlx.de/docs"
echo
echo -e "${GREEN}👤 默认管理员账户:${NC}"
echo "  邮箱: 1242772513@qq.com"
echo "  密码: 1242772513"
echo "  权限: 管理员"
echo
echo -e "${YELLOW}🔒 SSL证书配置:${NC}"
echo "  1. 确保域名已正确解析到服务器IP"
echo "  2. 运行以下命令获取SSL证书:"
echo "     sudo apt install certbot"
echo "     sudo certbot certonly --webroot -w /var/www/certbot -d AeroScout.izlx.de"
echo "  3. 证书获取成功后，重启Nginx:"
echo "     docker-compose -f docker-compose.domain.yml restart nginx"
echo
echo -e "${BLUE}🔍 查看日志命令:${NC}"
echo "  docker-compose -f docker-compose.domain.yml logs -f"
echo
echo -e "${YELLOW}📝 注意事项:${NC}"
echo "  1. 请确保域名DNS已正确配置"
echo "  2. 防火墙需开放80和443端口"
echo "  3. 首次启动可能需要几分钟时间"
echo "  4. 请及时配置SSL证书并修改默认密码"
echo
