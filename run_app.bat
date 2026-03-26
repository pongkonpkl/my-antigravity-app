@echo off
echo Starting FastAPI Backend (Port 8001)...
start cmd /k "uvicorn main:app --port 8001"
timeout /t 3
echo Starting God-Tier Native React Frontend (Vite)...
start cmd /k "npm run dev -- --open"

