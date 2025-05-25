@echo off
chcp 65001 >nul
title AeroScout 快速部署工具

:menu
cls
echo ╔══════════════════════════════════════╗
echo ║        AeroScout 部署管理工具        ║
echo ║      服务器: 47.79.39.147           ║
echo ╚══════════════════════════════════════╝
echo.
echo 1. 🚀 一键部署到生产环境
echo 2. 📊 查看服务状态
echo 3. 📋 查看服务日志
echo 4. 🔄 重启所有服务
echo 5. 🛑 停止所有服务
echo 6. 🧹 清理系统
echo 7. 💾 备份数据
echo 8. 📖 查看部署文档
echo 9. ❌ 退出
echo.
set /p choice=请选择操作 (1-9): 

if "%choice%"=="1" goto deploy
if "%choice%"=="2" goto status
if "%choice%"=="3" goto logs
if "%choice%"=="4" goto restart
if "%choice%"=="5" goto stop
if "%choice%"=="6" goto cleanup
if "%choice%"=="7" goto backup
if "%choice%"=="8" goto docs
if "%choice%"=="9" goto exit
echo 无效选择，请重新输入
pause
goto menu

:deploy
echo 🚀 开始部署...
call deploy.bat
pause
goto menu

:status
echo 📊 服务状态:
docker-compose -f docker-compose.prod.yml ps
echo.
echo 🔍 端口监听状态:
netstat -an | findstr ":3000 :8000 :6379"
pause
goto menu

:logs
echo 选择要查看的服务日志:
echo 1. 前端 (frontend)
echo 2. 后端 (backend)  
echo 3. Celery (celery)
echo 4. Redis (redis)
echo 5. 所有服务
set /p log_choice=请选择 (1-5): 

if "%log_choice%"=="1" docker-compose -f docker-compose.prod.yml logs frontend
if "%log_choice%"=="2" docker-compose -f docker-compose.prod.yml logs backend
if "%log_choice%"=="3" docker-compose -f docker-compose.prod.yml logs celery
if "%log_choice%"=="4" docker-compose -f docker-compose.prod.yml logs redis
if "%log_choice%"=="5" docker-compose -f docker-compose.prod.yml logs
pause
goto menu

:restart
echo 🔄 重启所有服务...
docker-compose -f docker-compose.prod.yml restart
echo ✅ 服务重启完成
pause
goto menu

:stop
echo 🛑 停止所有服务...
docker-compose -f docker-compose.prod.yml down
echo ✅ 服务已停止
pause
goto menu

:cleanup
echo 🧹 清理系统...
docker system prune -f
docker volume prune -f
echo ✅ 清理完成
pause
goto menu

:backup
echo 💾 备份数据...
if not exist backups mkdir backups
set backup_name=backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%
docker cp aeroscout-backend:/app/aeroscout.db backups\aeroscout_%backup_name%.db
copy .env.production backups\env_%backup_name%.txt
echo ✅ 备份完成: backups\aeroscout_%backup_name%.db
pause
goto menu

:docs
echo 📖 打开部署文档...
start DEPLOYMENT.md
pause
goto menu

:exit
echo 👋 再见！
exit /b 0
