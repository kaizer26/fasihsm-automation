@echo off
title FASIH-SM Server
color 0A

echo =========================================
echo   FASIH-SM Local Server
echo =========================================
echo.

REM Check Prerequisites
echo [1/4] Checking prerequisites...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python tidak ditemukan! Silakan install Python 3.10+
    echo         Download: https://www.python.org/downloads/windows/
    echo         PENTING: Centang "Add Python to PATH" saat install!
    pause
    exit /b 1
)

node -v >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js tidak ditemukan! Silakan install Node.js terbaru.
    echo         Download: https://nodejs.org/
    pause
    exit /b 1
)

REM Check Node.js version (must be 20+)
for /f "tokens=1 delims=v." %%a in ('node -v') do set NODE_MAJOR=%%a
if %NODE_MAJOR% LSS 20 (
    echo [ERROR] Node.js versi terlalu lama!
    echo.
    echo         Versi Anda: 
    node -v
    echo         Versi minimum: v20.19.0 atau v22.12.0
    echo.
    echo         Silakan update Node.js:
    echo         Download: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo [OK] Prerequisites found.
echo.

REM Setup Backend if needed
echo [2/4] Checking Backend...
cd /d %~dp0backend
if not exist "venv" (
    echo [INFO] Virtual environment tidak ditemukan. Membuat venv...
    python -m venv venv
    if %errorLevel% neq 0 (
        echo [ERROR] Gagal membuat virtual environment!
        pause
        exit /b 1
    )
)

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment rusak. Hapus folder backend\venv dan jalankan ulang.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
pip show flask >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Installing backend dependencies...
    pip install -r requirements.txt
    if %errorLevel% neq 0 (
        echo [ERROR] Gagal install dependencies backend!
        pause
        exit /b 1
    )
)
echo [OK] Backend ready.
echo.

REM Setup Frontend if needed
echo [3/4] Checking Frontend...
cd /d %~dp0frontend
if not exist "node_modules" (
    echo [INFO] node_modules tidak ditemukan. Menginstall dependencies...
    echo [INFO] Ini mungkin memakan waktu beberapa menit...
    call npm install
    if %errorLevel% neq 0 (
        echo [ERROR] Gagal install dependencies frontend!
        echo [HINT] Pastikan koneksi internet aktif dan npm bisa diakses.
        pause
        exit /b 1
    )
)
echo [OK] Frontend ready.
echo.

REM Launch Servers
echo [4/4] Launching Servers...
cd /d %~dp0
echo.
echo =========================================
echo   SERVERS STARTING
echo   Backend:  http://localhost:5005
echo   Frontend: http://localhost:5173
echo =========================================
echo.

REM Start Backend in minimized window
echo [INFO] Starting Backend Server...
start /min "FASIH-SM Backend" cmd /c "cd /d %~dp0backend && call venv\Scripts\activate.bat && python app.py"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start Frontend in this window
echo [INFO] Starting Frontend Server...
echo [INFO] Buka http://localhost:5173 di browser Anda.
echo [INFO] Tekan Ctrl+C untuk berhenti.
echo.
cd /d %~dp0frontend
call npm run dev

REM Check if npm run dev failed
if %errorLevel% neq 0 (
    echo.
    echo =========================================
    echo   [ERROR] Frontend gagal dijalankan!
    echo =========================================
    echo.
    echo Kemungkinan penyebab:
    echo 1. Port 5173 sudah dipakai aplikasi lain
    echo 2. Ada error di kode TypeScript/React
    echo 3. Dependencies tidak lengkap
    echo.
    echo Coba jalankan manual untuk melihat error:
    echo   cd frontend
    echo   npm run dev
    echo.
    pause
    goto cleanup
)

REM If npm finishes (Ctrl+C), kill the background backend
:cleanup
echo.
echo [INFO] Stopping Backend Server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5005 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo [OK] Done.
pause
