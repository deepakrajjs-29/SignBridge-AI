@echo off
set CORS_ORIGINS=http://localhost:3000,http://localhost:5173
rem MODEL_VERSION is only a fallback: models/registry.json active_model wins.
set MODEL_VERSION=SBAI-MDL-ISL-4.0.0
cd /d D:\Projects\SignBridge\backend
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
