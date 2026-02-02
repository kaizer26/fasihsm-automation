@echo off
title FASIH-SM Server
color 0A

echo =========================================
echo   FASIH-SM Local Server
echo =========================================
echo.
echo [INFO] Access via:
echo        Frontend: http://localhost:5173
echo        Backend:  http://localhost:5005
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
echo [INFO] Access via http://localhost:5173
echo.
cd /d %~dp0frontend
npm run dev

REM If npm finishes (Ctrl+C), kill the background backend
echo.
echo [INFO] Stopping Backend Server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5005 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo [OK] Done.
pause
