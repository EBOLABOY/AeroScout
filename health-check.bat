@echo off
chcp 65001 >nul
echo 🏥 AeroScout 健康检查
echo ========================

echo 检查前端服务...
curl -f http://47.79.39.147:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 前端服务正常
) else (
    echo ❌ 前端服务异常
)

echo 检查后端服务...
curl -f http://47.79.39.147:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 后端服务正常
) else (
    echo ❌ 后端服务异常
)

echo 检查Redis服务...
docker exec aeroscout-redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis服务正常
) else (
    echo ❌ Redis服务异常
)

echo.
echo 📊 容器状态:
docker-compose -f docker-compose.prod.yml ps

echo.
echo 💻 系统资源:
docker stats --no-stream

pause
