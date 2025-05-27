@echo off
echo AeroScout后端一键启动脚本
echo ============================
echo.

REM 检查虚拟环境
if exist .venv\Scripts\activate.bat (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo 错误: 未找到虚拟环境 (.venv)
    echo 请先创建并设置虚拟环境
    pause
    exit /b 1
)

REM 检查依赖项
echo 检查依赖项...
python -c "import databases" 2>nul
if %errorlevel% neq 0 (
    echo 安装databases模块...
    pip install databases
)

python -c "import aiosqlite" 2>nul
if %errorlevel% neq 0 (
    echo 安装aiosqlite模块...
    pip install aiosqlite
)



python -c "import celery" 2>nul
if %errorlevel% neq 0 (
    echo 安装celery模块...
    pip install "celery[redis]"
)

REM 检查Redis
echo 检查Redis服务器...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: Redis服务器可能未运行
    echo Celery任务队列可能无法正常工作
    echo 请确保Redis服务器已安装并运行
    echo.
    set /p choice=是否继续? (y/n):
    if /i "%choice%" neq "y" (
        echo 已取消启动
        pause
        exit /b 1
    )
)

REM 检查数据库
echo 检查数据库...
python fix_locations_table.py

REM Trip.com cookies will be fetched automatically by the backend when needed

REM 启动Uvicorn服务器
echo.
echo 启动Uvicorn服务器...
start "AeroScout Uvicorn" cmd /c "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM 启动Celery工作进程 (单线程模式)
echo.
echo 启动Celery工作进程 (单线程模式)...
start "AeroScout Celery" cmd /c "python -m celery -A app.celery_worker worker --loglevel=info --pool=solo"

echo.
echo AeroScout后端服务已启动
echo Uvicorn服务器: http://127.0.0.1:8000
echo Celery工作进程: 单线程模式
echo.
echo 注意: 在Windows环境下，Celery使用单线程模式以避免权限问题
echo 如果POI搜索功能仍然返回503错误，请等待几分钟让Celery完成Trip.com会话数据的获取
echo.
echo 按任意键退出此脚本 (服务将继续在后台运行)
pause
