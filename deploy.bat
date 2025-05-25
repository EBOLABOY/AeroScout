@echo off
chcp 65001 >nul
echo 🚀 开始部署 AeroScout 到生产环境...
echo 服务器IP: 47.79.39.147
echo ==================================

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

REM 停止现有容器（如果存在）
echo 🛑 停止现有容器...
docker-compose -f docker-compose.prod.yml down 2>nul

REM 清理旧的镜像（可选）
echo 🧹 清理旧镜像...
docker system prune -f 2>nul

REM 构建镜像
echo 🔨 构建 Docker 镜像...
docker-compose -f docker-compose.prod.yml build --no-cache
if %errorlevel% neq 0 (
    echo ❌ 镜像构建失败
    pause
    exit /b 1
)

REM 启动服务
echo 🚀 启动服务...
docker-compose -f docker-compose.prod.yml up -d
if %errorlevel% neq 0 (
    echo ❌ 服务启动失败
    pause
    exit /b 1
)

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 30 /nobreak >nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose -f docker-compose.prod.yml ps

echo.
echo 🎉 部署完成！
echo ==================================
echo 📱 前端访问地址: http://47.79.39.147:3000
echo 🔧 后端API地址: http://47.79.39.147:8000
echo 📚 API文档地址: http://47.79.39.147:8000/docs
echo.
echo 📊 查看服务状态: docker-compose -f docker-compose.prod.yml ps
echo 📋 查看日志: docker-compose -f docker-compose.prod.yml logs [service_name]
echo 🛑 停止服务: docker-compose -f docker-compose.prod.yml down
echo.
echo ⚠️  重要提醒:
echo 1. 请确保防火墙已开放 3000 和 8000 端口
echo 2. 请修改 .env.production 中的 SECRET_KEY
echo 3. 建议配置 HTTPS 和域名
echo 4. 定期备份数据库文件
echo.
pause
