@echo off
echo AeroScout后端启动脚本 (支持Redis搜索会话存储)
echo ================================================
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

REM 检查Redis依赖
echo 检查Redis依赖...
python -c "import redis" 2>nul
if %errorlevel% neq 0 (
    echo 安装Redis模块...
    pip install redis>=4.5.0
)

REM 检查Redis服务器
echo 检查Redis服务器状态...
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0); r.ping(); print('Redis服务器运行正常')" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Redis服务器未运行或无法连接
    echo.
    echo 请确保Redis服务器正在运行:
    echo 1. 如果已安装Redis，请启动Redis服务器
    echo 2. 如果未安装Redis，可以使用Docker运行:
    echo    docker run -d -p 6379:6379 redis:latest
    echo 3. 或者下载并安装Redis: https://redis.io/download
    echo.
    echo 注意: 如果Redis不可用，系统将自动回退到内存存储
    echo.
    pause
)

REM 测试Redis搜索会话存储
echo.
echo 测试Redis搜索会话存储功能...
python test_redis_sessions.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Redis搜索会话存储测试失败，但服务仍将启动
    echo 系统将使用内存存储作为备选方案
    echo.
)

REM 检查数据库
echo.
echo 检查数据库...
python fix_locations_table.py

REM Trip.com cookies will be fetched automatically by the backend when needed

REM 启动Uvicorn服务器
echo.
echo 启动Uvicorn服务器...
start "AeroScout Uvicorn" cmd /c "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM 启动Celery工作进程
echo.
echo 启动Celery工作进程...
start "AeroScout Celery" cmd /c "python -m celery -A app.celery_worker worker --loglevel=info --pool=solo"

echo.
echo ✅ AeroScout后端服务已启动
echo.
echo 🌐 Uvicorn服务器: http://127.0.0.1:8000
echo 📋 API文档: http://127.0.0.1:8000/docs
echo 🔄 Celery工作进程: 单线程模式
echo 💾 搜索会话存储: Redis (如可用) 或 内存存储
echo.
echo 🔍 测试Redis搜索会话存储:
echo    GET http://127.0.0.1:8000/api/v2/flights/health
echo    GET http://127.0.0.1:8000/api/v2/flights/sessions
echo.
echo 注意:
echo - Redis搜索会话存储支持多用户并发和会话持久化
echo - 如果Redis不可用，系统会自动回退到内存存储
echo - 搜索会话默认TTL为1小时 (可在.env中配置REDIS_SESSION_TTL)
echo.
echo 按任意键退出此脚本 (服务将继续在后台运行)
pause
