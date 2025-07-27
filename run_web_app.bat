@echo off
cd /d "%~dp0"
start http://localhost:5000
"C:\Program Files\Python312\python.exe" app.py
pause
