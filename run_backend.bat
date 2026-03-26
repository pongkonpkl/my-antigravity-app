@echo off
title Coin PT Backend [API]
echo Clearing existing python processes on port 8001...
PowerShell -Command "Stop-Process -Name python -Force -ErrorAction SilentlyContinue"
timeout /t 2 >nul
echo Starting Backend Server...
python main.py
pause
