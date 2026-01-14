@echo off
title FASIH-SM Firewall Setup
color 0E

echo =========================================
echo   FASIH-SM Firewall Setup
echo =========================================
echo.
echo Menambahkan rule firewall untuk port 5000 dan 5173...
echo.

REM Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Script ini harus dijalankan sebagai Administrator!
    echo.
    echo Cara:
    echo 1. Klik kanan pada file ini
    echo 2. Pilih "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Add firewall rules
echo [INFO] Adding Flask Backend rule (port 5000)...
netsh advfirewall firewall add rule name="FASIH-SM Flask Backend" dir=in action=allow protocol=tcp localport=5000 >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Backend rule added successfully
) else (
    echo [SKIP] Backend rule already exists
)

echo [INFO] Adding Vite Frontend rule (port 5173)...
netsh advfirewall firewall add rule name="FASIH-SM Vite Frontend" dir=in action=allow protocol=tcp localport=5173 >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Frontend rule added successfully
) else (
    echo [SKIP] Frontend rule already exists
)

echo.
echo =========================================
echo   Setup Complete!
echo =========================================
echo.
echo Sekarang device lain di jaringan yang sama
echo dapat mengakses FASIH-SM di PC ini.
echo.
pause
