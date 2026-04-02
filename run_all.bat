@echo off
setlocal EnableDelayedExpansion
title Telegram Signals MT5 Bot
cd /d %~dp0

set PYTHON=%~dp0venv312\Scripts\python.exe
set UVICORN=%~dp0venv312\Scripts\uvicorn.exe
set REQ=%~dp0requirements.txt
set DASH_PORT=8501
set DASH_HOST=127.0.0.1
set DASH_URL=http://%DASH_HOST%:%DASH_PORT%

if not exist "%PYTHON%" (
    echo venv312 Python not found at %PYTHON%
    pause
    exit /b 1
)

if not exist "%UVICORN%" (
    echo uvicorn.exe not found at %UVICORN%
    pause
    exit /b 1
)

if not exist "%REQ%" (
    echo requirements.txt not found at %REQ%
    pause
    exit /b 1
)

echo ==========================================
echo Installing required packages...
echo ==========================================
"%PYTHON%" -m pip install --upgrade pip
"%PYTHON%" -m pip install -r "%REQ%" --upgrade-strategy only-if-needed

if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Verifying required modules...
echo ==========================================
"%PYTHON%" -c "import aiogram, MetaTrader5, fastapi, uvicorn, jinja2; print('All required packages are available.')"

if errorlevel 1 (
    echo Module verification failed.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Checking required files...
echo ==========================================
if not exist "forwarder.py" (
    echo forwarder.py not found
    pause
    exit /b 1
)
if not exist "telegram_async_bot.py" (
    echo telegram_async_bot.py not found
    pause
    exit /b 1
)
if not exist "dashboard_app\web.py" (
    echo dashboard_app\web.py not found
    pause
    exit /b 1
)
if not exist "dashboard_app\routes.py" (
    echo dashboard_app\routes.py not found
    pause
    exit /b 1
)
if not exist "dashboard_app\services.py" (
    echo dashboard_app\services.py not found
    pause
    exit /b 1
)
if not exist "dashboard_app\templates\dashboard.html" (
    echo dashboard_app\templates\dashboard.html not found
    pause
    exit /b 1
)
if not exist "dashboard_app\static\css\dashboard.css" (
    echo dashboard_app\static\css\dashboard.css not found
    pause
    exit /b 1
)
if not exist "dashboard_app\static\js\dashboard.js" (
    echo dashboard_app\static\js\dashboard.js not found
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Starting services...
echo ==========================================

start "Forwarder" cmd /k "cd /d %~dp0 && %PYTHON% forwarder.py"
timeout /t 2 /nobreak >nul

start "Telegram Async Bot" cmd /k "cd /d %~dp0 && %PYTHON% telegram_async_bot.py"
timeout /t 2 /nobreak >nul

start "Web Server" cmd /k "cd /d %~dp0 && %UVICORN% dashboard_app.web:app --host 0.0.0.0 --port %DASH_PORT%"
timeout /t 2 /nobreak >nul

echo.
echo Waiting for dashboard on %DASH_URL% ...
set DASH_READY=

for /L %%I in (1,1,20) do (
    netstat -ano | findstr /r /c:":%DASH_PORT% .*LISTENING" >nul
    if not errorlevel 1 (
        set DASH_READY=1
        goto :dashboard_ready
    )
    timeout /t 1 /nobreak >nul
)

:dashboard_ready
if defined DASH_READY (
    echo Dashboard is listening on port %DASH_PORT%.
) else (
    echo Dashboard did not start listening on port %DASH_PORT% yet.
    echo Check the "Web Server" window for errors.
)

echo.
echo Local dashboard URLs:
echo http://127.0.0.1:%DASH_PORT%
echo http://localhost:%DASH_PORT%
echo http://YOUR-LAN-IP:%DASH_PORT%
echo.

if exist "cloudflared.exe" (
    if defined DASH_READY (
        echo Starting Cloudflare tunnel...
        start "Cloudflare Tunnel" cmd /k "cd /d %~dp0 && cloudflared.exe tunnel --url http://localhost:%DASH_PORT%"
        echo Public URL will appear in the Cloudflare Tunnel window.
    ) else (
        echo Skipping Cloudflare tunnel because dashboard is not ready.
    )
) else (
    if exist "ngrok.exe" (
        if defined DASH_READY (
            echo Starting ngrok tunnel...
            start "ngrok Tunnel" cmd /k "cd /d %~dp0 && ngrok.exe http %DASH_PORT%"
            echo Public URL will appear in the ngrok window.
        ) else (
            echo Skipping ngrok tunnel because dashboard is not ready.
        )
    ) else (
        echo No cloudflared.exe or ngrok.exe found in project root.
        echo External public URL not started automatically.
    )
)

echo.
echo Main runner is interactive and not auto-started:
echo %PYTHON% main.py
echo.

if defined DASH_READY (
    start "" "%DASH_URL%"
) else (
    echo Browser not opened because dashboard is not ready.
)

echo All services start commands have been issued.
pause
