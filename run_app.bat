@echo off
title StorePilot AI - Startup
cd /d "C:\Users\master\WorkBuddy AI\rea逆向的特定功能\mvp-agent-os"

echo ========================================
echo   StorePilot AI One-Click Launcher
echo ========================================
echo.

echo [1/3] Checking Python environment...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python ready
echo.

echo [2/3] Releasing port 8000...
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul
echo [OK] Port 8000 ready
echo.

echo [3/3] Starting API server...
start "StorePilot AI Server" cmd /c "python -m uvicorn app:app --host 0.0.0.0 --port 8000 --log-level warning"
timeout /t 4 /nobreak >nul
echo [OK] Server started on port 8000
echo.

echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000/
echo [OK] Browser opened
echo.

echo ========================================
echo   System Ready!
echo   Dashboard: http://localhost:8000/
echo   API Docs:  http://localhost:8000/docs
echo   Payment:   国泰世华银行 (013) 李国荣
echo   Account:   117-50-605328-0
echo   Pricing:   NT$ 1,568/月  |  $49 USD/月
echo ========================================
echo.
echo Press any key to close this window...
pause >nul
