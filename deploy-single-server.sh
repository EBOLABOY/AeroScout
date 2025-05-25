#!/bin/bash

# AeroScout 单服务器部署脚本
# 服务器IP: 47.79.39.147
# 前端和后端都部署在同一台服务器上

set -e

echo "🚀 AeroScout 单服务器部署"
echo "服务器: 47.79.39.147"
echo "=========================="

# 检查部署模式
echo "请选择部署模式:"
echo "1. 简单模式 (前端:3000, 后端:8000)"
echo "2. Nginx模式 (统一入口:80)"
read -p "请选择 (1-2): " deploy_mode

case $deploy_mode in
    1)
        echo "🔧 使用简单模式部署..."
        COMPOSE_FILE="docker-compose.prod.yml"
        ;;
    2)
        echo "🔧 使用Nginx模式部署..."
        COMPOSE_FILE="docker-compose.nginx.yml"
        ;;
    *)
        echo "❌ 无效选择，使用默认简单模式"
        COMPOSE_FILE="docker-compose.prod.yml"
        ;;
esac

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker 安装完成，请重新登录后再次运行此脚本"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，正在安装..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose 安装完成"
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    cp .env.production .env
    echo "⚠️  请编辑 .env 文件，修改 SECRET_KEY 等重要配置"
    echo "按回车键继续..."
    read
fi

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose -f $COMPOSE_FILE down || true

# 清理旧镜像
echo "🧹 清理旧镜像..."
docker system prune -f || true

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose -f $COMPOSE_FILE up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f $COMPOSE_FILE ps

# 健康检查
echo "🏥 健康检查..."

if [ "$deploy_mode" = "2" ]; then
    # Nginx模式
    echo "检查Nginx服务..."
    if curl -f http://localhost &> /dev/null; then
        echo "✅ 前端服务正常 (通过Nginx)"
    else
        echo "❌ 前端服务异常"
    fi
    
    if curl -f http://localhost/api/health &> /dev/null; then
        echo "✅ 后端服务正常 (通过Nginx)"
    else
        echo "❌ 后端服务异常"
    fi
else
    # 简单模式
    echo "检查前端服务..."
    if curl -f http://localhost:3000 &> /dev/null; then
        echo "✅ 前端服务正常"
    else
        echo "❌ 前端服务异常"
    fi
    
    echo "检查后端服务..."
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ 后端服务正常"
    else
        echo "❌ 后端服务异常"
    fi
fi

echo ""
echo "🎉 部署完成！"
echo "=========================="

if [ "$deploy_mode" = "2" ]; then
    echo "🌐 访问地址:"
    echo "   前端: http://47.79.39.147"
    echo "   API:  http://47.79.39.147/api"
    echo "   文档: http://47.79.39.147/docs"
else
    echo "🌐 访问地址:"
    echo "   前端: http://47.79.39.147:3000"
    echo "   API:  http://47.79.39.147:8000"
    echo "   文档: http://47.79.39.147:8000/docs"
fi

echo ""
echo "📋 管理命令:"
echo "   查看状态: docker-compose -f $COMPOSE_FILE ps"
echo "   查看日志: docker-compose -f $COMPOSE_FILE logs -f"
echo "   重启服务: docker-compose -f $COMPOSE_FILE restart"
echo "   停止服务: docker-compose -f $COMPOSE_FILE down"
echo ""
echo "⚠️  重要提醒:"
echo "1. 确保防火墙已开放相应端口"
echo "2. 定期备份数据库文件"
echo "3. 监控系统资源使用情况"
