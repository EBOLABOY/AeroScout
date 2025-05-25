#!/bin/bash

# AeroScout 生产环境部署脚本
# 服务器IP: 47.79.39.147

set -e  # 遇到错误立即退出

echo "🚀 开始部署 AeroScout 到生产环境..."
echo "服务器IP: 47.79.39.147"
echo "=================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 停止现有容器（如果存在）
echo "🛑 停止现有容器..."
docker-compose -f docker-compose.prod.yml down || true

# 清理旧的镜像（可选）
echo "🧹 清理旧镜像..."
docker system prune -f || true

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose -f docker-compose.prod.yml build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

# 检查后端健康状态
echo "🏥 检查后端健康状态..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ 后端服务启动成功"
        break
    else
        echo "⏳ 等待后端服务启动... ($i/10)"
        sleep 5
    fi
    if [ $i -eq 10 ]; then
        echo "❌ 后端服务启动失败"
        docker-compose -f docker-compose.prod.yml logs backend
        exit 1
    fi
done

# 检查前端健康状态
echo "🏥 检查前端健康状态..."
for i in {1..10}; do
    if curl -f http://localhost:3000 &> /dev/null; then
        echo "✅ 前端服务启动成功"
        break
    else
        echo "⏳ 等待前端服务启动... ($i/10)"
        sleep 5
    fi
    if [ $i -eq 10 ]; then
        echo "❌ 前端服务启动失败"
        docker-compose -f docker-compose.prod.yml logs frontend
        exit 1
    fi
done

echo ""
echo "🎉 部署完成！"
echo "=================================="
echo "📱 前端访问地址: http://47.79.39.147:3000"
echo "🔧 后端API地址: http://47.79.39.147:8000"
echo "📚 API文档地址: http://47.79.39.147:8000/docs"
echo ""
echo "📊 查看服务状态: docker-compose -f docker-compose.prod.yml ps"
echo "📋 查看日志: docker-compose -f docker-compose.prod.yml logs [service_name]"
echo "🛑 停止服务: docker-compose -f docker-compose.prod.yml down"
echo ""
echo "⚠️  重要提醒:"
echo "1. 请确保防火墙已开放 3000 和 8000 端口"
echo "2. 请修改 .env.production 中的 SECRET_KEY"
echo "3. 建议配置 HTTPS 和域名"
echo "4. 定期备份数据库文件"
