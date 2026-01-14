@echo off
title FASIH-SM - Auto Update Repository
color 0B

echo ============================================================
echo      FASIH-SM AUTOMATION TOOL - GIT UPDATE
echo ============================================================
echo.

REM 1. Check if Git is initialized
if not exist ".git" (
    echo [ERROR] Git belum diinisialisasi di folder ini.
    echo Silakan ikuti instruksi di README.md untuk pertama kali upload.
    pause
    exit /b 1
)

REM 2. Get Commit Message
set /p commit_msg="Masukkan pesan update (commit message): "
if "%commit_msg%"=="" (
    set commit_msg="Update - %date% %time%"
)

echo.
echo [1/3] Menambahkan perubahan...
git add .

echo [2/3] Membuat commit...
git commit -m "%commit_msg%"

echo [3/3] Melakukan push ke GitHub...
git push origin main
if %errorLevel% neq 0 (
    echo.
    echo [WARNING] Gagal push ke branch 'main'. Mencoba branch 'master'...
    git push origin master
)

echo.
echo ============================================================
echo   UPDATE SELESAI!
echo ============================================================
echo.
pause
