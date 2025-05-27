@echo off
echo ========================================
echo    AeroScout Backend Startup Script
echo ========================================
echo.

REM Set Redis path
set REDIS_PATH=D:\Redis
set REDIS_SERVER=%REDIS_PATH%\redis-server.exe
set REDIS_CLI=%REDIS_PATH%\redis-cli.exe

REM Check if Redis exists
echo [1/7] Checking Redis installation...
if not exist "%REDIS_SERVER%" (
    echo ERROR: Redis server not found
    echo    Expected path: %REDIS_SERVER%
    echo    Please ensure Redis is installed in D:\Redis directory
    echo.
    pause
    exit /b 1
)
echo OK: Redis server found: %REDIS_SERVER%

REM Check if Redis is already running
echo.
echo [2/7] Checking Redis service status...
"%REDIS_CLI%" ping >nul 2>&1
if %errorlevel% equ 0 (
    echo OK: Redis server is already running
) else (
    echo Starting Redis server...
    start "Redis Server" "%REDIS_SERVER%" --port 6379

    REM Wait for Redis to start
    echo    Waiting for Redis to start...
    timeout /t 3 /nobreak >nul

    REM Verify Redis started successfully
    "%REDIS_CLI%" ping >nul 2>&1
    if %errorlevel% equ 0 (
        echo OK: Redis server started successfully
    ) else (
        echo ERROR: Redis server failed to start
        echo    Please check Redis configuration or start Redis manually
        pause
        exit /b 1
    )
)

REM Check virtual environment
echo.
echo [3/7] Checking Python virtual environment...
if exist .venv\Scripts\activate.bat (
    echo OK: Virtual environment found, activating...
    call .venv\Scripts\activate.bat
    echo    Virtual environment activated
) else (
    echo ERROR: Virtual environment not found (.venv)
    echo    Please create virtual environment first:
    echo    python -m venv .venv
    echo    .venv\Scripts\activate.bat
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check key dependencies
echo.
echo [4/7] Checking Python dependencies...

echo    Checking FastAPI...
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo    Installing FastAPI...
    pip install fastapi
)

echo    Checking Uvicorn...
python -c "import uvicorn" 2>nul
if %errorlevel% neq 0 (
    echo    Installing Uvicorn...
    pip install "uvicorn[standard]"
)

echo    Checking Celery...
python -c "import celery" 2>nul
if %errorlevel% neq 0 (
    echo    Installing Celery...
    pip install "celery[redis]"
)

echo    Checking Redis Python client...
python -c "import redis" 2>nul
if %errorlevel% neq 0 (
    echo    Installing Redis Python client...
    pip install "redis>=4.5.0"
)

echo    Checking database dependencies...
python -c "import databases, aiosqlite" 2>nul
if %errorlevel% neq 0 (
    echo    Installing database dependencies...
    pip install databases aiosqlite
)

echo OK: Dependencies check completed

REM Test Redis connection
echo.
echo [5/7] Testing Redis connection...
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0); r.ping(); print('OK: Redis connection test successful')" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Redis connection test failed
    echo    Please check Redis server status
    pause
    exit /b 1
)

REM Check database
echo.
echo [6/7] Checking database...
if exist fix_locations_table.py (
    python fix_locations_table.py
)
echo OK: Database check completed

REM Start backend services
echo.
echo [7/7] Starting backend services...
echo.

REM Start Uvicorn server
echo Starting Uvicorn API server...
start "AeroScout API Server" cmd /c "title AeroScout API Server && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM Wait for Uvicorn to start
timeout /t 2 /nobreak >nul

REM Start Celery worker
echo Starting Celery worker...
start "AeroScout Celery Worker" cmd /c "title AeroScout Celery Worker && python -m celery -A app.celery_worker worker --loglevel=info --pool=solo"

echo.
echo ========================================
echo     AeroScout Backend Started Successfully!
echo ========================================
echo.
echo Service Status:
echo    API Server: http://127.0.0.1:8000
echo    API Docs: http://127.0.0.1:8000/docs
echo    Celery Worker: Running (solo mode)
echo    Redis Server: Running (port 6379)
echo.
echo Management Commands:
echo    Redis CLI: %REDIS_CLI%
echo    Stop Redis: taskkill /f /im redis-server.exe
echo.
echo Test Endpoints:
echo    Health Check: GET http://127.0.0.1:8000/health
echo    Redis Sessions: GET http://127.0.0.1:8000/api/v2/flights/health
echo.
echo Notes:
echo    - Celery uses solo mode on Windows
echo    - Redis is used for search sessions and Celery task queue
echo    - All services run in background
echo    - Closing this window will not stop services
echo.
echo Press any key to exit this script...
pause >nul
