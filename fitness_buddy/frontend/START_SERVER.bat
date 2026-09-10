@echo off
echo.
echo  =========================================
echo   Fitness Buddy - Starting Server...
echo  =========================================
echo.
echo  Server will open at: http://localhost:3000
echo.
echo  Keep this window OPEN while using the app.
echo  Press Ctrl+C to stop the server.
echo.

:: Kill anything already on port 3000
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000 "') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start the server
node "%~dp0server.js"

pause
