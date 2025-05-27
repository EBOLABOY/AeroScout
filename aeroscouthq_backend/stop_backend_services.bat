@echo off
echo ========================================
echo    AeroScout Backend Stop Script
echo ========================================
echo.

echo Stopping AeroScout backend services...
echo.

REM Stop Uvicorn process
echo [1/4] Stopping Uvicorn API server...
taskkill /f /fi "WINDOWTITLE eq AeroScout API Server*" >nul 2>&1
if %errorlevel% equ 0 (
    echo OK: Uvicorn API server stopped
) else (
    echo WARNING: No running Uvicorn API server found
)

REM Stop Celery process
echo.
echo [2/4] Stopping Celery worker...
taskkill /f /fi "WINDOWTITLE eq AeroScout Celery Worker*" >nul 2>&1
if %errorlevel% equ 0 (
    echo OK: Celery worker stopped
) else (
    echo WARNING: No running Celery worker found
)

REM Stop Python processes (backup method)
echo.
echo [3/4] Checking and stopping related Python processes...
setlocal enabledelayedexpansion
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find "python.exe"') do (
    set pid=%%i
    set pid=!pid:"=!
    wmic process where "processid=!pid!" get commandline /format:list | find "uvicorn" >nul 2>&1
    if !errorlevel! equ 0 (
        echo    Stopping Python process PID: !pid!
        taskkill /f /pid !pid! >nul 2>&1
    )
    wmic process where "processid=!pid!" get commandline /format:list | find "celery" >nul 2>&1
    if !errorlevel! equ 0 (
        echo    Stopping Python process PID: !pid!
        taskkill /f /pid !pid! >nul 2>&1
    )
)

REM Ask whether to stop Redis
echo.
echo [4/4] Redis server management...
set /p stop_redis=Stop Redis server? (y/n):
if /i "%stop_redis%"=="y" (
    echo Stopping Redis server...
    taskkill /f /im redis-server.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo OK: Redis server stopped
    ) else (
        echo WARNING: No running Redis server found
    )
) else (
    echo INFO: Redis server remains running
)

echo.
echo ========================================
echo        Service Stop Operation Complete!
echo ========================================
echo.
echo Operation Summary:
echo    - Uvicorn API server: Stopped
echo    - Celery worker: Stopped
echo    - Related Python processes: Cleaned
if /i "%stop_redis%"=="y" (
    echo    - Redis server: Stopped
) else (
    echo    - Redis server: Still running
)
echo.
echo Tips:
echo    - To restart, run start_backend_with_redis.bat
echo    - To check process status, use Task Manager
echo.
pause
