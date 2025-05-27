@echo off
echo AeroScout Celery工作进程启动脚本 (单线程模式)
echo ================================================

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

REM 启动Celery工作进程 (单线程模式)
echo.
echo 启动Celery工作进程 (单线程模式)...
echo 这将在当前窗口运行Celery，按Ctrl+C停止
echo.
python -m celery -A app.celery_worker worker --loglevel=info --pool=solo

echo.
echo Celery工作进程已停止
pause
