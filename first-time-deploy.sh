#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo -e "    AeroScout 首次部署脚本"
echo -e "========================================${NC}"
echo

# 获取用户输入的API地址
read -p "请输入后端API地址 (默认: http://AeroScout.izlx.de/api): " API_URL
API_URL=${API_URL:-http://AeroScout.izlx.de/api}

echo
echo -e "${YELLOW}配置信息:${NC}"
echo "  API地址: $API_URL"
echo "  默认管理员: 1242772513@qq.com"
echo "  默认密码: 1242772513"
echo

read -p "确认开始部署? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo -e "${RED}部署已取消${NC}"
    exit 1
fi

echo
echo -e "${GREEN}🚀 开始首次部署...${NC}"
echo

# 设置环境变量
export NEXT_PUBLIC_API_URL="$API_URL"

# 写入.env文件
cat > .env << EOF
# AeroScout 生产环境配置
NEXT_PUBLIC_API_URL=$API_URL
EOF

echo -e "${GREEN}✅ 环境变量配置完成${NC}"
echo

# 停止现有服务
echo -e "${YELLOW}🛑 停止现有服务...${NC}"
docker-compose -f docker-compose.nginx.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# 清理旧镜像（可选）
echo -e "${YELLOW}🧹 清理旧镜像...${NC}"
docker system prune -f

# 创建必要的目录
echo -e "${YELLOW}📁 创建必要的目录...${NC}"
sudo mkdir -p /var/www/certbot
sudo mkdir -p /etc/letsencrypt

# 构建并启动服务
echo -e "${YELLOW}🔨 构建并启动服务...${NC}"
docker-compose -f docker-compose.nginx.yml up -d --build

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 30

# 检查服务状态
echo -e "${YELLOW}📊 检查服务状态...${NC}"
docker-compose -f docker-compose.nginx.yml ps

echo
echo -e "${BLUE}========================================"
echo -e "    🎉 首次部署完成!"
echo -e "========================================${NC}"
echo
echo -e "${GREEN}📋 部署信息:${NC}"
echo "  前端地址: http://AeroScout.izlx.de"
echo "  后端地址: $API_URL"
echo "  API文档: http://AeroScout.izlx.de/docs"
echo
echo -e "${GREEN}👤 默认管理员账户:${NC}"
echo "  邮箱: 1242772513@qq.com"
echo "  密码: 1242772513"
echo "  权限: 管理员"
echo
echo -e "${YELLOW}📝 注意事项:${NC}"
echo "  1. 首次启动可能需要几分钟时间"
echo "  2. 数据库会自动初始化"
echo "  3. 默认管理员账户会自动创建"
echo "  4. 请及时修改默认密码"
echo
echo -e "${BLUE}🔍 查看日志命令:${NC}"
echo "  docker-compose -f docker-compose.nginx.yml logs -f"
echo
echo -e "${YELLOW}📝 注意事项:${NC}"
echo "  1. 请确保域名DNS已正确配置"
echo "  2. 防火墙需开放80端口"
echo "  3. 首次启动可能需要几分钟时间"
echo "  4. 请及时修改默认管理员密码"
echo
