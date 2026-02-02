@echo off
title FASIH-SM - One-Click Setup & Start
color 0B

echo ============================================================
echo      FASIH-SM AUTOMATION TOOL - SETUP & START
echo ============================================================
echo.

REM 1. Check Prerequisites
echo [1/4] Checking prerequisites...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python tidak ditemukan! Silakan install Python 3.10+
    pause
    exit /b 1
)

node -v >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js tidak ditemukan! Silakan install Node.js terbaru.
    pause
    exit /b 1
)
echo [OK] Prerequisites found.
echo.

REM 2. Setup Backend
echo [2/4] Setting up Backend...
cd /d %~dp0backend
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

echo [INFO] Installing/Updating backend dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo [OK] Backend ready.
echo.

REM 3. Setup Frontend
echo [3/4] Setting up Frontend...
cd /d %~dp0frontend
if not exist "node_modules" (
    echo [INFO] Installing frontend dependencies (this may take a while)...
    call npm install
)
echo [OK] Frontend ready.
echo.

REM 4. Launch Servers
echo [4/4] Launching Servers...
cd /d %~dp0
echo.
echo ============================================================
echo   SETUP SELESAI!
echo   Backend Berjalan di: http://localhost:5005
echo   Frontend Berjalan di: http://localhost:5173
echo ============================================================
echo.

REM Start Backend (Minimized)
start /min "FASIH-SM Backend" cmd /c "cd /d %~dp0backend && call venv\Scripts\activate.bat && python app.py"

REM Start Frontend (In-window)
cd /d %~dp0frontend
echo [INFO] Buka http://localhost:5173 di browser Anda.
echo [INFO] Tekan Ctrl+C di jendela ini untuk berhenti.
echo.
npm run dev

REM Cleanup backend on exit
echo.
echo [INFO] Stopping Backend Server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5005 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo [OK] Done.
pause
