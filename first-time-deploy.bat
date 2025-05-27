@echo off
echo ========================================
echo    AeroScout 首次部署脚本
echo ========================================
echo.

REM 获取用户输入的API地址
set /p API_URL="请输入后端API地址 (默认: http://localhost:8000): "
if "%API_URL%"=="" set API_URL=http://localhost:8000

echo.
echo 配置信息:
echo   API地址: %API_URL%
echo   默认管理员: 1242772513@qq.com
echo   默认密码: 1242772513
echo.

set /p CONFIRM="确认开始部署? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo 部署已取消
    pause
    exit /b 1
)

echo.
echo 🚀 开始首次部署...
echo.

REM 设置环境变量
set NEXT_PUBLIC_API_URL=%API_URL%

REM 写入.env文件
echo # AeroScout 生产环境配置 > .env
echo NEXT_PUBLIC_API_URL=%API_URL% >> .env
echo.

echo ✅ 环境变量配置完成
echo.

REM 停止现有服务
echo 🛑 停止现有服务...
docker-compose -f docker-compose.prod.yml down

REM 清理旧镜像（可选）
echo 🧹 清理旧镜像...
docker system prune -f

REM 构建并启动服务
echo 🔨 构建并启动服务...
docker-compose -f docker-compose.prod.yml up -d --build

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 30 /nobreak > nul

REM 检查服务状态
echo 📊 检查服务状态...
docker-compose -f docker-compose.prod.yml ps

echo.
echo ========================================
echo    🎉 首次部署完成!
echo ========================================
echo.
echo 📋 部署信息:
echo   前端地址: http://localhost:3000
echo   后端地址: %API_URL%
echo   API文档: %API_URL%/docs
echo.
echo 👤 默认管理员账户:
echo   邮箱: 1242772513@qq.com
echo   密码: 1242772513
echo   权限: 管理员
echo.
echo 📝 注意事项:
echo   1. 首次启动可能需要几分钟时间
echo   2. 数据库会自动初始化
echo   3. 默认管理员账户会自动创建
echo   4. 请及时修改默认密码
echo.
echo 🔍 查看日志命令:
echo   docker-compose -f docker-compose.prod.yml logs -f
echo.

pause
