@echo off
echo ========================================
echo    AeroScout Backend Quick Start
echo ========================================
echo.

REM Set Redis path
set REDIS_PATH=D:\Redis
set REDIS_CLI=%REDIS_PATH%\redis-cli.exe

REM Quick Redis check
echo Checking Redis status...
"%REDIS_CLI%" ping >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Redis server...
    start "Redis Server" "%REDIS_PATH%\redis-server.exe" --port 6379
    timeout /t 3 /nobreak >nul
)

REM Activate virtual environment
echo Activating Python virtual environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found, please run start_backend_with_redis.bat first
    pause
    exit /b 1
)

REM Start services
echo.
echo Starting backend services...

REM Start Uvicorn
start "AeroScout API Server" cmd /c "title AeroScout API Server && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM Start Celery
timeout /t 2 /nobreak >nul
start "AeroScout Celery Worker" cmd /c "title AeroScout Celery Worker && python -m celery -A app.celery_worker worker --loglevel=info --pool=solo"

echo.
echo Backend services started successfully!
echo.
echo API Server: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press any key to exit...
pause >nul
