@echo off
title Stop FASIH-SM Servers
color 0C

echo =========================================
echo   Stopping FASIH-SM Servers
echo =========================================
echo.

echo [INFO] Stopping processes on port 5000 (Backend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo [INFO] Stopping processes on port 5173 (Frontend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo [OK] All FASIH-SM servers stopped.
echo.
pause
