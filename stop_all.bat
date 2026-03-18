@echo off
title Stop Telegram Signals MT5 Bot

echo Stopping project services...

taskkill /F /FI "WINDOWTITLE eq Forwarder*" /T
taskkill /F /FI "WINDOWTITLE eq Telegram Async Bot*" /T
taskkill /F /FI "WINDOWTITLE eq Web Server*" /T

echo Done.
pause
