@echo off
echo AeroScout 部署脚本
echo.

REM 获取用户输入的API地址
set /p API_URL="请输入后端API地址 (例如: http://47.79.39.147:8000): "

REM 如果用户没有输入，使用默认值
if "%API_URL%"=="" set API_URL=http://47.79.39.147:8000

echo.
echo 使用API地址: %API_URL%
echo.

REM 设置环境变量
set NEXT_PUBLIC_API_URL=%API_URL%

REM 写入.env文件
echo # AeroScout 部署环境变量配置 > .env
echo NEXT_PUBLIC_API_URL=%API_URL% >> .env
echo.

echo 正在部署...
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

echo.
echo 部署完成！
echo 前端地址: http://localhost:3000
echo 后端地址: %API_URL%
echo API文档: %API_URL%/docs
echo.
pause
