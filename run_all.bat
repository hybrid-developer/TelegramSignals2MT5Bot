@echo off
setlocal
title Telegram Signals MT5 Bot
cd /d %~dp0

set PYTHON=%~dp0venv312\Scripts\python.exe
set REQ=%~dp0requirements.txt

if not exist "%PYTHON%" (
    echo venv312 Python not found at %PYTHON%
    pause
    exit /b 1
)

if not exist "%REQ%" (
    echo requirements.txt not found at %REQ%
    pause
    exit /b 1
)

echo Installing missing packages from requirements.txt...
"%PYTHON%" -m pip install -r "%REQ%" --upgrade-strategy only-if-needed

if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo Starting services...

start "Forwarder" cmd /k "%PYTHON%" forwarder.py
start "Telegram Async Bot" cmd /k "%PYTHON%" telegram_async_bot.py
start "Web Server" cmd /k "%PYTHON%" -m streamlit run dashboard.py --server.headless true --server.port 8501

echo.
echo Main runner is interactive and not auto-started:
echo %PYTHON% main.py
echo.
echo All services started.
pause
