@echo off
title Sleep Tracker

echo.
echo  ========================================
echo    Sleep Tracker is starting...
echo  ========================================
echo.

:: Change to the script's directory
cd /d "%~dp0"

:: Start the browser after a short delay (in background)
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

:: Run the Flask app using the virtual environment
".venv\Scripts\python.exe" app.py

:: App has closed - exit automatically (no pause needed since shutdown is intentional)
exit
