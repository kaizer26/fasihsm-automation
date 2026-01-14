@echo off
title FASIH-SM Server
color 0A

echo =========================================
echo   FASIH-SM Local Network Server
echo =========================================
echo.

REM Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP:~1%

echo [INFO] Your IP Address: %IP%
echo.
echo [INFO] Other devices can access:
echo        Frontend: http://%IP%:5173
echo        Backend:  http://%IP%:5000
echo.
echo =========================================

REM Check if virtual environment exists
if exist "backend\venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call backend\venv\Scripts\activate.bat
)

REM Start Backend in minimized window
echo [INFO] Starting Backend Server...
start /min "FASIH-SM Backend" cmd /c "cd /d %~dp0backend && python app.py"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start Frontend in this window
echo [INFO] Starting Frontend Server...
echo [INFO] Access via http://%IP%:5173
echo.
cd /d %~dp0frontend
npm run dev -- --host

REM If npm finishes (Ctrl+C), kill the background backend
echo.
echo [INFO] Stopping Backend Server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo [OK] Done.
pause
