#!/bin/bash

# AeroScout 服务器完全清理和重新部署脚本
# ============================================

set -e  # 遇到错误立即退出

echo "🧹 AeroScout 服务器完全清理和重新部署"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 确认操作
echo "⚠️  警告：此脚本将："
echo "   - 停止并删除所有Docker容器"
echo "   - 删除所有Docker镜像"
echo "   - 删除所有Docker网络"
echo "   - 删除所有Docker数据卷"
echo "   - 清理Docker系统缓存"
echo "   - 重新部署AeroScout项目"
echo ""
read -p "确认继续？(y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "操作已取消"
    exit 0
fi

echo ""
log_info "开始清理过程..."

# 1. 停止所有运行中的容器
log_info "停止所有运行中的Docker容器..."
if [ "$(docker ps -q)" ]; then
    docker stop $(docker ps -q)
    log_success "所有容器已停止"
else
    log_info "没有运行中的容器"
fi

# 2. 删除所有容器
log_info "删除所有Docker容器..."
if [ "$(docker ps -aq)" ]; then
    docker rm $(docker ps -aq)
    log_success "所有容器已删除"
else
    log_info "没有容器需要删除"
fi

# 3. 删除所有镜像
log_info "删除所有Docker镜像..."
if [ "$(docker images -q)" ]; then
    docker rmi $(docker images -q) -f
    log_success "所有镜像已删除"
else
    log_info "没有镜像需要删除"
fi

# 4. 删除所有网络（保留默认网络）
log_info "删除所有自定义Docker网络..."
NETWORKS=$(docker network ls --filter type=custom -q)
if [ "$NETWORKS" ]; then
    docker network rm $NETWORKS
    log_success "所有自定义网络已删除"
else
    log_info "没有自定义网络需要删除"
fi

# 5. 删除所有数据卷
log_info "删除所有Docker数据卷..."
if [ "$(docker volume ls -q)" ]; then
    docker volume rm $(docker volume ls -q) -f
    log_success "所有数据卷已删除"
else
    log_info "没有数据卷需要删除"
fi

# 6. 清理Docker系统
log_info "清理Docker系统缓存..."
docker system prune -af --volumes
log_success "Docker系统清理完成"

# 7. 检查Docker状态
log_info "检查Docker清理结果..."
echo "容器数量: $(docker ps -aq | wc -l)"
echo "镜像数量: $(docker images -q | wc -l)"
echo "网络数量: $(docker network ls --filter type=custom -q | wc -l)"
echo "数据卷数量: $(docker volume ls -q | wc -l)"

echo ""
log_success "Docker环境清理完成！"

# 8. 检查是否已有AeroScout项目
if [ -d "AeroScout" ]; then
    log_warning "发现已存在的AeroScout目录"
    read -p "是否删除并重新克隆？(y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf AeroScout
        log_success "旧项目目录已删除"
    else
        log_info "使用现有项目目录"
        cd AeroScout
        git pull origin main
        log_success "项目代码已更新"
    fi
else
    # 9. 克隆AeroScout项目
    log_info "克隆AeroScout项目..."
    git clone https://github.com/EBOLABOY/AeroScout.git
    log_success "项目克隆完成"
    cd AeroScout
fi

# 10. 配置环境变量
log_info "配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    log_warning "已创建.env文件，请编辑配置："
    echo ""
    echo "需要配置的关键变量："
    echo "SECRET_KEY=AS2024_Kx9#mP7\$vQ2&nR8@wE5!tY3^uI6*oL1+sD4%fG9~hJ0"
    echo "NEXT_PUBLIC_API_URL=https://AeroScout.izlx.de/api"
    echo ""
    read -p "是否现在编辑.env文件？(y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano .env
    fi
else
    log_info ".env文件已存在"
fi

# 11. 检查必要的配置文件
log_info "检查部署配置文件..."
required_files=(
    "docker-compose.production.yml"
    "nginx.production.conf"
    "aeroscout-frontend/Dockerfile"
    "aeroscouthq_backend/Dockerfile"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        log_success "✓ $file"
    else
        log_error "✗ $file 缺失"
        exit 1
    fi
done

# 12. 开始部署
echo ""
log_info "开始部署AeroScout..."
echo "使用配置文件: docker-compose.production.yml"
echo ""

# 构建并启动服务
docker-compose -f docker-compose.production.yml up -d --build

echo ""
log_info "等待服务启动..."
sleep 30

# 13. 检查部署状态
log_info "检查服务状态..."
docker-compose -f docker-compose.production.yml ps

echo ""
log_info "检查服务健康状态..."

# 检查后端健康
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    log_success "✓ 后端服务正常"
else
    log_warning "⚠ 后端服务可能还在启动中"
fi

# 检查前端
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    log_success "✓ 前端服务正常"
else
    log_warning "⚠ 前端服务可能还在启动中"
fi

# 检查Redis
if docker exec aeroscout-redis redis-cli ping >/dev/null 2>&1; then
    log_success "✓ Redis服务正常"
else
    log_warning "⚠ Redis服务异常"
fi

echo ""
log_success "🎉 AeroScout部署完成！"
echo ""
echo "📊 部署信息："
echo "   - 前端地址: http://localhost:3000"
echo "   - 后端API: http://localhost:8000"
echo "   - API文档: http://localhost:8000/docs"
echo "   - 健康检查: http://localhost:8000/health"
echo ""
echo "🔑 默认管理员账户："
echo "   - 邮箱: 1242772513@qq.com"
echo "   - 密码: 1242772513"
echo ""
echo "📋 管理命令："
echo "   - 查看日志: docker-compose -f docker-compose.production.yml logs -f"
echo "   - 重启服务: docker-compose -f docker-compose.production.yml restart"
echo "   - 停止服务: docker-compose -f docker-compose.production.yml down"
echo ""
echo "⚠️  重要提醒："
echo "   1. 请及时修改默认管理员密码"
echo "   2. 确保防火墙开放80和443端口"
echo "   3. 配置域名解析到服务器IP"
echo "   4. 如需SSL，请配置Certbot证书"
echo ""

log_success "部署脚本执行完成！"
